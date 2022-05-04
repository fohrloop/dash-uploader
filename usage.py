import uuid

import dash_uploader as du
import dash


if du.utils.dash_version_is_at_least("2.0.0"):
    from dash import html  # if dash <= 2.0.0, use: import dash_html_components as html
else:
    import dash_html_components as html

from dash.dependencies import Output

app = dash.Dash(__name__)

s3_config = None
# uncomment the following lines to get stored credentials from env or aws config files

# import boto3
# session = boto3.Session()
# credentials = session.get_credentials()
# credentials = credentials.get_frozen_credentials()
# access_key = credentials.access_key
# secret_key = credentials.secret_key
# from dash_uploader.settings import S3Configuration
# s3_config = S3Configuration(
#         region_name = "eu-central-1",
#         endpoint_url="https://s3.eu-central-1.amazonaws.com",
#         use_ssl=True,
#         aws_access_key_id=credentials.access_key,
#         aws_secret_access_key=credentials.secret_key,
#         bucket="my-bucket",
#         prefix="my-prefix",
# )

UPLOAD_FOLDER_ROOT = r"/tmp/Uploads"
du.configure_upload(app=app, folder=UPLOAD_FOLDER_ROOT, s3_config=s3_config)


def get_upload_component(id):
    return du.Upload(
        id=id,
        text="Drag and Drop files here",
        text_completed="Completed: ",
        cancel_button=True,
        pause_button=True,
        max_file_size=130,  # 130 Mb
        max_total_size=350,
        # chunk_size=6, # 6 MB to use multipart upload to s3
        # filetypes=["csv", "zip"],
        upload_id=uuid.uuid1(),  # Unique session id
        max_files=10,
    )


def get_app_layout():

    return html.Div(
        [
            html.H1("Demo"),
            html.Div(
                [
                    get_upload_component(id="dash-uploader"),
                    html.Div(id="callback-output"),
                ],
                style={  # wrapper div style
                    "textAlign": "center",
                    "width": "600px",
                    "padding": "10px",
                    "display": "inline-block",
                },
            ),
        ],
        style={
            "textAlign": "center",
        },
    )


# get_app_layout is a function
# This way we can use unique session id's as upload_id's
app.layout = get_app_layout

# uncomment the following line to get the logs
# app.server.logger.setLevel(logging.DEBUG)


# 3) Create a callback
@du.callback(
    output=Output("callback-output", "children"),
    id="dash-uploader",
)
def callback_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files])


if __name__ == "__main__":
    app.run_server(debug=True)
