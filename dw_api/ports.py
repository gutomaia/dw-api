"""Core interfaces and types for the Downwind API framework.

This module defines the abstract interfaces and type definitions that form
the foundation of the Downwind API's endpoint generation system. It provides
the contract that must be implemented by specific web framework adapters.
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Callable  # ,Type, List, Union

from dw_core.cqrs import Command, Query

__all__ = ['CommandFunctionType', 'QueryFunctionType']


CommandFunctionType = Callable[[Command], None]
"""Type definition for command handler functions.

These functions take a Command object as input and return None,
as commands modify state but don't return values.
"""

QueryFunctionType = Callable[[Any], Query]
"""Type definition for query handler functions.

These functions take any input parameters and return a Query object,
as queries are used to retrieve data.
"""


class EndpointGenerator(metaclass=ABCMeta):
    """Abstract base class for endpoint generation in different web frameworks.

    This class defines the interface that must be implemented to support
    automatic endpoint generation in a specific web framework (e.g., FastAPI,
    Flask, etc.).
    """

    @abstractmethod
    def generate_command_route(
        self, command: Command, func: CommandFunctionType
    ):
        """Generate a route for handling a command.

        Args:
            command: The Command class to create an endpoint for
            func: The function that handles the command
        """
        pass

    @abstractmethod
    def generate_query_route(self, query: Query, func: QueryFunctionType):
        """Generate a route for handling a query.

        Args:
            query: The Query class to create an endpoint for
            func: The function that handles the query
        """
        pass

    @abstractmethod
    def get_app(self):
        """Retrieve the web application instance.

        Returns:
            The web framework's application instance
        """
        pass
