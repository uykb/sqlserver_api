from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Pswd
from schemas import PswdResponse

router = APIRouter(
    prefix="/api/pswd",
    tags=["密码表管理 (PSWD)"]
)

@router.get("/{user_id}", response_model=PswdResponse)
def get_pswd_name(user_id: int, db: Session = Depends(get_db)):
    """
    根据 USR (ID) 查询 PSWD 表中的用户名 (NAME)
    """
    result = db.query(Pswd).filter(Pswd.USR == user_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="User not found in PSWD table")
    return {"USR": result.USR, "NAME": result.NAME}
