import logging
import os
import shutil
import time
import traceback

from flask import request
from flask import abort

from dash_uploader.utils import retry

logger = logging.getLogger(__name__)


def get_chunk_name(uploaded_filename, chunk_number):
    return uploaded_filename + "_part_%03d" % chunk_number


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

    remove_file = staticmethod(retry(wait_time=0.35, max_time=15.0)(remove_file))

    def __init__(self, server, upload_folder, use_upload_id):
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

        """
        self.server = server
        self.upload_folder = upload_folder
        self.use_upload_id = use_upload_id

    def post(self):
        try:
            return self._post()
        except Exception:
            logger.error(traceback.format_exc())

    def _post(self):

        r = RequestData(request)

        # make our temp directory
        temp_root = self.get_temp_root(r.upload_id)
        temp_dir = os.path.join(temp_root, r.unique_identifier)
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)

        # save the chunk data
        chunk_name = get_chunk_name(r.filename, r.chunk_number)
        chunk_file = os.path.join(temp_dir, chunk_name)

        # make a lock file
        lock_file_path = os.path.join(temp_dir, ".lock_{:d}".format(r.chunk_number))

        with open(lock_file_path, "a"):
            os.utime(lock_file_path, None)
        r.chunk_data.save(chunk_file)
        self.remove_file(lock_file_path)

        # check if the upload is complete
        chunk_paths = [
            os.path.join(temp_dir, get_chunk_name(r.filename, x))
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
                    os.path.isfile(os.path.join(temp_dir, ".lock_{:d}".format(chunk)))
                    for chunk in range(1, r.n_chunks_total + 1)
                ]
            ):
                tried += 1
                if tried >= 5:
                    logger.error("Error uploading files with temp_dir: %s.", temp_dir)
                    raise Exception("Error uploading files with temp_dir: " + temp_dir)
                time.sleep(1)

            # Make sure some other chunk didn't trigger file reconstruction
            target_file_name = os.path.join(temp_root, r.filename)
            if os.path.exists(target_file_name):
                logger.info("File %s exists already. Overwriting..", target_file_name)
                self.remove_file(target_file_name)

            with open(target_file_name, "ab") as target_file:
                for p in chunk_paths:
                    with open(p, "rb") as stored_chunk_file:
                        target_file.write(stored_chunk_file.read())
            self.server.logger.debug("File saved to: %s", target_file_name)
            shutil.rmtree(temp_dir)

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
        temp_dir = os.path.join(self.get_temp_root(r.upload_id), r.unique_identifier)

        # chunk path based on the parameters
        chunk_file = os.path.join(temp_dir, get_chunk_name(r.filename, r.chunk_number))
        self.server.logger.debug("Getting chunk: %s", chunk_file)

        if os.path.isfile(chunk_file):
            # Let flow.js know this chunk already exists
            return "OK"
        else:
            # Let flow.js know this chunk does not exists
            # and needs to be uploaded
            abort(404, "Not found")

    def get_temp_root(self, upload_id):
        return (
            os.path.join(self.upload_folder, upload_id)
            if self.use_upload_id
            else self.upload_folder
        )


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
