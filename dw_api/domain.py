from pydantic import BaseModel, Field


class CommandAccept(BaseModel):   # status code 202
    accepted: bool = Field(
        title='Command Accepted',
        description='Defines the acceptance of the command',
        example='True/False',
    )


class CommandExecuted(BaseModel):   # status code 200
    accepted: bool = Field(
        title='Command Accepted',
        description='Defines the acceptance of the command',
        example='True/False',
    )
