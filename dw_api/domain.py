"""Domain models for the Downwind API response handling.

This module contains the Pydantic models used for standardizing API responses
in the Downwind framework. These models ensure consistent response formats
across all automatically generated endpoints.
"""

from pydantic import BaseModel, Field


class CommandAccept(BaseModel):   # status code 202
    """Response model for accepted commands that will be processed asynchronously.

    This model is used when a command is accepted but not yet executed,
    typically returning a 202 Accepted status code.
    """

    accepted: bool = Field(
        title='Command Accepted',
        description='Defines the acceptance of the command',
        example='True/False',
    )


class CommandExecuted(BaseModel):   # status code 200
    """Response model for synchronously executed commands.

    This model is used when a command has been executed immediately,
    typically returning a 200 OK status code.
    """

    accepted: bool = Field(
        title='Command Accepted',
        description='Defines the acceptance of the command',
        example='True/False',
    )
