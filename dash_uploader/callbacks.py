from pathlib import Path

from dash.dependencies import Input, State

import dash_uploader.settings as settings


def query_app_and_root(component_id):
    """Query the app and the root folder by the given component id.
    This is a private method, and should not be exposed to users.
    """
    app_idx = settings.user_configs_query.get(component_id, None)
    if app_idx is None:
        app_idx = settings.user_configs_default
    app_item = settings.user_configs[app_idx]
    if not app_item["is_dash"]:
        raise TypeError("The du.configure_upload must be called with a dash.Dash instance before the @du.callback can be used! Please, configure the dash-uploader.")
    app = app_item["app"]
    upload_folder_root = app_item["upload_folder_root"]
    return app, upload_folder_root


def create_dash_callback(callback, app_root_folder):  # pylint: disable=redefined-outer-name
    """Wrap the dash callback with the upload_folder_root.
    This function could be used as a wrapper. It will add the
    configurations of dash-uploader to the callback.
    This is a private method, and should not be exposed to users.
    """

    def wrapper(iscompleted, filenames, upload_id):
        if not iscompleted:
            return

        out = []
        if filenames is not None:
            if upload_id:
                root_folder = Path(app_root_folder) / upload_id
            else:
                root_folder = Path(app_root_folder)

            for filename in filenames:
                file = root_folder / filename
                out.append(str(file))

        return callback(out)

    return wrapper


def callback(
    output,
    id="dash-uploader",
):
    """
    Add a callback to dash application.
    This callback fires when upload is completed.
    Note: Must be called after du.configure_upload!

    Parameters
    ----------
    output: dash Ouput
        The output dash component
    id: str
        The id of the du.Upload component.

    Example
    -------
    @du.callback(
       output=Output('callback-output', 'children'),
       id='dash-uploader',
    )
    def get_a_list(filenames):
        return html.Ul([html.Li(filenames)])
    """
    app, upload_folder_root = query_app_and_root(id)

    def add_callback(function):
        """
        Parameters
        ---------
        function: callable
            Function that receivers one argument,
            filenames and returns one argument,
            a dash component. The filenames is either
            None or list of str containing the uploaded
            file(s).
        output: dash.dependencies.Output
            The dash output. For example:
            Output('callback-output', 'children')

        """
        dash_callback = create_dash_callback(
            function,
            upload_folder_root,
        )

        dash_callback = app.callback(
            output,
            [Input(id, "isCompleted")],
            [State(id, "fileNames"), State(id, "upload_id")],
        )(dash_callback)
        return function

    return add_callback
