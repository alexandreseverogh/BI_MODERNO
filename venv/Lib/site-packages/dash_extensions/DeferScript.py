# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class DeferScript(Component):
    """A DeferScript component.
Used to delay import of js resources until after React had been loaded. Typically used to apply js to dynamic content.

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- src (string; optional):
    Local or external source of the javascript to import."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'DeferScript'

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        src: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'src']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'src']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DeferScript, self).__init__(**args)
