from typing import List

import inject
from dw_core.cqrs import Query, QueryRequest


class ExecuteQuerySpec:
    def given_port(self, port):
        raise NotImplementedError()

    def when_execute_query(
        self,
        path: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
    ):
        raise NotImplementedError()

    def assert_response_has(self, **kwargs):
        raise NotImplementedError()

    def test_execute_query(self):
        class ListUsers(Query):
            users: List[str]

        def get_users() -> ListUsers:
            return ListUsers(users=['root'])

        self.given_port(get_users)

        self.when_execute_query(f'/{ListUsers.__name__.lower()}')

        self.assert_response_has(users__0='root')

    def test_execute_query_with_repository(self):
        class ListCars(Query):
            cars: List[str]

        class CarRepository:
            def get_cars(self):
                return ['charger']

        def get_cars(repository=CarRepository()) -> ListCars:
            return ListCars(cars=repository.get_cars())

        self.given_port(get_cars)

        self.when_execute_query(f'/{ListCars.__name__.lower()}')

        self.assert_response_has(cars__0='charger')

    def test_execute_query_with_dependency_injection_repository(self):
        class ListCars(Query):
            cars: List[str]

        class CarRepository:
            def get_cars(self):
                return ['mustang']

        @inject.autoparams('repository')
        def get_cars(repository: CarRepository) -> ListCars:
            return ListCars(cars=repository.get_cars())

        self.given_port(get_cars)

        self.when_execute_query(f'/{ListCars.__name__.lower()}')

        self.assert_response_has(cars__0='mustang')

    def test_execute_query_with_query_request(self):
        class WhoAmIRequest(QueryRequest):
            __dw_path__ = '/whoami'
            subject: str

        class WhoAmI(Query):
            subject: str

        def whoami(req: WhoAmIRequest) -> WhoAmI:
            return WhoAmI(subject=req.subject)

        self.given_port(whoami)

        self.when_execute_query('/whoami', params={'subject': 'user-2'})

        self.assert_response_has(subject='user-2')
