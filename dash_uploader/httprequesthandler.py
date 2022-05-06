import logging
import pathlib
import os
import shutil
import time
import traceback
from typing import Dict, Final

from flask import request
from flask import abort
from dash_uploader.s3 import S3Configuration
from dash_uploader.utils import retry

# try importing boto3 as it is a feature dependency
try:
    import boto3
except ImportError:
    HAS_BOTO = False
else:
    HAS_BOTO = True


logger = logging.getLogger(__name__)

# chunk size should be greater than 5Mb for s3 multipart upload
S3_MIN_CHUNK_SIZE: Final[int] = 5 * 1024 * 1024


def get_chunk_name(uploaded_filename, chunk_number):
    return f"{uploaded_filename}_part_{chunk_number}"


def remove_file(file):
    os.unlink(file)


class RequestData:
    # A helper class that contains data from the request
    # parsed into handier form.

    def __init__(self, request):
        """
        Parameters
        ----------
        request: flask.request
            The Flask request object
        """
        # Available fields: https://github.com/flowjs/flow.js
        self.n_chunks_total = request.form.get("flowTotalChunks", type=int)
        self.total_size = request.form.get("flowTotalSize", type=int)
        self.chunk_size = request.form.get("flowChunkSize", type=int)
        self.chunk_number = request.form.get("flowChunkNumber", default=1, type=int)
        self.filename = request.form.get("flowFilename", default="error", type=str)
        # 'unique' identifier for the file that is being uploaded.
        # Made of the file size and file name (with relative path, if available)
        self.unique_identifier = request.form.get(
            "flowIdentifier", default="error", type=str
        )
        # flowRelativePath is the flowFilename with the directory structure included
        # the path is relative to the chosen folder.
        self.relative_path = request.form.get("flowRelativePath", default="", type=str)
        if not self.relative_path:
            self.relative_path = self.filename

        # Get the chunk data.
        # Type of `chunk_data`: werkzeug.datastructures.FileStorage
        self.chunk_data = request.files["file"]

        self.upload_id = request.form.get("upload_id", default="", type=str)


class BaseHttpRequestHandler:

    UPLOADS: Dict[str, dict] = {}

    remove_file = staticmethod(retry(wait_time=0.35, max_time=15.0)(remove_file))

    def __init__(
        self, server, upload_folder, use_upload_id, s3_config: S3Configuration = None
    ):
        """
        Parameters
        ----------
        server: flask.Flask
            The flask server instance
        upload_folder: str
            The folder to use for uploads
        use_upload_id: bool
            Determines if the uploads are put into
            folders defined by a "upload id" (upload_id).
            If True, uploads will be put into `folder`/<upload_id>/;
            that is, every user (for example with different
            session id) will use their own folder. If False,
            all files from all sessions are uploaded into
            same folder (not recommended).
        s3_config: None or class
            Used for uploading file to a s3 bucket. If provided, `folder` will be used for
            temp folder for chunks during multipart upload

        """
        self.server = server
        self.upload_folder = pathlib.Path(upload_folder)
        self.use_upload_id = use_upload_id

        if not s3_config:
            self.upload_to_s3 = False
        else:
            if not HAS_BOTO:
                raise ValueError(
                    "`s3_config` is provided but boto3 is missing. Please re-install dash_uploader with 's3' feature enabled"
                )
            self.upload_to_s3 = True
            self.s3 = boto3.client(
                "s3",
                region_name=s3_config.location.region_name,
                use_ssl=s3_config.location.use_ssl,
                endpoint_url=s3_config.location.endpoint_url,
                aws_access_key_id=s3_config.credentials.aws_access_key_id,
                aws_secret_access_key=s3_config.credentials.aws_secret_access_key,
            )
            self.bucket = s3_config.location.bucket  # "my-bucket"
            pf = s3_config.location.prefix  # "my-root-folder/"
            # append trailing separator if provided
            pf = pf + "/" if pf and not pf.endswith("/") else pf
            # remove leading slash if present
            self.prefix = pf.removeprefix("/")

    def post(self):
        try:
            return self._post()
        except Exception:
            logger.error(traceback.format_exc())

    def _post(self):

        r = RequestData(request)

        # make our temp directory
        upload_session_root = self.get_upload_session_root(r.upload_id)
        temporary_folder_for_file_chunks = upload_session_root / r.unique_identifier

        if not temporary_folder_for_file_chunks.exists():
            temporary_folder_for_file_chunks.mkdir(parents=True)
            if self.upload_to_s3:
                # use multipart upload for multichunks
                if r.n_chunks_total > 1:
                    # chunk size should be greater than 5Mb for s3 multipart upload
                    if r.chunk_number == 1 and r.chunk_size <= S3_MIN_CHUNK_SIZE:
                        # set chunkSize to a value greater than 5 for Upload component
                        abort(
                            500,
                            "Chunk size should be greater than 5 Mb for multipart upload",
                        )

                    res = self.s3.create_multipart_upload(
                        Bucket=self.bucket, Key=self.get_s3_path(r)
                    )
                    s3_upload_id = res["UploadId"]
                    self.UPLOADS[r.unique_identifier] = {
                        "UploadId": s3_upload_id,
                        "Parts": [],
                    }
                    self.server.logger.debug("Start multipart upload %s" % s3_upload_id)
                else:
                    # do nothing for single chunks, just upload later
                    pass

        # save the chunk data
        chunk_name = get_chunk_name(r.filename, r.chunk_number)
        chunk_file = temporary_folder_for_file_chunks / chunk_name

        # make a lock file
        lock_file_path = temporary_folder_for_file_chunks / f".lock_{r.chunk_number}"

        with open(lock_file_path, "a"):
            os.utime(lock_file_path, None)

        r.chunk_data.save(chunk_file)

        if self.upload_to_s3:
            with open(chunk_file, "rb") as stored_chunk_file:
                if r.n_chunks_total > 1:
                    s3_upload = self.UPLOADS.get(r.unique_identifier)
                    part = self.s3.upload_part(
                        Body=stored_chunk_file,
                        Bucket=self.bucket,
                        Key=self.get_s3_path(r),
                        UploadId=s3_upload["UploadId"],
                        PartNumber=r.chunk_number,
                    )
                    self.server.logger.debug(
                        "Uploaded part to s3: %s - %s", r.chunk_number, part
                    )
                    s3_upload["Parts"].append(
                        {"PartNumber": r.chunk_number, "ETag": part["ETag"]}
                    )
                else:
                    # upload chunk directly
                    self.s3.upload_fileobj(
                        Fileobj=stored_chunk_file,
                        Bucket=self.bucket,
                        Key=self.get_s3_path(r),
                    )

        self.remove_file(lock_file_path)

        # check if the upload is complete
        chunk_paths = [
            os.path.join(
                temporary_folder_for_file_chunks, get_chunk_name(r.filename, x)
            )
            for x in range(1, r.n_chunks_total + 1)
        ]
        upload_complete = all([os.path.exists(p) for p in chunk_paths])

        # combine all the chunks to create the final file
        if upload_complete:

            # Make sure all files are finished writing
            # but do not wait forever..
            tried = 0
            while any(
                [
                    os.path.isfile(
                        os.path.join(
                            temporary_folder_for_file_chunks, ".lock_{:d}".format(chunk)
                        )
                    )
                    for chunk in range(1, r.n_chunks_total + 1)
                ]
            ):
                tried += 1
                if tried >= 5:
                    logger.error(
                        "Error uploading files with temporary_folder_for_file_chunks: %s.",
                        temporary_folder_for_file_chunks,
                    )
                    raise Exception(
                        "Error uploading files with temporary_folder_for_file_chunks: "
                        + temporary_folder_for_file_chunks
                    )
                time.sleep(1)

            if self.upload_to_s3 and r.n_chunks_total > 1:
                # we need to complete the multipart upload process
                s3_upload = self.UPLOADS.get(r.unique_identifier)
                result = self.s3.complete_multipart_upload(
                    Bucket=self.bucket,
                    Key=self.get_s3_path(r),
                    UploadId=s3_upload["UploadId"],
                    MultipartUpload={"Parts": s3_upload["Parts"]},
                )
                self.server.logger.debug("Uploaded file to s3: %s", result)
            else:
                # Make sure some other chunk didn't trigger file reconstruction
                target_file_name = os.path.join(upload_session_root, r.filename)
                if os.path.exists(target_file_name):
                    logger.info(
                        "File %s exists already. Overwriting..", target_file_name
                    )
                    self.remove_file(target_file_name)

                with open(target_file_name, "ab") as target_file:
                    for p in chunk_paths:
                        with open(p, "rb") as stored_chunk_file:
                            target_file.write(stored_chunk_file.read())
                self.server.logger.debug("File saved to: %s", target_file_name)
            shutil.rmtree(temporary_folder_for_file_chunks)
            if self.upload_to_s3 and r.n_chunks_total > 1:
                # remove the upload record from the hash table
                self.UPLOADS.pop(r.unique_identifier, None)

        return r.filename

    def get(self):
        try:
            return self._get()
        except Exception:
            logger.error(traceback.format_exc())

    def _get(self):
        # flow.js uses a GET request to check if it uploaded the file already.
        # https://github.com/flowjs/flow.js/
        # TODO: Since testChunks is set to false, this seems to be permanently disabled.
        #       Should this be removed altogether?

        r = RequestData(request)

        if not (r.unique_identifier and r.filename and r.chunk_number):
            # Parameters are missing or invalid
            abort(500, "Parameter error")

        # chunk folder path based on the parameters
        temporary_folder_for_file_chunks = os.path.join(
            self.get_upload_session_root(r.upload_id), r.unique_identifier
        )

        # chunk path based on the parameters
        chunk_file = os.path.join(
            temporary_folder_for_file_chunks, get_chunk_name(r.filename, r.chunk_number)
        )
        self.server.logger.debug("Getting chunk: %s", chunk_file)

        if os.path.isfile(chunk_file):
            # Let flow.js know this chunk already exists
            return "OK"
        else:
            # Let flow.js know this chunk does not exists
            # and needs to be uploaded
            abort(404, "Not found")

    def get_upload_session_root(self, upload_id):
        return (
            (self.upload_folder / upload_id)
            if self.use_upload_id
            else self.upload_folder
        )

    def get_s3_path(self, r: RequestData):
        return os.path.join(self.prefix, r.upload_id, r.relative_path)


class HttpRequestHandler(BaseHttpRequestHandler):
    # You may use the flask.request
    # and flask.session inside the methods of this
    # class when needed.
    def __init__(self, *args, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)

    def post_before(self):
        pass

    def post(self):
        self.post_before()
        returnvalue = super().post()
        self.post_after()
        return returnvalue

    def post_after(self):
        pass

    def get_before(self):
        pass

    def get(self):
        self.get_before()
        returnvalue = super().get()
        self.get_after()
        return returnvalue

    def get_after(self):
        pass
