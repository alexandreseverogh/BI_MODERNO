# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Purify(Component):
    """A Purify component.
A simple component that displays HTML in a safe way via DOMPurify.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    The class of the component.

- config (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Configuration (optional) of DOMPurify, see the docs
    https://github.com/cure53/DOMPurify.

- html (string; optional):
    Html string."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'Purify'

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        html: typing.Optional[str] = None,
        config: typing.Optional[typing.Dict[typing.Union[str, float, int], typing.Any]] = None,
        className: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'className', 'config', 'html']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'config', 'html']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Purify, self).__init__(**args)
