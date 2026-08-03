from dw_auth.domain import AuthenticatedPrincipal
from dw_core.cqrs import Command, Query
from dw_settings.domain import AdminSettings, UserSettings


class BoardSettings(UserSettings):
    board: str = 'v10-double'
    weight: int = 12


class RankingSettings(AdminSettings):
    algorithm: str = 'rank-v1'
    window_days: int = 30


class ResolveSettingsSpec:
    """Contract spec: settings instances are injected as handler arguments.

    Implementations must wire an endpoint generator (or the RouteExecutor
    directly), a SettingsProvider, an Authenticator and the principal +
    settings argument resolvers, then implement the hooks below.

    Requests are authenticated as 'user-1' by default.
    """

    def given_port(self, port):
        raise NotImplementedError()

    def given_user_settings(self, subject: str, settings: UserSettings):
        raise NotImplementedError()

    def given_admin_settings(self, settings: AdminSettings):
        raise NotImplementedError()

    def when_execute_query(
        self,
        path: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
    ):
        raise NotImplementedError()

    def when_execute_command(
        self,
        path: str,
        *,
        payload: dict | None = None,
        headers: dict | None = None,
    ):
        raise NotImplementedError()

    def when_execute_query_unauthorized(
        self,
        path: str,
        *,
        params: dict | None = None,
    ):
        """Execute a query as an anonymous caller, expecting a 401."""
        raise NotImplementedError()

    def assert_response_has(self, **kwargs):
        raise NotImplementedError()

    def test_user_settings_injected_into_query(self):
        class MyBoard(Query):
            board: str
            weight: int

        def get_my_board(
            principal: AuthenticatedPrincipal,
            board_settings: BoardSettings,
        ) -> MyBoard:
            return MyBoard(
                board=board_settings.board,
                weight=board_settings.weight,
            )

        self.given_user_settings(
            'user-1', BoardSettings(board='v12', weight=13)
        )
        self.given_port(get_my_board)

        self.when_execute_query(f'/{MyBoard.__name__.lower()}')

        self.assert_response_has(board='v12', weight=13)

    def test_user_settings_defaults_injected_when_not_stored(self):
        class MyBoard(Query):
            board: str
            weight: int

        def get_my_board(
            principal: AuthenticatedPrincipal,
            board_settings: BoardSettings,
        ) -> MyBoard:
            return MyBoard(
                board=board_settings.board,
                weight=board_settings.weight,
            )

        self.given_port(get_my_board)

        self.when_execute_query(f'/{MyBoard.__name__.lower()}')

        self.assert_response_has(board='v10-double', weight=12)

    def test_user_settings_injected_into_command(self):
        class RegisterTraining(Command):
            distance_km: float

        def register_training(
            cmd: RegisterTraining,
            principal: AuthenticatedPrincipal,
            board_settings: BoardSettings,
        ) -> dict:
            return {
                'distance_km': cmd.distance_km,
                'board': board_settings.board,
            }

        self.given_user_settings('user-1', BoardSettings(board='v12'))
        self.given_port(register_training)

        self.when_execute_command(
            f'/{RegisterTraining.__name__.lower()}',
            payload={'distance_km': 10.5},
        )

        self.assert_response_has(distance_km=10.5, board='v12')

    def test_user_settings_are_isolated_by_subject(self):
        class MyBoard(Query):
            board: str
            weight: int

        def get_my_board(
            principal: AuthenticatedPrincipal,
            board_settings: BoardSettings,
        ) -> MyBoard:
            return MyBoard(
                board=board_settings.board,
                weight=board_settings.weight,
            )

        self.given_user_settings('user-2', BoardSettings(board='v14'))
        self.given_port(get_my_board)

        self.when_execute_query(f'/{MyBoard.__name__.lower()}')

        self.assert_response_has(board='v10-double', weight=12)

    def test_admin_settings_injected(self):
        class RankingConfig(Query):
            algorithm: str
            window_days: int

        def get_ranking_config(
            ranking_settings: RankingSettings,
        ) -> RankingConfig:
            return RankingConfig(
                algorithm=ranking_settings.algorithm,
                window_days=ranking_settings.window_days,
            )

        self.given_admin_settings(
            RankingSettings(algorithm='rank-v2', window_days=7)
        )
        self.given_port(get_ranking_config)

        self.when_execute_query(f'/{RankingConfig.__name__.lower()}')

        self.assert_response_has(algorithm='rank-v2', window_days=7)

    def test_admin_settings_defaults_injected_when_not_stored(self):
        class RankingConfig(Query):
            algorithm: str
            window_days: int

        def get_ranking_config(
            ranking_settings: RankingSettings,
        ) -> RankingConfig:
            return RankingConfig(
                algorithm=ranking_settings.algorithm,
                window_days=ranking_settings.window_days,
            )

        self.given_port(get_ranking_config)

        self.when_execute_query(f'/{RankingConfig.__name__.lower()}')

        self.assert_response_has(algorithm='rank-v1', window_days=30)

    def test_user_settings_require_authentication(self):
        class MyBoard(Query):
            board: str

        def get_my_board(board_settings: BoardSettings) -> MyBoard:
            return MyBoard(board=board_settings.board)

        self.given_port(get_my_board)

        self.when_execute_query_unauthorized(f'/{MyBoard.__name__.lower()}')
