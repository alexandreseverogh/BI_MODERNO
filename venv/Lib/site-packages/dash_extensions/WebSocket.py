# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class WebSocket(Component):
    """A WebSocket component.
A simple interface to the WebSocket API.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- error (boolean | number | string | dict | list; optional):
    This property is set with the content of the onerror event.

- message (boolean | number | string | dict | list; optional):
    When messages are received, this property is updated with the
    message content.

- protocols (list of strings; optional):
    Supported websocket protocols (optional).

- send (boolean | number | string | dict | list; optional):
    When this property is set, a message is sent with its content.

- state (boolean | number | string | dict | list; default { readyState: WebSocket.CLOSED }):
    This websocket state (in the readyState prop) and associated
    information.

- timeout (number; default 1000):
    How many ms to wait for websocket to be ready when sending a
    message (optional).

- url (string; optional):
    The websocket endpoint (e.g. wss://echo.websocket.org)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'WebSocket'

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        state: typing.Optional[typing.Any] = None,
        message: typing.Optional[typing.Any] = None,
        error: typing.Optional[typing.Any] = None,
        send: typing.Optional[typing.Any] = None,
        url: typing.Optional[str] = None,
        protocols: typing.Optional[typing.Sequence[str]] = None,
        timeout: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'error', 'message', 'protocols', 'send', 'state', 'timeout', 'url']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'error', 'message', 'protocols', 'send', 'state', 'timeout', 'url']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(WebSocket, self).__init__(**args)
