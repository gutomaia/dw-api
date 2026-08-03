from unittest import TestCase

import inject
from dw_auth.domain import AnonymousPrincipal, AuthenticatedPrincipal
from dw_auth.ports import Authenticator
from dw_auth.resolver import PrincipalArgumentResolver
from dw_settings.domain import AdminSettings, UserSettings
from dw_settings.ports import SettingsProvider
from dw_settings.resolver import SettingsArgumentResolver
from dw_settings.tests.inmemory_provider import InMemorySettingsProvider

from dw_api.endpoint import filter_command_function, filter_query_function
from dw_api.exceptions import Unauthorized
from dw_api.executor import RouteExecutor, route_path
from dw_api.tests.resolve_settings_spec import ResolveSettingsSpec


class HeaderAuthenticator(Authenticator):
    def authenticate(self, headers):
        if not headers:
            return AnonymousPrincipal()
        token = headers.get('authorization') or headers.get('Authorization')
        if token:
            return AuthenticatedPrincipal(subject=token, provider='test')
        return AnonymousPrincipal()


class ResolveSettingsRouteExecutorTest(ResolveSettingsSpec, TestCase):
    def setUp(self) -> None:
        self.ports = []
        self.provider = InMemorySettingsProvider()

        inject.configure(
            lambda binder: binder.bind(SettingsProvider, self.provider).bind(
                Authenticator, HeaderAuthenticator()
            ),
            clear=True,
        )

        self.executor = RouteExecutor(
            resolvers=[
                PrincipalArgumentResolver(),
                SettingsArgumentResolver(),
            ]
        )

    def tearDown(self) -> None:
        inject.clear()

    def given_port(self, port):
        self.ports.append(port)

    def given_user_settings(self, subject: str, settings: UserSettings):
        self.provider.set_user_settings(subject, settings)

    def given_admin_settings(self, settings: AdminSettings):
        self.provider.set_admin_settings(settings)

    def _find_command_port(self, path: str):
        for port in self.ports:
            is_command, command = filter_command_function(port)
            if is_command and route_path(command) == path:
                return command, port
        raise AssertionError(f'No command port registered for path: {path}')

    def _find_query_port(self, path: str):
        for port in self.ports:
            is_command, _ = filter_command_function(port)
            if is_command:
                continue
            is_query, query_request, query = filter_query_function(port)
            if is_query and route_path(query_request or query) == path:
                return port, query_request
        raise AssertionError(f'No query port registered for path: {path}')

    def _execute_query(self, path, params, headers):
        func, query_request = self._find_query_port(path)
        return self.executor.execute_query(
            func,
            headers,
            query_request=query_request,
            params=params,
        )

    def when_execute_query(self, path: str, *, params=None, headers=None):
        headers = headers or {'Authorization': 'user-1'}
        result = self._execute_query(path, params, headers)
        self.response_json = result.model_dump(mode='json')

    def when_execute_command(self, path: str, *, payload=None, headers=None):
        headers = headers or {'Authorization': 'user-1'}
        command, func = self._find_command_port(path)
        self.response_json = self.executor.execute_command(
            command, func, payload or {}, headers
        )

    def when_execute_query_unauthorized(self, path: str, *, params=None):
        with self.assertRaises(Unauthorized):
            self._execute_query(path, params, {})

    def assert_response_has(self, **kwargs):
        for key, expected in kwargs.items():
            parts = key.split('__')
            value = self.response_json
            for part in parts:
                if isinstance(value, list):
                    value = value[int(part)]
                else:
                    value = value[part]
            self.assertEqual(value, expected)
