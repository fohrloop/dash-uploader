

#  dash-uploader
To use the Upload component you need to two things
- Configure dash-uploader with [`du.configure_upload`](#duconfigure_upload)
- Create the upload component with [`du.Upload`](#duupload)

Typically you also would like to define [callbacks](#3-callbacks) (functions that are called automatically when upload finishes).

> ⚠️**Security note**: The Upload component allows uploads of arbitrary files to the server harddisk and one should take this into account (with user token checking etc.) if used as part of a public website! Particularly, the `configure_upload` opens a route for `POST` HTTP requests. Use the [`http_request_handler`](#http_request_handler--none-or-subclass-of--duhttprequesthandler) argument for defining your custom validation logic.


# Table of contents

  [1 Configuring dash-uploader](#1-configuring-dash-uploader)
- [`du.configure_upload`](#duconfigure_upload)
- [`du.configure_upload_flask`](#duconfigure_upload_flask)

[2 Creating Upload components](#2-creating-upload-components)
- [`du.Upload`](#duupload)

 [3 Callbacks](#3-callbacks)
- [`@du.callback`](#ducallback)
- [`@app.callback`](#appcallback)
 
[4 Custom handling of HTTP Requests](#4-custom-handling-of-http-requests)
- [`du.HttpRequestHandler`](#duhttprequesthandler)

[5 A short example of cross-domain uploading](#5-a-short-example-of-cross-domain-uploading)
- [`Local dashboard side`](#local-dashboard-side)
- [`Remote flask service side`](#remote-flask-service-side)
<hr>

## 1 Configuring dash-uploader

You need to configure the dash uploader after you created your dash application instance (`app`) and before you create any Upload components

**Example 1: file server is provided by `dash`**
```python
import dash
import dash_uploader as du

app = dash.Dash(...)
# Configure components and the main layout...

du.configure_upload(app, r'C:\tmp\uploads')
```

**Example 2: file server is provided by `flask`**
```python
import flask
import dash_uploader as du

app = flask.Flask(...)

du.configure_upload_flask(app, r'C:\tmp\uploads')
```

### `du.configure_upload`

```python
configure_upload(app, folder, use_upload_id=True, upload_api=None, allowed_origins=None, http_request_handler=None)
```

#### app: dash.Dash
The application instance. Usually created using
```python
app = dash.Dash(__name__)
```
#### folder: str
The folder where to upload files.  Can be relative 
(`"uploads"`) or absolute (`r"C:\tmp\my_uploads"`).
If the folder does not exist, it will be created
automatically.

#### use_upload_id: bool (Default: True)
Determines if the uploads are put into
folders defined by a "upload id". To define an upload id, use the `upload_id` parameter of the `du.Upload` component. In typical use case, upload id's are unique for different users. In that case, you must use a callable as the `app.layout`.

If True, uploads will be put into `<folder>/<upload_id>/`;
that is, every user (for example with different 
session id) will use their own folder. If False, 
all files from all sessions are uploaded into
same folder (not recommended).

#### upload_api: None or str
The upload api endpoint to use; the url that is used
internally for the upload component POST and GET HTTP
requests. For example, using `upload_api="/API/dash-uploader"` would create api endpoint and use address

```
http://<myhost>[<requests_pathname_prefix>]/API/dash-uploader
```
for the communication between the front-end and the server. The `requests_pathname_prefix` is added automatically, if the dash `app` instance has `requests_pathname_prefix`. (used with proxies)

#### allowed_origins: None or str or [str]
*New in version **0.6.0***

The list of allowed origin(s) for the cross-domain access. If set `'*'`, all domains would be allowed. If set `None`, would use `du.settings` to configure the origin(s).

> The default configurations is
> ```python
> du.settings.allowed_origins = '*'
> ```

#### http_request_handler:  None or subclass of  du.HttpRequestHandler
*New in version **0.5.0***

Used for custom configuration on the HTTP POST and GET requests. This can be used to add validation for the HTTP requests (⚠️Important
if your site is public!). If None, dash_uploader.HttpRequestHandler is used.
If you provide a class, use a subclass of `du.HttpRequestHandler`.
See the documentation of [`@du.HttpRequestHandler`](#duhttprequesthandler) for
more details.

### `du.configure_upload_flask`
*New in version **0.6.0***

```python
configure_upload_flask(app, folder, use_upload_id=True, upload_api=None, allowed_origins=None, http_request_handler=None)
```

#### app: flask.Flask
The application instance. Usually created using
```python
app = flask.Flask(__name__)
```

#### folder: str
The same as the argument of `du.configure_upload`.

#### use_upload_id: bool (Default: True)
The same as the argument of `du.configure_upload`.

#### upload_api: None or str
The same as the argument of `du.configure_upload`.

#### allowed_origins: None or str or [str]
The same as the argument of `du.configure_upload`.

#### http_request_handler:  None or subclass of  du.HttpRequestHandler
The same as the argument of `du.configure_upload`.

## 2 Creating Upload components
### `du.Upload`
Below are the arguments for the `du.Upload` component and their default values.
```python
Upload(
    id='dash-uploader',
    text='Drag and Drop Here to upload!',
    text_completed='Uploaded: ',
    cancel_button=True,
    pause_button=False,
    filetypes=None,
    max_file_size=1024,
    chunk_size=1,
    default_style=None,
    upload_id=None,
    service_addr=None,
    max_files=1,
)
```

#### id: str (default: 'dash-uploader')
The html id for the component. This is needed when defining callbacks. Note that ids must be unique in a dash application.


#### text: str (Default: ''Drag and Drop Here to upload!')

The text to be shown in the upload "Drag
and Drop" area. Optional.

#### text_completed: str

The text to show in the upload area 
after upload has completed succesfully before
the name of the uploaded file. 

For example, if user
uploaded "data.zip" and `text_completed` is 
"Ready! ", then user would see text "Ready! 
data.zip".

#### cancel_button: bool
If True, shows a cancel button.

#### pause_button: bool
    If True, shows a pause button.

#### filetypes: list of str or None
The filetypes that can be uploaded. 
For example `['zip', 'rar']`.
Note that this just checks the extension of the 
filename, and user might still upload any kind 
of file (by renaming)!
By default, all filetypes are accepted.

#### max_file_size: numeric
The maximum file size in Megabytes. Default: 1024 (=1Gb).

#### chunk_size: numeric
*New in version **0.6.0***
The chunk size in Megabytes. Optional. Default: 1 (=1Mb).

#### default_style: None or dict

Inline CSS styling for the main div element. 
If None, use the default style of the component.
If dict, will use the union on the given dict
and the default style. (you may override
part of the style by giving a dictionary)
More styling options through the CSS classes.

#### upload_id: None or str
The upload id, created with `uuid.uuid1()` or uuid.uuid4(), for example. If `None`, creates random session id with `uuid.uuid1()`.  Defines a subfolder where the files are to be uploaded.

Only used, if `use_upload_id` parameter is set to `True` in [`du.configure_upload`](#duconfigure_upload).

#### service_addr: None or str
*New in version **0.6.0***

The address of the upload target API. If given `None`, would use the default configurations. In this case, the uploader would upload files to the local service. Setting this argument would override the configurations in `du.settings`.

The default service addr is generated by joining `du.settings.routes_pathname_prefix` and `du.settings.upload_api` together. This option would override the whole addr, **not only** the `upload_api`.

> The default configurations is
> ```python
> du.settings.routes_pathname_prefix = '/'
> du.settings.upload_api = '*'
> ```

#### max_files: int (default: 1)
>⚠️ **Experimental** feature. Read below. For bulletproof
implementation, force usage of zip files and keep
max_files = 1.

The number of files that can be added to 
the upload field simultaneously.

**Notes**: <br>
**(1)** If even a single file which is not supported file
    type (i.e. missing in  `filetypes`), is added to the upload queue, upload process of all files will be permanently interrupted. <br>
**(2)** Use reasonably small number in `max_files`. <br>
**(3)** When uploading two (or more) folders with Chrome, there is 
    a bug in resumable.js which makes only one of the
    folders to be uploaded. See:
    https://github.com/23/resumable.js/issues/416<br>
**(4)** When uploading folders, note that the subdirectories
    are **not** created -> All files in the folders will
    be uploaded to the single upload folder.<br>



## 3 Callbacks

Callbacks can be defined using two different approaches
- `@du.callback`: short notation, for typical use cases
- `@app.callback`: needs more verbose code. In case you need more control than when using the `@du.callback`.


In the following example it is assumed that the `du.Upload` component id is `dash-uploader`, i.e. the component was created with:

```
du.Upload(
    id='dash-uploader',
)
```
###  `@du.callback`
*New in version **0.6.0***

Add the option `prevent_initial_call`. This option would only work when `dash>=1.12.0`.

*New in version **0.3.0***

Easiest way to call a simple callback after uploading would be something like:

```python
@du.callback(
    output=Output('callback-output', 'children'),
    id='dash-uploader',
    prevent_initial_call=True,
)
def get_a_list(filenames):
    return html.Ul([html.Li(filenames)])
```

The syntax is
```python
@du.callback(
    output=<Output>,
    id=<Upload_id>,
    prevent_initial_call=<bool>,
)
def call_me(filenames):
    # Do some processing
    return <Dash component>
```

> The option `prevent_initial_call` would prevent the uploader callback to be fired when the component is initialized. This feature is supported since `dash>=1.12.0`. If your dash version is lower than `v1.12.0`, `du.callback` is still compatible, but this option would not work.

#### output: dash.dependencies.Output

This is the Output object, just as in regular [dash callbacks](https://dash.plotly.com/basic-callbacks).

#### output: str
This must be the same `id` as used when initiating your `du.Upload` component.

#### call_me: function
A function that takes exactly one argument: `filenames`.

#### filenames: list of str
A list of strings. These will be the uploaded files. For example: 
`['C:\tmp\Uploads\166d6f24-a80d-11ea-aa00-f48c5012fb50\dataset.csv']`

#### Dash component
The return value of the `call_me` should be a dash component, as in the regular [dash callbacks].

### `@app.callback`


This method needs more verbose code and it is the conventional "[dash way]((https://dash.plotly.com/basic-callbacks))" to create a callback.  Use this if `@du.callback` does not give you enough control.

The syntax can be seen in the following example
```python
@app.callback(
    Output('callback-output', 'children'),
    [Input('dash-uploader', 'isCompleted')],
    [State('dash-uploader', 'fileNames'),
     State('dash-uploader', 'upload_id')],
)
def callback_on_completion(iscompleted, filenames, upload_id):
    if not iscompleted:
        return

    out = []
    if filenames is not None:
        if upload_id:
            root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
        else:
            root_folder = Path(UPLOAD_FOLDER_ROOT)

        for filename in filenames:
            file = root_folder / filename
            out.append(file)
        return html.Ul([html.Li(str(x)) for x in out])

    return html.Div("No Files Uploaded Yet!")
```

#### du.Upload properties used
- `isCompleted`: boolean flag indicating if uploading has been completed. 
- `fileNames`: List of strings of the filenames or None. This does not have the upload folder or the upload_id in it. 
- `upload_id`: The upload id used when initiating the `du.Upload` component.

## 4 Custom handling of HTTP Requests
### `du.HttpRequestHandler`
*New in version **0.5.0***

The `HttpRequestHandler` is a class that is meant to be subclassed. It is used as an argument for [`configure_upload`](#duconfigure_upload), and it makes custom HTTP POST and GET request handling possible. For example, if you run your dash app publicly, you should use some validation logic to validate the HTTP requests from the users!


#### Example of a subclass

```python
class HttpRequestHandler(BaseHttpRequestHandler):
    # You may use the flask.request
    # and flask.session inside the methods of this
    # class when needed.
    def __init__(self, *args, **kwargs):
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
```

#### How does this all work?

- The React Component of `dash-uploader` sends HTTP POST requests. It could in the future send also HTTP GET requests, or other HTTP requests.
- The Flask server (Dash uses Flask underneath) is configured in [`configure_upload`](#duconfigure_upload) to call the `post()` function of the `http_request_handler` on every HTTP POST request directed to the API endpoint of the dash-uploader.
- The values in the POST request are listed in [Documentation of resumable.js](https://github.com/23/resumable.js#how-do-i-set-it-up-with-my-server). Most interesting from these is probably the filename (`resumableFilename`).  In addition to these, there is `upload_id` added by the `dash-uploader`, if `use_upload_id=True` when calling [`configure_upload`](#duconfigure_upload).
- You can use the [flask.request](https://flask.palletsprojects.com/en/1.1.x/api/#flask.request) and [flask.session](https://flask.palletsprojects.com/en/1.1.x/api/#flask.session) proxies as you like. There you get access to all the HTTP Request parameters and Cookies, for example. As an quick example, to get the request filename, upload_id and some cookie value, you can use:

```python
from flask import request 

filename = request.form.get("resumableFilename", default="error", type=str)
upload_id = request.form.get("upload_id", default="", type=str)
cookie_value = request.cookies.get('some_cookie')
```

## 5 A short example of cross-domain uploading
*New in version **0.6.0***

The dash-uploader support the cross-domain uploading when your file server is deployed by remote flask apps. In this section, we would introduce this feature by the following example:

![](https://mermaid.ink/img/eyJjb2RlIjoiZmxvd2NoYXJ0IExSXG4gICAgc3ViZ3JhcGggbG9jYWxbTG9jYWwgRGFzaF1cbiAgICAgICAgdXAxKGR1LlVwbG9hZCAxPGJyPnNlcnZpY2VfYWRkcj1pcDE6cG9ydDEvQVBJLi4uKVxuICAgICAgICB1cDIoZHUuVXBsb2FkIDI8YnI-c2VydmljZV9hZGRyPWlwMjpwb3J0Mi9BUEkuLi4pXG4gICAgICAgIHVwbiguLi4pXG4gICAgZW5kXG5cbiAgICByZW1vdGUxW1JlbW90ZSBGbGFzayAxPGJyPmlwMTpwb3J0MS9BUEkuLi5dOjo6YXBwXG4gICAgcmVtb3RlMltSZW1vdGUgRmxhc2sgMjxicj5pcDI6cG9ydDIvQVBJLi4uXTo6OmFwcFxuICAgIHJlbW90ZW5bLi4uXTo6OmFwcFxuXG4gICAgdXAxLS0-cmVtb3RlMVxuICAgIHVwMi0tPnJlbW90ZTJcbiAgICB1cG4tLT5yZW1vdGVuXG5cbiAgICBjbGFzc0RlZiBhcHAgZmlsbDojZmZmNGRkLCBzdHJva2U6I0VFRENCQTtcbiIsIm1lcm1haWQiOnsidGhlbWUiOiJkZWZhdWx0In0sInVwZGF0ZUVkaXRvciI6ZmFsc2V9)

> Currently, the cross-domain remote service supports both the `dash` app and the `flask` app. By providing the `service_addr` option for the `dash.Upload`, you could upload your files to a remote dashboard or a remote flask app from your local dashboard.

### Local dashboard side

We assume that our local dashboard is deployed on `localhost:8060`. The remote service is deployed on `localhost:8061`. Here we show an example of the dash component defined in the local dashboard:

```python
du.Upload(
    id='uploader',
    text='Drag & Drop or Select a File',
    filetypes=None,
    upload_id='.',
    max_files=1,
    chunk_size=5,
    max_file_size=20 * 1024,
    service_addr='http://localhost:8061/API/resumable',
    default_style={
        'width': '100%',
        'paddingLeft': '.5rem',
        'paddingRight': '.5rem',
        'minHeight': 'min-content',
        'lineHeight': '50px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center'
    }
),
```

Defining more than one `du.Upload` is possible. Users could configure different `service_addr`s for different `du.Upload`s.

The dash app could be deployed by

```python
import dash

app = dash.Dash(__name__, ...)
app.run_server(host='localhost', port=8060, debug=False)
```

### Remote flask service side

A minimal example of the remote service deployed on `localhost:8061` is shown as follows:

```python
import os
import flask

import dash_uploader as du

app = flask.Flask('test-uploader')

os.makedirs('upload', exist_ok=True)
du.configure_upload_flask(app, folder='upload', upload_api='/API/resumable', use_upload_id=False)

if __name__ == '__main__':
    import colorama
    import termcolor

    colorama.init()
    app.run(host='localhost', port=8061, debug=False)
```

To test the performance, users could lauch both services (the dashboard and the `flask` app). The file uploaded by the dashboard would be forwarded to the flask side directly.
