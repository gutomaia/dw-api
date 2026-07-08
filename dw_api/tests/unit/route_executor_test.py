from typing import List
from unittest import TestCase
from unittest.mock import patch

from dw_core.cqrs import Command, Query, QueryRequest

from dw_api.exceptions import (
    BadRequest,
    DependencyNotConfigured,
    Forbidden,
    InvalidHandlerResult,
    NotFound,
    Unauthorized,
)
from dw_api.executor import RouteExecutor, route_path


class CustomForbidden(Exception):
    pass


class RouteExecutorTest(TestCase):
    def setUp(self):
        self.resolvers = []
        self.get_resolvers_patched = patch(
            'dw_api.executor.get_argument_resolvers',
            wraps=lambda: self.resolvers,
        )
        self.get_resolvers_patched.start()

    def tearDown(self):
        self.get_resolvers_patched.stop()

    def test_route_path_uses_dw_path(self):
        class Ping(Command):
            __dw_path__ = '/custom/ping'

        self.assertEqual(route_path(Ping), '/custom/ping')

    def test_route_path_falls_back_to_lowercase_name(self):
        class Ping(Command):
            pass

        self.assertEqual(route_path(Ping), '/ping')

    def test_execute_command_returns_empty_dict_for_none(self):
        class Echo(Command):
            message: str

        def echo(cmd: Echo) -> None:
            assert cmd.message == 'hi'

        executor = RouteExecutor()
        result = executor.execute_command(Echo, echo, {'message': 'hi'}, {})
        self.assertEqual(result, {})

    def test_execute_command_returns_dict_result(self):
        class Echo(Command):
            message: str

        def echo(cmd: Echo) -> dict:
            return {'echoed': cmd.message}

        executor = RouteExecutor()
        result = executor.execute_command(Echo, echo, {'message': 'hi'}, {})
        self.assertEqual(result, {'echoed': 'hi'})

    def test_execute_command_invalid_result_type(self):
        class Echo(Command):
            message: str

        def echo(cmd: Echo) -> dict:
            return 'not-a-dict'

        executor = RouteExecutor()
        with self.assertRaises(InvalidHandlerResult):
            executor.execute_command(Echo, echo, {'message': 'hi'}, {})

    def test_execute_query_without_request(self):
        class ListUsers(Query):
            users: List[str]

        def get_users() -> ListUsers:
            return ListUsers(users=['root'])

        executor = RouteExecutor()
        result = executor.execute_query(get_users, {})
        self.assertEqual(result.users, ['root'])

    def test_execute_query_with_request(self):
        class WhoAmIRequest(QueryRequest):
            subject: str

        class WhoAmI(Query):
            subject: str

        def whoami(req: WhoAmIRequest) -> WhoAmI:
            return WhoAmI(subject=req.subject)

        executor = RouteExecutor()
        result = executor.execute_query(
            whoami, {}, query_request=WhoAmIRequest, params={'subject': 'u1'}
        )
        self.assertEqual(result.subject, 'u1')

    def test_key_error_maps_to_not_found(self):
        class Echo(Command):
            pass

        def echo(cmd: Echo) -> None:
            raise KeyError('missing')

        executor = RouteExecutor()
        with self.assertRaises(NotFound):
            executor.execute_command(Echo, echo, {}, {})

    def test_value_error_maps_to_bad_request(self):
        class Echo(Command):
            pass

        def echo(cmd: Echo) -> None:
            raise ValueError('invalid data')

        executor = RouteExecutor()
        with self.assertRaises(BadRequest) as ctx:
            executor.execute_command(Echo, echo, {}, {})
        self.assertEqual(str(ctx.exception), 'invalid data')

    def test_custom_error_map(self):
        class Echo(Command):
            pass

        def echo(cmd: Echo) -> None:
            raise CustomForbidden()

        executor = RouteExecutor(error_map=[(CustomForbidden, Forbidden)])
        with self.assertRaises(Forbidden):
            executor.execute_command(Echo, echo, {}, {})

    def test_permission_error_on_resolution_maps_to_unauthorized(self):
        class DenyingResolver:
            def supports(self, arg_type):
                return arg_type is str

            def resolve(self, *, arg_name, arg_type, context, resolved_kwargs):
                raise PermissionError()

        self.resolvers.append(('deny', DenyingResolver()))

        class Echo(Command):
            pass

        def echo(cmd: Echo, subject: str) -> None:
            raise RuntimeError('must not be called')

        executor = RouteExecutor()
        with self.assertRaises(Unauthorized):
            executor.execute_command(Echo, echo, {}, {})

    def test_resolution_failure_maps_to_dependency_not_configured(self):
        class BrokenResolver:
            def supports(self, arg_type):
                return arg_type is str

            def resolve(self, *, arg_name, arg_type, context, resolved_kwargs):
                raise RuntimeError('boom')

        self.resolvers.append(('broken', BrokenResolver()))

        class Echo(Command):
            pass

        def echo(cmd: Echo, subject: str) -> None:
            raise RuntimeError('must not be called')

        executor = RouteExecutor()
        with self.assertRaises(DependencyNotConfigured):
            executor.execute_command(Echo, echo, {}, {})

    def test_explicit_resolvers_are_used(self):
        class SubjectResolver:
            def supports(self, arg_type):
                return arg_type is str

            def resolve(self, *, arg_name, arg_type, context, resolved_kwargs):
                return {arg_name: 'user-1'}

        class Echo(Command):
            pass

        def echo(cmd: Echo, subject: str) -> dict:
            return {'subject': subject}

        executor = RouteExecutor(resolvers=[SubjectResolver()])
        result = executor.execute_command(Echo, echo, {}, {})
        self.assertEqual(result, {'subject': 'user-1'})

    def test_explicit_resolvers_skip_entrypoint_discovery(self):
        class EntrypointResolver:
            def supports(self, arg_type):
                return arg_type is str

            def resolve(self, *, arg_name, arg_type, context, resolved_kwargs):
                raise RuntimeError('must not be used')

        self.resolvers.append(('entrypoint', EntrypointResolver()))

        class Echo(Command):
            pass

        def echo(cmd: Echo) -> None:
            pass

        executor = RouteExecutor(resolvers=[])
        result = executor.execute_command(Echo, echo, {}, {})
        self.assertEqual(result, {})
