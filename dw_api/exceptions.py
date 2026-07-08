"""Framework-agnostic API error taxonomy for the Downwind API framework.

These exceptions are raised by the RouteExecutor template and translated by
each web framework adapter (FastAPI, AWS Lambda, ...) into the appropriate
transport response. This keeps status-code semantics defined once, in dw-api.
"""


class ApiError(Exception):
    status_code = 500
    default_detail = 'Internal error'

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class BadRequest(ApiError):
    status_code = 400
    default_detail = 'Bad request'


class Unauthorized(ApiError):
    status_code = 401
    default_detail = 'Unauthorized'


class Forbidden(ApiError):
    status_code = 403
    default_detail = 'Forbidden'


class NotFound(ApiError):
    status_code = 404
    default_detail = 'Not found'


class DependencyNotConfigured(ApiError):
    status_code = 500
    default_detail = 'Dependency not configured'


class InvalidHandlerResult(ApiError):
    status_code = 500
    default_detail = 'Command handler returned invalid type'
