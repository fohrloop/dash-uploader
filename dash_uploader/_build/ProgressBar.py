# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ProgressBar(Component):
    """A ProgressBar component.
A ProgressBar component. 
 Used as a part of Upload component.

Keyword arguments:
- progressBar (number; default 0): The progressbar value
- isUploading (boolean; default False): The upload status (boolean)"""
    @_explicitize_args
    def __init__(self, progressBar=Component.UNDEFINED, isUploading=Component.UNDEFINED, **kwargs):
        self._prop_names = ['progressBar', 'isUploading']
        self._type = 'ProgressBar'
        self._namespace = 'dash_uploader'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['progressBar', 'isUploading']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ProgressBar, self).__init__(**args)
