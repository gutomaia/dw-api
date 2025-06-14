from typing import List

import inject
from dw_core.cqrs import Command, Event, Query


class GenerateEndpointSpec:
    def given_command(self, _class):
        raise NotImplementedError()

    def given_port(self, port):
        raise NotImplementedError()

    def given_registered_command(self, func, class_):
        raise NotImplementedError()

    def when_call(self, instance):
        raise NotImplementedError()

    def when_auto_generate_endpoints(self):
        raise NotImplementedError()

    def assert_endpoints_length(self, size):
        raise NotImplementedError()

    def assert_result_code(self, code):
        raise NotImplementedError()

    def assert_command_called(self, command):
        raise NotImplementedError()

    def test_generate_command(self):
        class Echo(Command):
            message: str

        def echo(msg: Echo) -> None:
            pass

        self.given_port(echo)

        self.when_auto_generate_endpoints()

        self.assert_endpoints_length(1)

    def test_generate_two_commands(self):
        class One(Command):
            first: bool

        class Two(Command):
            second: bool

        def one(n: One) -> None:
            pass

        def two(n: Two) -> None:
            pass

        self.given_port(one)
        self.given_port(two)

        self.when_auto_generate_endpoints()

        self.assert_endpoints_length(2)

    def test_call_command(self):
        class Echo(Command):
            message: str

        def echo(msg: Echo) -> None:
            print(msg.message)

        self.given_port(echo)

        self.when_auto_generate_endpoints()
        self.when_call(Echo(message='Hello World'))

        self.assert_result_code(200)

    def test_command_called(self):
        class Called(Command):
            is_called: bool

        def call(cmd: Called) -> None:
            assert cmd.is_called

        self.given_port(call)

        self.when_auto_generate_endpoints()
        self.when_call(Called(is_called=True))

        self.assert_command_called(call)

    def test_command_with_return_filtered(self):
        class WithoutNoneReturn(Command):
            nodetheless: bool

        def noreturn(cmd: WithoutNoneReturn):
            pass

        self.given_port(noreturn)

        self.when_auto_generate_endpoints()

        self.assert_endpoints_length(1)

    def test_generate_query(self):
        class ListUsers(Query):
            users: List[str]

        def get_users() -> ListUsers:
            return ListUsers(users=['root'])

        self.given_port(get_users)

        self.when_auto_generate_endpoints()

        self.assert_endpoints_length(1)

    def test_generate_query_with_repository(self):
        class ListCars(Query):
            cars: List[str]

        class CarRepository:
            def get_cars(self):
                return ['mustang']

        def get_cars(repository=CarRepository()) -> ListCars:
            return repository.get_cars()

        self.given_port(get_cars)

        self.when_auto_generate_endpoints()

        self.assert_endpoints_length(1)

    def test_generate_query_with_dependency_injection_repository(self):
        class ListCars(Query):
            cars: List[str]

        class CarRepository:
            def get_cars(self):
                return ['mustang']

        @inject.autoparams('repository')
        def get_cars(repository: CarRepository) -> ListCars:
            return repository.get_cars()

        self.given_port(get_cars)

        self.when_auto_generate_endpoints()

        self.assert_endpoints_length(1)

    def test_generate_with_event_handler(self):
        class Notification(Event):
            message: str

        def notify(notification: Notification):
            pass

        self.given_port(notify)

        self.when_auto_generate_endpoints()

        self.assert_endpoints_length(0)

    def test_command_with_repository(self):
        class CreateUser(Command):
            username: str

        class UserRepository:
            pass

        @inject.autoparams('repository')
        def create_user(user: CreateUser, repository: UserRepository):
            pass

        self.given_port(create_user)

        self.when_auto_generate_endpoints()

        self.assert_endpoints_length(1)
