from dash_uploader._build.Upload_ReactComponent import Upload_ReactComponent

DEFAULT_STYLE = {
    'width': '100%',
    # min-height and line-height should be the same to make
    # the centering work.
    'minHeight': '100px',
    'lineHeight': '100px',
    'textAlign': 'center',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '7px',
}


# Implemented as function, but still uppercase.
# This is because subclassing the Dash-auto-generated
# "Upload from Upload.py" will give some errorss
def Upload(
    text='Drag and Drop Here to upload!',
    text_completed='Uploaded: ',
    cancel_button=True,
    pause_button=False,
    filetypes=None,
    max_file_size=1024,
    css_id=None,
    default_style=None,
):
    """
    Parameters
    ----------
    text: str
        The text to show in the upload "Drag
        and Drop" area. Optional.
    text_completed: str
        The text to show in the upload area 
        after upload has completed succesfully before
        the name of the uploaded file. For example, if user
        uploaded "data.zip" and `text_completed` is 
        "Ready! ", then user would see text "Ready! 
        data.zip".
    cancel_button: bool
        If True, shows a cancel button.
    pause_button: bool
        If True, shows a pause button.
    filetypes: list of str or None
        The filetypes that can be uploaded. 
        For example ['zip', 'rar'].
        Note that this just checks the extension of the 
        filename, and user might still upload any kind 
        of file (by renaming)!
        By default, all filetypes are accepted.
    max_file_size: numeric
        The maximum file size in Megabytes. Optional.
    css_id: str
        The CSS id for the component. Optional.
    default_style: None or dict
        Inline CSS styling for the main div element. 
        If None, use the default style of the component.
        If dict, will use the union on the given dict
        and the default style. (you may override
        part of the style by giving a dictionary)
        More styling options through the CSS classes.
    Returns
    -------
    Upload: dash component
        Initiated Dash component for app.layout.
    """

    # Handle styling
    if default_style is None:
        default_style = dict(DEFAULT_STYLE)
    else:
        default_style = {**DEFAULT_STYLE, **default_style}

    arguments = dict(
        # Have not tested if using many files
        # is reliable -> Do not allow
        maxFiles=1,
        maxFileSize=max_file_size * 1024 * 1024,
        textLabel=text,
        service='/API/resumable',
        startButton=False,
        # Not tested so default to one.
        simultaneousUploads=1,
        completedMessage=text_completed,
        cancelButton=cancel_button,
        pauseButton=pause_button,
        defaultStyle=default_style,
        activeStyle=default_style,
        completeStyle=default_style,
    )

    if css_id:
        arguments['id'] = css_id
    else:
        arguments['id'] = 'resumable-upload-component'
    if filetypes:
        arguments['filetypes'] = filetypes

    return Upload_ReactComponent(**arguments)
