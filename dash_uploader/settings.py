from typing import Optional
from dataclasses import dataclass

# The default upload api endpoint
# The du.configure_upload can change this
upload_api = "/API/dash-uploader"

# Needed if using a proxy; when dash.Dash is used
# with a `requests_pathname_prefix`.
# The front-end will prefix this string to the requests
# that are made to the proxy server
requests_pathname_prefix = "/"

# From dash source code:
# Note that `requests_pathname_prefix` is the prefix for the AJAX calls that
# originate from the client (the web browser) and `routes_pathname_prefix` is
# the prefix for the API routes on the backend (this flask server).
# `url_base_pathname` will set `requests_pathname_prefix` and
# `routes_pathname_prefix` to the same value.
# If you need these to be different values then you should set
# `requests_pathname_prefix` and `routes_pathname_prefix`,
# not `url_base_pathname`.
routes_pathname_prefix = "/"

# Confguration parameters if the files to be uploaded to a S3 bucket
@dataclass
class S3Configuration:
    # s3 region name
    region_name: str
    # bucket name
    bucket: str
    # s3 endpoint URL like 'example.xxx.amazonaws.com'
    #  if "http/https" scheme provided `use_ssl` is ignored
    endpoint_url: str
    # access key id
    aws_access_key_id: str
    # secret key 
    aws_secret_access_key: str
    # whether to use secure connection
    use_ssl: Optional[bool] = True
    # optional prefix under the bucket if provided should end with '/'
    prefix: Optional[str] = ""
