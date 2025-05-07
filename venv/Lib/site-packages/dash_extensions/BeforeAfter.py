# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class BeforeAfter(Component):
    """A BeforeAfter component.
BeforeAfter — A before‑and‑after image slider built on img-comparison-slider.
*

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- after (dict; optional):
    Props for the `after` Img component. eg {\"src\":
    \"/assets/lena_color.png\"}.

- before (dict; optional):
    Props for the `before` Img component. eg {\"src\":
    \"/assets/lena_bw.png\"}.

- direction (a value equal to: 'horizontal', 'vertical'; optional):
    Set slider direction.

- height (string; optional):
    Image height — default \"auto\" for responsive images.

- hover (boolean; optional):
    Automatic slide on mouse over.

- keyboard (a value equal to: 'enabled', 'disabled'; optional):
    Enable/disable slider position control with the keyboard.

- value (number; optional):
    The divider position can be specified as a percentage, i.e. 0 to
    100.

- width (string; optional):
    Image width — default \"100%\" for responsive images."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'BeforeAfter'

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        height: typing.Optional[str] = None,
        width: typing.Optional[str] = None,
        hover: typing.Optional[bool] = None,
        value: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        direction: typing.Optional[Literal["horizontal", "vertical"]] = None,
        keyboard: typing.Optional[Literal["enabled", "disabled"]] = None,
        before: typing.Optional[dict] = None,
        after: typing.Optional[dict] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'after', 'before', 'direction', 'height', 'hover', 'keyboard', 'value', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'after', 'before', 'direction', 'height', 'hover', 'keyboard', 'value', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(BeforeAfter, self).__init__(**args)
