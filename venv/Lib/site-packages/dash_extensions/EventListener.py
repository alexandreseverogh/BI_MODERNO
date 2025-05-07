# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class EventListener(Component):
    """An EventListener component.
A component that listens for events and forwards them to Dash.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component. If any children are provided, the
    component will listen for events from these components. If no
    children are specified, the component will listen for events from
    the document object.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    A custom class name.

- event (dict; optional):
    The latest event fired.

- events (list of dicts; default [    {      event: 'keydown',      props: ['key', 'altKey', 'ctrlKey', 'shiftKey', 'metaKey', 'repeat']    }  ]):
    The event entry specifies which event to listen to, e.g. \"click\"
    for click events. The \"props\" entry specifies what event
    properties to record, e.g. [\"x\", \"y\"] to get the cursor
    position.

    `events` is a list of dicts with keys:

    - event (string; required)

    - props (list of strings; optional)

- logging (boolean; default False):
    If True, event information is logged to the javascript console.

- n_events (number; default 0):
    The number of events fired.

- useCapture (boolean; default False):
    Value of useCapture used when registering event listeners."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'EventListener'
    Events = TypedDict(
        "Events",
            {
            "event": str,
            "props": NotRequired[typing.Sequence[str]]
        }
    )

    @_explicitize_args
    def __init__(
        self,
        children: typing.Optional[typing.Union[str, int, float, ComponentType, typing.Sequence[typing.Union[str, int, float, ComponentType]]]] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        events: typing.Optional[typing.Sequence["Events"]] = None,
        logging: typing.Optional[bool] = None,
        style: typing.Optional[typing.Any] = None,
        className: typing.Optional[str] = None,
        event: typing.Optional[dict] = None,
        n_events: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        useCapture: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'className', 'event', 'events', 'logging', 'n_events', 'style', 'useCapture']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'event', 'events', 'logging', 'n_events', 'style', 'useCapture']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(EventListener, self).__init__(children=children, **args)
