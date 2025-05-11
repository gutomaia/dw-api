==========
Quickstart
==========

This guide will help you get started with using the Downwind API module in your application.

Installation
-----------

.. code-block:: bash

    pip install dw-api

Basic Usage
----------

1. Define Your Commands and Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commands and queries are the core building blocks of your API. Commands modify state while queries retrieve data.

.. code-block:: python

    from dw_core.cqrs import Command, Query
    from pydantic import Field
    from typing import Optional

    class CreateUserCommand(Command):
        username: str = Field(..., description="User's username")
        email: str = Field(..., description="User's email address")
        full_name: Optional[str] = Field(None, description="User's full name")

    class GetUserQuery(Query):
        user_id: str = Field(..., description="ID of the user to retrieve")

2. Implement Handlers
~~~~~~~~~~~~~~~~~~~

Create handler functions for your commands and queries. Command handlers return None, while query handlers return data.

.. code-block:: python

    from typing import Dict
    from your_app.models import User

    def handle_create_user(cmd: CreateUserCommand) -> None:
        # Implementation for creating a user
        user = User(
            username=cmd.username,
            email=cmd.email,
            full_name=cmd.full_name
        )
        user.save()

    def handle_get_user(query: GetUserQuery) -> Dict:
        # Implementation for retrieving a user
        user = User.get_by_id(query.user_id)
        return {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }

3. Create Your Endpoint Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement the EndpointGenerator interface for your web framework. Here's an example using FastAPI:

.. code-block:: python

    from fastapi import FastAPI
    from dw_api.ports import EndpointGenerator, CommandFunctionType, QueryFunctionType
    from dw_core.cqrs import Command, Query
    from dw_api.domain import CommandAccept, CommandExecuted

    class FastAPIEndpointGenerator(EndpointGenerator):
        def __init__(self):
            self.app = FastAPI()

        def generate_command_route(
            self, command: Command, func: CommandFunctionType
        ):
            @self.app.post(f"/commands/{command.__name__}")
            async def handle_command(cmd: command):
                func(cmd)
                return CommandExecuted(accepted=True)

        def generate_query_route(
            self, query: Query, func: QueryFunctionType
        ):
            @self.app.get(f"/queries/{query.__name__}")
            async def handle_query(q: query):
                return func(q)

        def get_app(self):
            return self.app

4. Generate Endpoints
~~~~~~~~~~~~~~~~~~

Use the auto_generate_endpoint function to create your API endpoints:

.. code-block:: python

    from dw_api.endpoint import auto_generate_endpoint

    # Initialize your endpoint generator
    generator = FastAPIEndpointGenerator()

    # Generate endpoints
    auto_generate_endpoint(generator)

    # Get the FastAPI app
    app = generator.get_app()

Advanced Usage Examples
---------------------

Event Handling
~~~~~~~~~~~~

You can also handle events in your application:

.. code-block:: python

    from dw_core.cqrs import Event
    from typing import List

    class UserCreatedEvent(Event):
        user_id: str
        username: str

    def handle_user_created(event: UserCreatedEvent) -> None:
        # Handle the user created event
        notify_admin(f"New user created: {event.username}")

Validation and Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use Pydantic's validation features:

.. code-block:: python

    from pydantic import Field, EmailStr

    class UpdateUserCommand(Command):
        user_id: str
        email: EmailStr = Field(..., description="Must be a valid email")
        age: int = Field(..., gt=0, lt=150, description="User's age")

Questions or Need Help?
--------------------

If you have questions about:

1. How to structure your commands and queries
2. Best practices for handler implementation
3. Framework-specific integration details
4. Advanced usage patterns

Please refer to our detailed documentation or reach out to our community.
