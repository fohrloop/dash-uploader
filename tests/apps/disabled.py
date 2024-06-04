"""
Test app used by test_disabled.
"""
import uuid
import json

import dash_uploader as du
import dash

if du.utils.dash_version_is_at_least("2.0.0"):
    from dash import html, dcc
else:
    import dash_html_components as html
    import dash_core_components as dcc

from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__)

UPLOAD_FOLDER_ROOT = r"C:\tmp\Uploads"
du.configure_upload(app, UPLOAD_FOLDER_ROOT)


def get_upload_component(id):
    return du.Upload(
        id=id,
        text="Drag and Drop files here",
        text_completed="Completed: ",
        cancel_button=True,
        max_file_size=1800,  # 1800 MB
        filetypes=["csv", "zip"],
        upload_id=uuid.uuid1(),  # Unique session id
        max_files=2,
    )


def get_app_layout():

    return html.Div(
        [
            html.H1("Demo"),
            html.Div(
                [
                    dcc.Checklist(
                        id="uploader-configs",
                        options=[
                            {"label": "Disabled", "value": 0},
                            {"label": "Disable Drag & Drop", "value": 1},
                        ],
                        value=[],
                        labelStyle={"display": "inline-block"},
                    ),
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
            html.Div(
                children=[
                    "Triggered configs:",
                    html.Span(
                        id="configs-output", children=json.dumps([])
                    ),  # This element needs to be visible, otherwise, selenium could not find its content.
                    html.Button(id="reset-button", n_clicks=0, children="Reset text"),
                ],
                style={
                    "textAlign": "left",
                },  # wrapper div style
            ),
        ],
        style={
            "textAlign": "center",
        },
    )


# get_app_layout is a function
# This way we can use unique session id's as upload_id's
app.layout = get_app_layout


# Create a callback
@du.callback(
    output=Output("callback-output", "children"),
    id="dash-uploader",
)
def callback_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files])


@app.callback(Output("dash-uploader", "disabled"), [Input("uploader-configs", "value")])
def check_disabled(val_configs):
    if 0 in val_configs:  # Disabled
        return True
    else:
        return False


@app.callback(
    Output("dash-uploader", "disableDragAndDrop"), [Input("uploader-configs", "value")]
)
def check_disableDragAndDrop(val_configs):
    if 1 in val_configs:  # Disabled
        return True
    else:
        return False


@app.callback(
    Output("configs-output", "children"),
    [Input("dash-uploader", "disabled"), Input("dash-uploader", "disableDragAndDrop")],
)
def update_config_states(is_disabled, is_disableDragAndDrop):
    """This callback is used for confirming that the states of the element have been changed."""
    val_configs = []
    if is_disabled:
        val_configs.append(0)
    if is_disableDragAndDrop:
        val_configs.append(1)
    return json.dumps(val_configs)


# Possibility to modify text of upload component with a click
# Used in tests to reset the text of the component
# as there will be multiple "Completed" texts expected in a row
@app.callback(
    Output("dash-uploader", "text"),
    Input("reset-button", "n_clicks"),
)
def on_reset_click(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return "Text resetted"


if __name__ == "__main__":
    app.run_server(debug=True)
