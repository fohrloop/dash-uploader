from pathlib import Path

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, State

import dash_uploader.settings as settings
from dash_uploader.uploadstatus import UploadStatus
from dash_uploader.utils import dash_version_is_at_least


def _create_dash_callback(callback, settings):  # pylint: disable=redefined-outer-name
    """Wrap the dash callback with the du.settings.
    This function could be used as a wrapper. It will add the
    configurations of dash-uploader to the callback.
    """

    def wrapper(
        callbackbump,
        uploaded_filenames,
        total_files_count,
        uploaded_files_size,
        total_files_size,
        upload_id,
        *args,
    ):
        if not callbackbump:
            raise PreventUpdate()

        uploadedfilepaths = []
        if uploaded_filenames is not None:
            if upload_id:
                root_folder = Path(settings.UPLOAD_FOLDER_ROOT) / upload_id
            else:
                root_folder = Path(settings.UPLOAD_FOLDER_ROOT)

            for filename in uploaded_filenames:
                file = root_folder / filename
                uploadedfilepaths.append(str(file))

        status = UploadStatus(
            uploaded_files=uploadedfilepaths,
            n_total=total_files_count,
            uploaded_size_mb=uploaded_files_size,
            total_size_mb=total_files_size,
            upload_id=upload_id,
        )
        return callback(status, *args)

    return wrapper


def callback(
    output,
    id="dash-uploader",
    state=None,   # The state parameter is placed last in order to maintain better parameter order compatibility.
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
        dash_callback = _create_dash_callback(
            function,
            settings,
        )

        if not hasattr(settings, "app"):
            raise Exception(
                "The du.configure_upload must be called before the @du.callback can be used! Please, configure the dash-uploader."
            )

        kwargs = dict()
        if dash_version_is_at_least("1.12"):
            # See: https://github.com/plotly/dash/blob/dev/CHANGELOG.md  and
            #      https://community.plotly.com/t/dash-v1-12-0-release-pattern-matching-callbacks-fixes-shape-drawing-new-datatable-conditional-formatting-options-prevent-initial-call-and-more/38867
            # the `prevent_initial_call` option was added in Dash v.1.12
            kwargs["prevent_initial_call"] = True

        # Input: Change in the props will trigger callback.
        #     Whenever 'this.props.setProps' is called on the JS side,
        #     (dash specific special prop that is passed to every
        #     component of the dash app), a HTTP request is used to
        #     trigger a change in the property/attribute of a dash
        #     python component.
        # State: Pass along extra values without firing the callbacks.
        #
        # See also: https://dash.plotly.com/basic-callbacks
        states = [
                State(id, "uploadedFileNames"),
                State(id, "totalFilesCount"),
                State(id, "uploadedFilesSize"),
                State(id, "totalFilesSize"),
                State(id, "upload_id"),
            ]
        if state:
            if isinstance(state, list):
                states.extend(state)
            else:
                states.append(state)
        dash_callback = settings.app.callback(
            output,
            [Input(id, "dashAppCallbackBump")],
            states,
            **kwargs
        )(dash_callback)

        return function

    return add_callback
