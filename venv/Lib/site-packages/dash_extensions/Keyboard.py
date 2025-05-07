# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Keyboard(Component):
    """A Keyboard component.
A component that listens for keyboard events and forwards them to Dash.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component. If any children are provided, the
    component will listen for events from these components. If no
    children are specified, the component will listen for events from
    the document object.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- captureKeys (list of string | dict with strings as keys and values of type boolean | number | string | dict | lists; optional):
    The keys to capture. Defaults to all keys. Can be either a string
    (e.g. \"Enter\") or an object (e.g. {key: 'Enter', ctrlKey:
    True}).

- className (string; optional):
    A custom class name.

- eventProps (list of strings; default ["key", "altKey", "ctrlKey", "shiftKey", "metaKey", "repeat"]):
    The event properties to forward to Dash, see
    https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent.

- keydown (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    The result of the key down event.

- keys_pressed (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    A dict of objects like keydown for all keys currently pressed.

- keyup (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    The result of the key up event.

- n_keydowns (number; default 0):
    A counter, which is incremented on each key down event.

- n_keyups (number; default 0):
    A counter, which is incremented on each key up event.

- useCapture (boolean; default False):
    Value of useCapture used when registering event listeners."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'Keyboard'

    @_explicitize_args
    def __init__(
        self,
        children: typing.Optional[typing.Union[str, int, float, ComponentType, typing.Sequence[typing.Union[str, int, float, ComponentType]]]] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        style: typing.Optional[typing.Any] = None,
        className: typing.Optional[str] = None,
        eventProps: typing.Optional[typing.Sequence[str]] = None,
        captureKeys: typing.Optional[typing.Sequence[typing.Union[str, typing.Dict[typing.Union[str, float, int], typing.Any]]]] = None,
        keydown: typing.Optional[typing.Dict[typing.Union[str, float, int], typing.Any]] = None,
        keyup: typing.Optional[typing.Dict[typing.Union[str, float, int], typing.Any]] = None,
        keys_pressed: typing.Optional[typing.Dict[typing.Union[str, float, int], typing.Any]] = None,
        n_keydowns: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        n_keyups: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        useCapture: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'captureKeys', 'className', 'eventProps', 'keydown', 'keys_pressed', 'keyup', 'n_keydowns', 'n_keyups', 'style', 'useCapture']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'captureKeys', 'className', 'eventProps', 'keydown', 'keys_pressed', 'keyup', 'n_keydowns', 'n_keyups', 'style', 'useCapture']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Keyboard, self).__init__(children=children, **args)
