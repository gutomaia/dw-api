"""Endpoint generation functionality for the Downwind API framework.

This module provides the core functionality for automatically generating API
endpoints from command and query handlers. It uses type inspection to identify
valid handlers and generates appropriate routes through the endpoint generator.
"""

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
    """Identify if an object is a valid command handler function.

    Args:
        obj: The object to inspect

    Returns:
        A tuple of (is_command_handler, command_type) where:
        - is_command_handler: True if the object is a valid command handler
        - command_type: The Command class the handler accepts, or None
    """
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
    """Check if an object is a command handler function.

    Args:
        obj: The object to check

    Returns:
        True if the object is a command handler function
    """
    is_command, _ = filter_command_function(obj)
    return is_command


def filter_query_function(obj: Any) -> Tuple[bool, Type[Query]]:
    """Identify if an object is a valid query handler function.

    Args:
        obj: The object to inspect

    Returns:
        A tuple of (is_query_handler, query_type) where:
        - is_query_handler: True if the object is a valid query handler
        - query_type: The Query class the handler returns, or None
    """
    if callable(obj):
        hints = get_type_hints(obj)
        return_type = hints.get('return')
        if return_type is not None and issubclass(return_type, Query):
            return True, hints.get('return')
    return False, None


@inject.autoparams('generator')
def auto_generate_endpoint(generator: EndpointGenerator):
    """Automatically generate endpoints for all command and query handlers.

    This function scans all registered ports, identifies command and query
    handlers, and generates appropriate API endpoints through the provided
    endpoint generator.

    Args:
        generator: An implementation of EndpointGenerator for the target
                 web framework
    """
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
