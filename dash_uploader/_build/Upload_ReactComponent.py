# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Upload_ReactComponent(Component):
    """An Upload_ReactComponent component.


Keyword arguments:
- maxFiles (number; default 1): Maximum number of files that can be uploaded in one session
- maxFileSize (number; default 1024 * 1024 * 10): Maximum size per file in bytes.
- chunkSize (number; default 1024 * 1024): Size of file chunks to send to server.
- simultaneousUploads (number; optional): Number of simultaneous uploads to select
- service (string; default '/API/dash-uploader'): The service to send the files to
- className (string; default 'resumable-default'): Class to add to the upload component by default
- hoveredClass (string; default 'resumable-hovered'): Class to add to the upload component when it is hovered
- disabledClass (string; default 'resumable-disabled'): Class to add to the upload component when it is disabled
- pausedClass (string; default 'resumable-paused'): Class to add to the upload component when it is paused
- completeClass (string; default 'resumable-complete'): Class to add to the upload component when it is complete
- uploadingClass (string; default 'resumable-uploading'): Class to add to the upload component when it is uploading
- defaultStyle (dict; optional): Style attributes to add to the upload component
- uploadingStyle (dict; optional): Style when upload is in progress
- completeStyle (dict; optional): Style when upload is completed (upload finished)
- textLabel (string; default 'Click Here to Select a File'): The string to display in the upload component
- completedMessage (string; default 'Complete! '): Message to display when upload completed
- fileNames (list of strings; optional): The names of the files uploaded
- filetypes (list of strings; default undefined): List of allowed file types, e.g. ['jpg', 'png']
- startButton (boolean; default True): Whether or not to have a start button
- pauseButton (boolean; default True): Whether or not to have a pause button
- cancelButton (boolean; default True): Whether or not to have a cancel button
- disableDragAndDrop (boolean; default False): Whether or not to allow file drag and drop
- id (string; default 'default-dash-uploader-id'): User supplied id of this component
- isCompleted (boolean; default False): The boolean flag telling if upload is completed.
- upload_id (string; default ''): The ID for the upload event (for example, session ID)"""
    @_explicitize_args
    def __init__(self, maxFiles=Component.UNDEFINED, maxFileSize=Component.UNDEFINED, chunkSize=Component.UNDEFINED, simultaneousUploads=Component.UNDEFINED, service=Component.UNDEFINED, className=Component.UNDEFINED, hoveredClass=Component.UNDEFINED, disabledClass=Component.UNDEFINED, pausedClass=Component.UNDEFINED, completeClass=Component.UNDEFINED, uploadingClass=Component.UNDEFINED, defaultStyle=Component.UNDEFINED, uploadingStyle=Component.UNDEFINED, completeStyle=Component.UNDEFINED, textLabel=Component.UNDEFINED, completedMessage=Component.UNDEFINED, fileNames=Component.UNDEFINED, filetypes=Component.UNDEFINED, startButton=Component.UNDEFINED, pauseButton=Component.UNDEFINED, cancelButton=Component.UNDEFINED, disableDragAndDrop=Component.UNDEFINED, id=Component.UNDEFINED, isCompleted=Component.UNDEFINED, upload_id=Component.UNDEFINED, simultaneuosUploads=Component.UNDEFINED, onUploadErrorCallback=Component.UNDEFINED, **kwargs):
        self._prop_names = ['maxFiles', 'maxFileSize', 'chunkSize', 'simultaneousUploads', 'service', 'className', 'hoveredClass', 'disabledClass', 'pausedClass', 'completeClass', 'uploadingClass', 'defaultStyle', 'uploadingStyle', 'completeStyle', 'textLabel', 'completedMessage', 'fileNames', 'filetypes', 'startButton', 'pauseButton', 'cancelButton', 'disableDragAndDrop', 'id', 'isCompleted', 'upload_id']
        self._type = 'Upload_ReactComponent'
        self._namespace = 'dash_uploader'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['maxFiles', 'maxFileSize', 'chunkSize', 'simultaneousUploads', 'service', 'className', 'hoveredClass', 'disabledClass', 'pausedClass', 'completeClass', 'uploadingClass', 'defaultStyle', 'uploadingStyle', 'completeStyle', 'textLabel', 'completedMessage', 'fileNames', 'filetypes', 'startButton', 'pauseButton', 'cancelButton', 'disableDragAndDrop', 'id', 'isCompleted', 'upload_id']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Upload_ReactComponent, self).__init__(**args)
