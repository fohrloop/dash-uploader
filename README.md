![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/np-8/dash-uploader)&nbsp;![PyPI](https://img.shields.io/pypi/v/dash-uploader)&nbsp;![PyPI - Downloads](https://img.shields.io/pypi/dm/dash-uploader)&nbsp;![GitHub](https://img.shields.io/github/license/np-8/dash-uploader)

![upload large files with dash-uploader](docs/upload-demo.gif)

# 📤 dash-uploader

The alternative upload component for [Dash](https://dash.plotly.com/) applications. 

## 📢 dash-uploader 0.7.0 pre-release available 

🎉 There is pre-release version of dash-uploader 0.7.0 available in PyPI! 🎉 

```
python -m pip install dash-uploader --pre
```

- It fixes the multi-file upload issues!  
- Please, test it and give feedback to this [discussion](https://github.com/np-8/dash-uploader/discussions/88). 


## Table of contents
- [Short summary](#short-summary)
- [dash-uploader vs. dcc.Upload](#dash-uploader-vs-dccupload)
- [Installing](#installing)
- [Quickstart](#quickstart)
  - [Simple example](#simple-example)
  - [Example with callback](#example-with-callback-and-other-options)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [Changelog](#changelog)
- [Credits](#credits)

## Short summary
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 💾 Data file size has no limits. (Except the hard disk size)<bR>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ☎ Call easily a callback after uploading is finished.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 📤 Upload files using [flow.js](https://github.com/flowjs/flow.js/) <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 📦 All JS and CSS bundled with the package. No need for network calls for CSS/JS.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ✅ Works with Dash 1.1.0.+ & Python 3.6+. (Possibly with other versions, too)<br>


### dash-uploader vs. [dcc.Upload](https://dash.plotly.com/dash-core-components/upload)





|                       | dash-uploader                                      | [dcc.Upload](https://dash.plotly.com/dash-core-components/upload)                                                                                                                    |
| --------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Underlying technology | [flow.js](https://github.com/flowjs/flow.js/)      | HTML5 API                                                                                                                                                                            |
| File size             | Unlimited                                          | max ~150-200Mb ([link](https://community.plotly.com/t/dash-upload-component-decoding-large-files/8033/11))                                                                           |
| Uploads to            | Hard disk (server side)                            | First to browser memory (user side) Then, to server using callbacks.                                                                                                                 |
| Data type             | Uploaded as file; no need to parse at server side. | Uploaded as byte64 encoded string  -> Needs parsing                                                                                                                                  |
| See upload progress?  | Progressbar out of the box                         | No upload indicators out of the box. Generic loading indicator possible. [Progressbar not possible](https://community.plotly.com/t/upload-after-confirmation-and-progress-bar/7172). |

# Installing
```
pip install dash-uploader
```

# Quickstart

Full documentation [here](docs/dash-uploader.md) 
>⚠️**Security note**: The Upload component allows POST requests and uploads of arbitrary files to the server harddisk and one should take this into account (with user token checking etc.) if used as part of a public website! For this you can utilize the  `http_request_handler` argument of the [du.configure_upload](https://github.com/np-8/dash-uploader/blob/master/docs/dash-uploader.md#duconfigure_upload). (New in version 0.5.0)

## Simple example

```python
import dash
import dash_html_components as html
import dash_uploader as du

app = dash.Dash(__name__)

# 1) configure the upload folder
du.configure_upload(app, r"C:\tmp\Uploads")

# 2) Use the Upload component
app.layout = html.Div([
    du.Upload(),
])

if __name__ == '__main__':
    app.run_server(debug=True)

```

## Example with callback (and other options)
- **New in version 0.7.0:** Functions decorated with [`@du.callback`](https://github.com/np-8/dash-uploader/blob/dev/docs/dash-uploader.md#ducallback) must take `status` ([`du.UploadStatus`](https://github.com/np-8/dash-uploader/blob/dev/docs/dash-uploader.md#duuploadstatus)) object as the only input parameter (previously, `filenames`)


```python
from pathlib import Path
import uuid

import dash_uploader as du
import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

UPLOAD_FOLDER_ROOT = r"C:\tmp\Uploads"
du.configure_upload(app, UPLOAD_FOLDER_ROOT)

def get_upload_component(id):
    return du.Upload(
        id=id,
        max_file_size=1800,  # 1800 Mb
        filetypes=['csv', 'zip'],
        upload_id=uuid.uuid1(),  # Unique session id
    )


def get_app_layout():

    return html.Div(
        [
            html.H1('Demo'),
            html.Div(
                [
                    get_upload_component(id='dash-uploader'),
                    html.Div(id='callback-output'),
                ],
                style={  # wrapper div style
                    'textAlign': 'center',
                    'width': '600px',
                    'padding': '10px',
                    'display': 'inline-block'
                }),
        ],
        style={
            'textAlign': 'center',
        },
    )


# get_app_layout is a function
# This way we can use unique session id's as upload_id's
app.layout = get_app_layout


@du.callback(
    output=Output("callback-output", "children"),
    id="dash-uploader",
)
def callback_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files])



if __name__ == '__main__':
    app.run_server(debug=True)

```

## S3 upload support
Direct S3 support is can be enabled by installing the package with `s3` option (`python -m pip install dash-uploader[s3]`).
In order to upload the files directly to an S3 bucket, you could set up an `S3Configuration` object and pass it
to the `configure_upload` method.

Here is a minimal example;

```python
import boto3
session = boto3.Session()
# credentials will be fetched from environment variables or local aws configuration
# see https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html on 
# how to configure credentials for s3
credentials = session.get_credentials()
credentials = credentials.get_frozen_credentials()
access_key = credentials.access_key
secret_key = credentials.secret_key
from dash_uploader import s3
s3_config = s3.S3Configuration(
    location=s3.S3Location(
        region_name = "eu-central-1",
        endpoint_url="https://s3.eu-central-1.amazonaws.com",
        use_ssl=True,
        bucket="my-bucket",
        prefix="my-prefix",
    ),
    credentials=s3.S3Credentials(
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
    )
)

UPLOAD_FOLDER_ROOT = r"/tmp/Uploads"
du.configure_upload(app=app, folder=UPLOAD_FOLDER_ROOT, s3_config=s3_config)

```

> If `s3_config` is not specified, then a standard upload to local storage will be used.

Files will be uploaded to `<endpoint_url>/<bucket>/<prefix>/[<upload_id>/]`. (`<upload_id>/` will be used only if `use_upload_id` set to `True` in `du.configure_upload`)

>⚠️ Large files will be uploaded to s3 in chunks using multiple upload functionality.
`boto3` supports multiple upload only if the chunks are larger than 5Mib. This can be set while creating the `du.Upload` component.

> `UPLOAD_FOLDER_ROOT` is still required to store the chunks of large files being uploaded to s3.


## Passing multiple states to `du.callback`

Now it is possible to capture Dash components states in a `du.callback`. Simply pass `State` object(s) like you would typically do for a Dash callback.

```python
@du.callback(
    output=Output("callback-output", "children"),
    id="dash-uploader",
    state=State("callback-output", "children"),
)
def callback_on_completion(status: du.UploadStatus, state):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files])

```


## Contributing


| What?                                | How?                                                                                                                                                                                                                                         |
| :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🐞 Found a bug?                       | 🎟 <a href="https://github.com/np-8/dash-uploader/issues">File an Issue</a>                                                                                                                                                                   |
| 🙋‍♂️ Need help?                         | ❔  <a href="https://stackoverflow.com/questions/ask">Ask a question on StackOverflow</a> <br><a href="https://community.plotly.com/t/show-and-tell-dash-uploader-upload-large-files/38451">📧 Use this thread on community.plotly.com</a>     |
| 💡  Want to submit a feature request? | <a href="https://community.plotly.com/t/show-and-tell-dash-uploader-upload-large-files/38451">🎭 Discuss about it on community.plotly.com</a><br><a href="https://github.com/np-8/dash-uploader/issues">🎫 File an Issue (feature request)</a> |
| 🧙  Want to write code?               | 🔥 <a href="./docs/CONTRIBUTING.md">Here's how you get started!</a>                                                                                                                                                                           |
## Documentation
- [Documentation](docs/dash-uploader.md)
- [Developer documentation](docs/CONTRIBUTING.md)
- [Migration Guide](https://github.com/np-8/dash-uploader/wiki/Migration-Guide)

## Changelog

- [Changelog](./docs/CHANGELOG.md)
## Credits
- History: This package is based on the React 16 compatible version [dash-resumable-upload](https://github.com/westonkjones/dash-resumable-upload) (0.0.4) by [Weston Jones](https://github.com/westonkjones/) which in turn is based on [dash-resumable-upload](https://github.com/rmarren1/dash-resumable-upload) (0.0.3) by [Ryan Marren](https://github.com/rmarren1) 
- The package boilerplate is taken from the [dash-component-boilerplate](https://github.com/plotly/dash-component-boilerplate).
- The uploading JS function utilizes the [flow.js](https://github.com/flowjs/flow.js/) (2.14.x).
- The JS component is created using [React](https://github.com/facebook/react) (17.0.x)
- The CSS styling is mostly from [Bootstrap](https://getbootstrap.com/) 4.
