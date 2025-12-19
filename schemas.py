from pydantic import BaseModel
from datetime import datetime

class PswdResponse(BaseModel):
    USR: str
    NAME: str

class RefreshCustomerResponse(BaseModel):
    message: str
    ps_no: str
    updated_records: int
    timestamp: datetime
