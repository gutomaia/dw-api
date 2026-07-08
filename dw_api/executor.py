"""Framework-agnostic route execution template for the Downwind API.

The RouteExecutor implements the invariant request pipeline shared by every
web framework adapter (template method pattern):

    1. payload validation (commands / query requests)
    2. handler argument resolution (ResolverRegistry + entrypoint resolvers)
    3. handler invocation
    4. result normalization
    5. translation of raised exceptions into the dw_api error taxonomy

Adapters (dw-api-fastapi, dw-api-awslambda, ...) only register routes,
extract headers from the transport, call the executor and translate ApiError
into their transport-specific response.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from dw_core.core import get_argument_resolvers
from dw_core.cqrs import Command, QueryRequest
from dw_core.resolver import ResolutionContext, ResolverRegistry

from dw_api.exceptions import (
    ApiError,
    BadRequest,
    DependencyNotConfigured,
    InvalidHandlerResult,
    NotFound,
    Unauthorized,
)

ErrorMap = Sequence[tuple[type[Exception], type[ApiError]]]


def route_path(model: type) -> str:
    """Resolve the route path for a Command/Query/QueryRequest model."""
    return getattr(model, '__dw_path__', f'/{model.__name__.lower()}')


class RouteExecutor:
    def __init__(
        self,
        error_map: ErrorMap | None = None,
        resolvers: Sequence[Any] | None = None,
    ):
        self._registry = ResolverRegistry()
        if resolvers is None:
            for _, resolver in get_argument_resolvers():
                self._registry.register(resolver)
        else:
            for resolver in resolvers:
                self._registry.register(resolver)
        self._error_map: list[tuple[type[Exception], type[ApiError]]] = list(
            error_map or []
        )

    def resolve_kwargs(
        self,
        func: Callable[..., Any],
        headers: Mapping[str, str] | None,
        extras: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            return self._registry.resolve_kwargs(
                func,
                ResolutionContext(
                    headers=dict(headers) if headers else None,
                    extras=dict(extras or {}),
                ),
            )
        except PermissionError as e:
            raise Unauthorized() from e
        except Exception as e:
            raise DependencyNotConfigured() from e

    def execute_command(
        self,
        command_cls: type[Command],
        func: Callable[..., Any],
        payload: dict,
        headers: Mapping[str, str] | None,
        extras: dict[str, Any] | None = None,
    ) -> dict:
        command = command_cls.model_validate(payload)
        kwargs = self.resolve_kwargs(func, headers, extras)
        result = self._invoke(func, command, **kwargs)

        if result is None:
            return {}
        if isinstance(result, dict):
            return result
        raise InvalidHandlerResult()

    def execute_query(
        self,
        func: Callable[..., Any],
        headers: Mapping[str, str] | None,
        query_request: type[QueryRequest] | None = None,
        params: Mapping[str, Any] | None = None,
        extras: dict[str, Any] | None = None,
    ) -> Any:
        kwargs = self.resolve_kwargs(func, headers, extras)
        if query_request is None:
            return self._invoke(func, **kwargs)

        payload = query_request.model_validate(dict(params or {}))
        return self._invoke(func, payload, **kwargs)

    def _invoke(self, func: Callable[..., Any], *args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except ApiError:
            raise
        except Exception as e:
            for exc_type, api_error_type in self._error_map:
                if isinstance(e, exc_type):
                    raise api_error_type() from e
            if isinstance(e, KeyError):
                raise NotFound() from e
            if isinstance(e, ValueError):
                raise BadRequest(str(e)) from e
            raise
