from unittest import TestCase
from unittest.mock import patch

from dw_core.cqrs import Command, Query
from dw_api.tests.generate_endpoint_spec import GenerateEndpointSpec
from dw_api.endpoint import auto_generate_endpoint
import inject
from dw_api.ports import (
    EndpointGenerator,
    CommandFunctionType,
    QueryFunctionType,
)
from dw_api.domain import CommandExecuted
from functools import wraps


class App:
    def __init__(self, routes):
        self.routes = routes

    def __call__(self, command):
        self.routes[command.__class__](command)
        return CommandExecuted(accepted=True)


class FakeEndpointGenerator(EndpointGenerator):
    def __init__(self):
        self.routes = {}

    def generate_command_route(
        self, command: Command, func: CommandFunctionType
    ):
        self.routes[command] = func

    def generate_query_route(self, query: Query, func: QueryFunctionType):
        self.routes['default'] = func

    def get_app(self):
        return App(self.routes)


def spy(func):
    func.is_called = False

    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.is_called = True
        return func(*args, **kwargs)

    return wrapper


class GenerateEndpointTest(GenerateEndpointSpec, TestCase):
    def setUp(self) -> None:
        self.ports = []
        self.get_ports_patched = patch(
            'dw_api.endpoint.get_ports', wraps=self.get_ports
        )
        self.get_ports_mock = self.get_ports_patched.start()
        self.port_spies = {}

    def tearDown(self) -> None:
        self.get_ports_patched.stop()

    def get_ports(self):
        return self.ports

    def given_port(self, port):
        spyed = spy(port)
        self.port_spies[port] = spyed
        self.ports.append(('any', spyed))

    def when_auto_generate_endpoints(self):
        inject.configure(
            lambda binder: binder.bind(
                EndpointGenerator, FakeEndpointGenerator()
            ),
            clear=True,
        )
        self.app = auto_generate_endpoint()

    def when_call(self, instance):
        self.result = self.app(instance)

    def assert_endpoints_length(self, size):
        self.assertEqual(len(self.app.routes), size)

    def assert_result_code(self, code):
        if code == 200:
            self.assertIsInstance(self.result, CommandExecuted)

    def assert_command_called(self, command):
        spyed = self.port_spies[command]
        self.assertTrue(hasattr(spyed, 'is_called'))
        self.assertTrue(spyed.is_called)
