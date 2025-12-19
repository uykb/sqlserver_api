from pydantic import BaseModel

class PswdResponse(BaseModel):
    USR: int
    NAME: str
