from types import NoneType
from typing import Callable, Type, Any, get_type_hints, Tuple, Union
from dw_core.cqrs import Command, Query
from dw_core.core import get_ports
from dw_api.ports import EndpointGenerator
import inject


CommandFunctionType = Union[
    Callable[[Command], NoneType], Callable[[Command], None]
]
QueryFunctionType = Callable[[Any], Query]


def filter_command_function(obj: Any) -> Tuple[bool, Type[Command]]:
    if callable(obj):
        hints = get_type_hints(obj)
        params = list(hints.values())
        if (
            len(hints) >= 1
            and issubclass(params[0], Command)
            and (
                hints.get('return') is NoneType or hints.get('return') is None
            )
        ):
            return True, params[0]
    return False, None


def is_command_function(obj: Any) -> bool:
    is_command, _ = filter_command_function(obj)
    return is_command


def filter_query_function(obj: Any) -> Tuple[bool, Type[Query]]:
    if callable(obj):
        hints = get_type_hints(obj)
        return_type = hints.get('return')
        if return_type is not None and issubclass(return_type, Query):
            return True, hints.get('return')
    return False, None


@inject.autoparams('generator')
def auto_generate_endpoint(generator: EndpointGenerator):
    for _, port in get_ports():
        is_command, command = filter_command_function(port)
        if is_command:
            generator.generate_command_route(command, port)
            continue
        else:
            is_query, query = filter_query_function(port)
            if is_query:
                generator.generate_query_route(query, port)
                continue

    return generator.get_app()
