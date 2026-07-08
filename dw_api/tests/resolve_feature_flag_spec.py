from typing import Annotated, Any, List

from dw_core.cqrs import Command, Query
from dw_featureflag.client import FeatureFlags
from dw_featureflag.domain import FeatureFlag


class ResolveFeatureFlagSpec:
    """Contract spec: feature flags are injected as handler arguments.

    Implementations must wire an endpoint generator (or the RouteExecutor
    directly), a FeatureFlagProvider and the feature flag argument
    resolvers, then implement the hooks below.
    """

    def given_port(self, port):
        raise NotImplementedError()

    def given_feature_flag(
        self,
        flag: FeatureFlag,
        flag_value: Any,
        subject: str | None = None,
    ):
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

    def assert_response_has(self, **kwargs):
        raise NotImplementedError()

    def test_resolve_feature_flag_query(self):
        class ListUsers(Query):
            users: List[str]

        flag = FeatureFlag[bool](key='can_list_users', default=False)
        CanListUsers = Annotated[bool, flag]

        def get_users(can_list_users: CanListUsers) -> ListUsers:
            if not can_list_users:
                return ListUsers(users=[])
            return ListUsers(users=['root'])

        self.given_feature_flag(flag, True)
        self.given_port(get_users)

        self.when_execute_query(f'/{ListUsers.__name__.lower()}')

        self.assert_response_has(users__0='root')

    def test_resolve_feature_flag_query_when_disabled(self):
        class ListUsers(Query):
            users: List[str]

        flag = FeatureFlag[bool](key='can_list_users', default=False)
        CanListUsers = Annotated[bool, flag]

        def get_users(can_list_users: CanListUsers) -> ListUsers:
            if not can_list_users:
                return ListUsers(users=[])
            return ListUsers(users=['root'])

        self.given_port(get_users)

        self.when_execute_query(f'/{ListUsers.__name__.lower()}')

        self.assert_response_has(users=[])

    def test_resolve_feature_flag_command(self):
        class PromoteUser(Command):
            username: str

        flag = FeatureFlag[bool](key='can_promote', default=False)
        CanPromote = Annotated[bool, flag]

        def promote_user(cmd: PromoteUser, can_promote: CanPromote) -> dict:
            return {'username': cmd.username, 'promoted': can_promote}

        self.given_feature_flag(flag, True)
        self.given_port(promote_user)

        self.when_execute_command(
            f'/{PromoteUser.__name__.lower()}',
            payload={'username': 'root'},
        )

        self.assert_response_has(username='root', promoted=True)

    def test_resolve_feature_flag_command_when_disabled(self):
        class PromoteUser(Command):
            username: str

        flag = FeatureFlag[bool](key='can_promote', default=False)
        CanPromote = Annotated[bool, flag]

        def promote_user(cmd: PromoteUser, can_promote: CanPromote) -> dict:
            return {'username': cmd.username, 'promoted': can_promote}

        self.given_port(promote_user)

        self.when_execute_command(
            f'/{PromoteUser.__name__.lower()}',
            payload={'username': 'root'},
        )

        self.assert_response_has(username='root', promoted=False)

    def test_resolve_non_bool_feature_flag(self):
        class RankingConfig(Query):
            algorithm: str

        flag = FeatureFlag[str](key='ranking_algorithm', default='rank-v1')
        RankingAlgorithm = Annotated[str, flag]

        def get_ranking_config(algorithm: RankingAlgorithm) -> RankingConfig:
            return RankingConfig(algorithm=algorithm)

        self.given_feature_flag(flag, 'rank-v2')
        self.given_port(get_ranking_config)

        self.when_execute_query(f'/{RankingConfig.__name__.lower()}')

        self.assert_response_has(algorithm='rank-v2')

    def test_resolve_non_bool_feature_flag_default(self):
        class RankingConfig(Query):
            algorithm: str

        flag = FeatureFlag[str](key='ranking_algorithm', default='rank-v1')
        RankingAlgorithm = Annotated[str, flag]

        def get_ranking_config(algorithm: RankingAlgorithm) -> RankingConfig:
            return RankingConfig(algorithm=algorithm)

        self.given_port(get_ranking_config)

        self.when_execute_query(f'/{RankingConfig.__name__.lower()}')

        self.assert_response_has(algorithm='rank-v1')

    def test_resolve_multiple_feature_flags(self):
        class ListUsers(Query):
            users: List[str]
            algorithm: str

        can_list = FeatureFlag[bool](key='can_list_users', default=False)
        ranking = FeatureFlag[str](key='ranking_algorithm', default='rank-v1')
        CanListUsers = Annotated[bool, can_list]
        RankingAlgorithm = Annotated[str, ranking]

        def get_users(
            can_list_users: CanListUsers,
            algorithm: RankingAlgorithm,
        ) -> ListUsers:
            users = ['root'] if can_list_users else []
            return ListUsers(users=users, algorithm=algorithm)

        self.given_feature_flag(can_list, True)
        self.given_port(get_users)

        self.when_execute_query(f'/{ListUsers.__name__.lower()}')

        self.assert_response_has(users__0='root', algorithm='rank-v1')

    def test_resolve_feature_flags_collection(self):
        class ListUsers(Query):
            users: List[str]

        flag = FeatureFlag[bool](key='can_list_users', default=False)

        def get_users(flags: FeatureFlags) -> ListUsers:
            if not flags.get(flag):
                return ListUsers(users=[])
            return ListUsers(users=['root'])

        self.given_feature_flag(flag, True)
        self.given_port(get_users)

        self.when_execute_query(f'/{ListUsers.__name__.lower()}')

        self.assert_response_has(users__0='root')
