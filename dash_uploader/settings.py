# The default upload api endpoint
# The du.configure_upload can change this
upload_api = "/API/resumable"

# Needed if using a proxy; when dash.Dash is used
# with a `requests_pathname_prefix`.
# The front-end will prefix this string to the requests
# that are made to the proxy server
requests_pathname_prefix = '/'