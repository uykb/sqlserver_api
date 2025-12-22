from pydantic import BaseModel
from datetime import datetime

class RefreshCustomerResponse(BaseModel):
    message: str
    ps_no: str
    updated_records: int
    timestamp: datetime
