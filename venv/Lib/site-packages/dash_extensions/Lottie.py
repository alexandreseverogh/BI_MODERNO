# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Lottie(Component):
    """A Lottie component.
Light wrapper of the lottie-react component for Dash.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- action (a value equal to: 'play', 'pause', 'stop'; optional):
    Actions routed to the Lottie component to control the animation
    state.

- options (dict; optional):
    Options passed to the Lottie animation (see
    https://github.com/Gamote/lottie-react for details).

- speed (number; optional):
    Animation speed. 1 is normal speed (and default).

- url (string; optional):
    If set, data will be downloaded from this URL."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'Lottie'

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        url: typing.Optional[str] = None,
        speed: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        action: typing.Optional[Literal["play", "pause", "stop"]] = None,
        options: typing.Optional[dict] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'action', 'options', 'speed', 'url']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'action', 'options', 'speed', 'url']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Lottie, self).__init__(**args)
