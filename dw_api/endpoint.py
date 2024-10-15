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
        if (hints.get('return') is NoneType and len(hints) == 2) or (
            hints.get('return') is None and len(hints) == 1
        ):
            for param in hints.values():
                if issubclass(param, Command):
                    return True, param
    return False, None


def is_command_function(obj: Any) -> bool:
    is_command, _ = filter_command_function(obj)
    return is_command


def filter_query_function(obj: Any) -> Tuple[bool, Type[Query]]:
    if callable(obj):
        hints = get_type_hints(obj)
        if issubclass(hints.get('return'), Query) and len(hints) == 1:
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
