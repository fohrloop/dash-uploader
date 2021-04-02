# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Button(Component):
    """A Button component.
A Button component. 
 Used as a part of Upload component.

Keyword arguments:
- text (default ''): The text on the button
- btnClass (default 'dash-uploader-btn'): The CSS class for the button
- onClick (default () => { }): Function to call when clicked
- disabled (default False): Is disabled, the component
is not shown.
- isUploading (default False): Is true, the parent component
 has upload in progress."""
    @_explicitize_args
    def __init__(self, text=Component.UNDEFINED, btnClass=Component.UNDEFINED, onClick=Component.UNDEFINED, disabled=Component.UNDEFINED, isUploading=Component.UNDEFINED, **kwargs):
        self._prop_names = ['text', 'btnClass', 'onClick', 'disabled', 'isUploading']
        self._type = 'Button'
        self._namespace = 'dash_uploader'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['text', 'btnClass', 'onClick', 'disabled', 'isUploading']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Button, self).__init__(**args)
