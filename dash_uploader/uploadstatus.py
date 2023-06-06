from pathlib import Path
import warnings
from dash_uploader.s3 import S3Location


class UploadStatus:
    """
    The attributes of UploadStatus are:

    status.latest_file (pathlib.Path):
        The full file path to the file that has been latest uploaded
    status.uploaded_files (list of pathlib.Path):
        The list of full file paths to all of the uploaded files. (uploaded in this session)
    status.is_completed (bool):
        True if all the files have been uploaded
    status.n_uploaded (int):
        The number of files already uploaded in this session
    status.n_total (int):
        The number of files to be uploaded.
    status.uploaded_size_mb (float):
        Size of files uploaded in Megabytes
    status.total_size_mb (float):
        Total size of files to be uploaded in Megabytes
    status.upload_id (str or None):
        The upload id used in the upload process, if any.
    status.s3_location (S3Location or None):
        The S3 location used for uploading, if any
    """

    def __init__(
        self,
        uploaded_files,
        n_total,
        uploaded_size_mb,
        total_size_mb,
        upload_id=None,
        s3_location: S3Location = None,
    ):
        """
        Parameters
        ---------
        uploaded_files: list of str
            The uploaded files from first to latest
        n_uploaded: int
            The number of files already uploaded in this session
        n_total (int):
            The number of files to be uploaded
        uploaded_size_mb (float):
            The size of uploaded files
        total_size_mb  (float):
            The size of all files to be uploaded
        upload_id: None or str
            The upload id used.
        s3_location (S3Location or None):
            The S3 location used for uploading, if any
        """

        self.uploaded_files = [Path(x) for x in uploaded_files]
        self.latest_file = self.uploaded_files[-1]

        self.n_uploaded = len(uploaded_files)
        self.n_total = n_total
        self.upload_id = upload_id

        self.is_completed = self.n_uploaded == n_total
        if self.n_uploaded > n_total:
            warnings.warn(
                "Initializing UploadStatus with n_uploaded > n_total. This should not be happening"
            )

        self.uploaded_size_mb = uploaded_size_mb
        self.total_size_mb = total_size_mb
        self.progress = uploaded_size_mb / total_size_mb
        self.s3_location = s3_location

    def __str__(self):

        vals = [
            f"latest_file = {self.latest_file}",
            f"uploaded_files = [{', '.join(str(x) for x in self.uploaded_files)}]",
            f"is_completed = {self.is_completed}",
            f"n_uploaded = {self.n_uploaded}",
            f"n_total = {self.n_total}",
            f"uploaded_size_mb = {self.uploaded_size_mb}",
            f"total_size_mb = {self.total_size_mb}",
            f"progress = {self.progress}",
            f"upload_id = {self.upload_id}",
            f"s3_location = {self.s3_location}",
        ]
        return "<UploadStatus: " + ", ".join(vals) + ">"
