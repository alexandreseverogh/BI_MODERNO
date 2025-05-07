# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class EventSource(Component):
    """An EventSource component.
An interface to server sent events in Dash.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- close (boolean; optional):
    Close event source.

- error (string; optional):
    Error.

- message (string; optional):
    Received message.

- readyState (a value equal to: 0, 1, 2; optional):
    A number representing the state of the connection. Possible values
    are CONNECTING (0), OPEN (1), or CLOSED (2).

- url (string; required):
    A DOMString representing the URL of the source.

- withCredentials (boolean; default False):
    A boolean value indicating whether the EventSource object was
    instantiated with cross-origin (CORS) credentials set (True), or
    not (False, the default)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'EventSource'

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        close: typing.Optional[bool] = None,
        error: typing.Optional[str] = None,
        message: typing.Optional[str] = None,
        readyState: typing.Optional[Literal[0, 1, 2]] = None,
        withCredentials: typing.Optional[bool] = None,
        url: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'close', 'error', 'message', 'readyState', 'url', 'withCredentials']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'close', 'error', 'message', 'readyState', 'url', 'withCredentials']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['url']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(EventSource, self).__init__(**args)
