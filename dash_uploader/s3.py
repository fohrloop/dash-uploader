# Confguration parameters if the files to be uploaded to a S3 bucket
from dataclasses import dataclass
from typing import Optional


@dataclass
class S3Location:
    # s3 region name
    region_name: str
    # bucket name
    bucket: str
    # s3 endpoint URL like 'example.xxx.amazonaws.com'
    #  if "http/https" scheme provided `use_ssl` is ignored
    endpoint_url: str
    # whether to use secure connection
    use_ssl: Optional[bool] = True
    # optional prefix under the bucket if provided should end with '/'
    prefix: Optional[str] = ""


@dataclass
class S3Credentials:
    # access key id
    aws_access_key_id: str
    # secret key
    aws_secret_access_key: str

@dataclass
class S3Configuration:
    location: S3Location
    credentials: S3Credentials