============
Architecture
============

Overview
--------

The Downwind API module is designed as a framework-agnostic layer that automatically generates API endpoints based on CQRS principles. It serves as the interface layer of the Downwind framework, bridging the gap between your domain logic and HTTP endpoints.

Core Design Principles
----------------------

CQRS Integration
~~~~~~~~~~~~~~~~

* Strict separation between commands (write operations) and queries (read operations)
* Commands return void/None as they modify state
* Queries return data but don't modify state

Framework Agnosticism
~~~~~~~~~~~~~~~~~~~~~

* Abstract ``EndpointGenerator`` interface allows integration with any web framework
* Framework-specific implementations handle the actual route generation
* Clean separation between core logic and framework-specific code

Type Safety
~~~~~~~~~~~

* Extensive use of Python's type hints
* Automatic validation through Pydantic models
* Type-based routing and endpoint generation

Component Architecture
----------------------

Domain Layer (``domain.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains response models for standardized API responses:

.. code-block:: python

    class CommandAccept(BaseModel):
        """Response model for accepted commands."""
        accepted: bool

    class CommandExecuted(BaseModel):
        """Response model for executed commands."""
        accepted: bool

Port Layer (``ports.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~

Defines the core interfaces and types:

.. code-block:: python

    class EndpointGenerator(metaclass=ABCMeta):
        @abstractmethod
        def generate_command_route(
            self, command: Command, func: CommandFunctionType
        ):
            pass

        @abstractmethod
        def generate_query_route(
            self, query: Query, func: QueryFunctionType
        ):
            pass

Endpoint Generation (``endpoint.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implements the automatic endpoint generation logic:

.. code-block:: python

    @inject.autoparams('generator')
    def auto_generate_endpoint(generator: EndpointGenerator):
        """Generate endpoints for all command and query handlers."""
        for _, port in get_ports():
            is_command, command = filter_command_function(port)
            if is_command:
                generator.generate_command_route(command, port)

Flow of Operation
-----------------

1. Handler Registration
~~~~~~~~~~~~~~~~~~~~~~~

* Command and query handlers are defined in the application
* Handlers are registered through the Downwind core system

2. Endpoint Generation
~~~~~~~~~~~~~~~~~~~~~~

* ``auto_generate_endpoint`` scans registered handlers
* Validates handler signatures through type inspection
* Calls appropriate generator methods based on handler type

3. Request Handling
~~~~~~~~~~~~~~~~~~~

* Incoming requests are routed to generated endpoints
* Request data is validated against command/query models
* Handlers are invoked with validated data
* Responses are formatted according to standard models

Integration Points
------------------

Framework Integration
~~~~~~~~~~~~~~~~~~~~~

To integrate with a new web framework:

1. Implement the ``EndpointGenerator`` interface
2. Provide framework-specific route generation logic
3. Handle request/response conversion

Application Integration
~~~~~~~~~~~~~~~~~~~~~~~

1. Define command and query classes
2. Implement handler functions
3. Register handlers with Downwind core
4. Initialize appropriate endpoint generator
5. Call ``auto_generate_endpoint``
