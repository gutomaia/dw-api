# from types import NoneType
from typing import Any, Callable   # ,Type, List, Union
from dw_core.cqrs import Command, Query
from abc import ABCMeta, abstractmethod


__all__ = ['CommandFunctionType', 'QueryFunctionType']


CommandFunctionType = Callable[[Command], None]
QueryFunctionType = Callable[[Any], Query]


class EndpointGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate_command_route(
        self, command: Command, func: CommandFunctionType
    ):
        pass

    @abstractmethod
    def generate_query_route(self, query: Query, func: QueryFunctionType):
        pass

    @abstractmethod
    def get_app(self):
        pass
