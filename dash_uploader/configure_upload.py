import logging
# import os

# from dash import __version__ as dashversion
# import dash_html_components as html

import dash_uploader.settings as settings
from dash_uploader.upload import update_upload_api
from dash_uploader.httprequesthandler import HttpRequestHandler
from dash_uploader.fixture import cross_domain


logger = logging.getLogger("dash_uploader")


def configure_upload(
    app, folder, use_upload_id=True, upload_api=None, allowed_origins=None, http_request_handler=None
):
    """
    Configure the upload APIs for dash app.
    This function is required to be called before using du.callback.

    Parameters
    ---------
    app: dash.Dash
        The application instance
    folder: str
        The folder where to upload files.
        Can be relative ("uploads") or
        absolute (r"C:\\tmp\\my_uploads").
        If the folder does not exist, it will
        be created automatically.
    use_upload_id: bool
        Determines if the uploads are put into
        folders defined by a "upload id" (upload_id).
        If True, uploads will be put into `folder`/<upload_id>/;
        that is, every user (for example with different
        session id) will use their own folder. If False,
        all files from all sessions are uploaded into
        same folder (not recommended).
    upload_api: None or str
        The upload api endpoint to use; the url that is used
        internally for the upload component POST and GET HTTP
        requests. For example: "/API/dash-uploader"
    allowed_origins: None or str or [str]
        The list of allowed origin(s) for the cross-domain access. If
        set '*', all domains would be allowed. If set None, would use
        du.settings to configure the origin(s).
    http_request_handler: None or class
        Used for custom configuration on the Http POST and GET requests.
        This can be used to add validation for the HTTP requests (Important
        if your site is public!). If None, dash_uploader.HttpRequestHandler is used.
        If you provide a class, use a subclass of HttpRequestHandler.
        See the documentation of dash_uploader.HttpRequestHandler for
        more details.
    """
    settings.UPLOAD_FOLDER_ROOT = folder
    settings.app = app

    if upload_api is None:
        upload_api = settings.upload_api
    else:
        # Set the upload api since du.Upload components
        # that are created after du.configure_upload
        # need to be able to read the api endpoint.
        settings.upload_api = upload_api

    # Needed if using a proxy
    settings.requests_pathname_prefix = app.config.get("requests_pathname_prefix", "/")
    settings.routes_pathname_prefix = app.config.get("routes_pathname_prefix", "/")

    upload_api = update_upload_api(settings.routes_pathname_prefix, upload_api)

    if http_request_handler is None:
        http_request_handler = HttpRequestHandler

    decorate_server(
        app.server,
        folder,
        upload_api,
        http_request_handler=http_request_handler,
        allowed_origins=allowed_origins,
        use_upload_id=use_upload_id,
    )


def configure_upload_flask(
    app, folder, use_upload_id=True, upload_api=None, allowed_origins=None, http_request_handler=None,
):
    """
    Configure the upload APIs for flask app.
    When dash uploader is configured for a flask app. The server should be only
    used for accepting files. Configuring du.callback is not allowed in this
    case.

    Parameters
    ----------
    app: flask.Flask
        The flask server instance
    folder: str
        The folder where to upload files.
        Can be relative ("uploads") or
        absolute (r"C:\\tmp\\my_uploads").
        If the folder does not exist, it will
        be created automatically.
    use_upload_id: bool
        Determines if the uploads are put into
        folders defined by a "upload id" (upload_id).
        If True, uploads will be put into `folder`/<upload_id>/;
        that is, every user (for example with different
        session id) will use their own folder. If False,
        all files from all sessions are uploaded into
        same folder (not recommended).
    upload_api: None or str
        The upload api endpoint to use; the url that is used
        internally for the upload component POST and GET HTTP
        requests. For example: "/API/dash-uploader"
    allowed_origins: None or str or [str]
        The list of allowed origin(s) for the cross-domain access. If
        set '*', all domains would be allowed. If set None, would use
        du.settings to configure the origin(s).
    http_request_handler: None or class
        Used for custom configuration on the Http POST and GET requests.
        This can be used to add validation for the HTTP requests (Important
        if your site is public!). If None, dash_uploader.HttpRequestHandler is used.
        If you provide a class, use a subclass of HttpRequestHandler.
        See the documentation of dash_uploader.HttpRequestHandler for
        more details.
    """
    settings.UPLOAD_FOLDER_ROOT = folder

    if upload_api is None:
        upload_api = settings.upload_api
    else:
        # Set the upload api since du.Upload components
        # that are created after du.configure_upload
        # need to be able to read the api endpoint.
        settings.upload_api = upload_api

    # Needed if using a proxy
    settings.requests_pathname_prefix = app.config.get("requests_pathname_prefix", "/")
    settings.routes_pathname_prefix = app.config.get("routes_pathname_prefix", "/")

    upload_api = update_upload_api(settings.routes_pathname_prefix, upload_api)

    if http_request_handler is None:
        http_request_handler = HttpRequestHandler

    decorate_server(
        app,
        folder,
        upload_api,
        http_request_handler=http_request_handler,
        allowed_origins=allowed_origins,
        use_upload_id=use_upload_id,
    )


def decorate_server(
    server,
    temp_base,
    upload_api,
    http_request_handler,
    allowed_origins=None,
    use_upload_id=True,
):
    """
    Parameters
    ----------
    server: flask.Flask
        The flask server instance
    temp_base: str
        The upload root folder
    upload_api: str
        The upload api endpoint to use; the url that is used
        internally for the upload component POST and GET HTTP
        requests.
    use_upload_id: bool
        Determines if the uploads are put into
        folders defined by a "upload id" (upload_id).
        If True, uploads will be put into `folder`/<upload_id>/;
        that is, every user (for example with different
        session id) will use their own folder. If False,
        all files from all sessions are uploaded into
        same folder (not recommended).
    """

    handler = http_request_handler(
        server, upload_folder=temp_base, use_upload_id=use_upload_id
    )

    def get(*args, **kwargs):  # The two wrappers are required, because we need to modify the attributes of the function.
        return handler.get(*args, **kwargs)

    def post(*args, **kwargs):
        return handler.post(*args, **kwargs)

    server.add_url_rule(upload_api, None, cross_domain(methods=['GET'], origin=allowed_origins)(get), methods=['GET', 'OPTIONS'])
    server.add_url_rule(upload_api, None, cross_domain(methods=['POST'], origin=allowed_origins)(post), methods=['POST', 'OPTIONS'])
