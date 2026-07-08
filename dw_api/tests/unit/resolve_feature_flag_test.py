from typing import Any
from unittest import TestCase

import inject
from dw_core.cqrs import Command
from dw_featureflag.domain import FeatureFlag
from dw_featureflag.ports import FeatureFlagProvider
from dw_featureflag.resolver import (
    FeatureFlagsArgumentResolver,
    FeatureFlagValueArgumentResolver,
)
from dw_featureflag.tests.inmemory_provider import InMemoryFeatureFlagProvider

from dw_api.endpoint import filter_command_function, filter_query_function
from dw_api.executor import RouteExecutor, route_path
from dw_api.tests.resolve_feature_flag_spec import ResolveFeatureFlagSpec


class ResolveFeatureFlagRouteExecutorTest(ResolveFeatureFlagSpec, TestCase):
    def setUp(self) -> None:
        self.ports = []
        self.provider = InMemoryFeatureFlagProvider()

        inject.configure(
            lambda binder: binder.bind(FeatureFlagProvider, self.provider),
            clear=True,
        )

        self.executor = RouteExecutor(
            resolvers=[
                FeatureFlagValueArgumentResolver(),
                FeatureFlagsArgumentResolver(),
            ]
        )

    def tearDown(self) -> None:
        inject.clear()

    def given_port(self, port):
        self.ports.append(port)

    def given_feature_flag(
        self,
        flag: FeatureFlag,
        flag_value: Any,
        subject: str | None = None,
    ):
        self.provider.set_override(subject, flag, flag_value)

    def _find_command_port(self, path: str) -> tuple[type[Command], Any]:
        for port in self.ports:
            is_command, command = filter_command_function(port)
            if is_command and route_path(command) == path:
                return command, port
        raise AssertionError(f'No command port registered for path: {path}')

    def _find_query_port(self, path: str) -> tuple[Any, Any]:
        for port in self.ports:
            is_command, _ = filter_command_function(port)
            if is_command:
                continue
            is_query, query_request, query = filter_query_function(port)
            if is_query and route_path(query_request or query) == path:
                return port, query_request
        raise AssertionError(f'No query port registered for path: {path}')

    def when_execute_query(
        self,
        path: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
    ):
        func, query_request = self._find_query_port(path)
        result = self.executor.execute_query(
            func,
            headers,
            query_request=query_request,
            params=params,
        )
        self.response_json = result.model_dump(mode='json')

    def when_execute_command(
        self,
        path: str,
        *,
        payload: dict | None = None,
        headers: dict | None = None,
    ):
        command, func = self._find_command_port(path)
        self.response_json = self.executor.execute_command(
            command, func, payload or {}, headers
        )

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
