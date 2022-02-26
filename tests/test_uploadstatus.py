import dash_uploader as du
from pathlib import Path


def test_uploadstatus_creation_and_serialization():

    status = du.UploadStatus(
        uploaded_files=[
            Path(r"C:\somepath\some-upload-id\file.csv"),
            Path(r"C:\somepath\some-upload-id\another-file.csv"),
        ],
        n_total=5,
        uploaded_size_mb=51,
        total_size_mb=100,
        upload_id="some-upload-id",
    )
    assert status.is_completed == False
    assert status.progress == 0.51
    assert str(status.latest_file) == r"C:\somepath\some-upload-id\another-file.csv"
    assert status.upload_id == "some-upload-id"
    assert status.n_uploaded == 2
    assert status.n_total == 5
