import os
import csv
import io
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, Body
from fastapi.responses import StreamingResponse
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel

# Import from our modules
from database import engine, get_db
from models import User, Item, Base, Pswd

# --- Configuration ---
ADMIN_USERNAME = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-me")

# --- Database Initialization (Optional) ---
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to database to create tables. Error: {e}")

app = FastAPI(title="SQL Server API & Admin Demo")

# Add Session Middleware for Authentication
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# --- Authentication Backend for SQLAdmin ---
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # Validate credentials against Environment Variables
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session.update({"token": "authenticated"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return bool(token)

authentication_backend = AdminAuth(secret_key=SECRET_KEY)

# --- 1. Pydantic Schemas for API (CRUDRouter) ---

class PswdResponse(BaseModel):
    USR: int
    NAME: str

class UserCreate(BaseModel):
    username: str
    email: str
    hashed_password: str
    is_active: Optional[bool] = True

class UserModel(UserCreate):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    owner_id: int

class ItemModel(ItemCreate):
    id: int
    class Config:
        orm_mode = True

# --- 2. Setup RESTful API (FastAPI-CRUDRouter) ---

user_router = SQLAlchemyCRUDRouter(
    schema=UserModel,
    create_schema=UserCreate,
    db_model=User,
    db=get_db,
    prefix="users",
    tags=["Users"]
)

item_router = SQLAlchemyCRUDRouter(
    schema=ItemModel,
    create_schema=ItemCreate,
    db_model=Item,
    db=get_db,
    prefix="items",
    tags=["Items"]
)

app.include_router(user_router)
app.include_router(item_router)

@app.get("/api/pswd/{user_id}", response_model=PswdResponse, tags=["Custom Queries"])
def get_pswd_name(user_id: int, db: Session = Depends(get_db)):
    """
    根据 USR (ID) 查询 PSWD 表中的用户名 (NAME)
    """
    result = db.query(Pswd).filter(Pswd.USR == user_id).first()
    if not result:
        # 如果未找到，返回 404
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found in PSWD table")
    return {"USR": result.USR, "NAME": result.NAME}

# --- Extra Features: Export & Bulk Delete ---

@app.get("/api/users/export", tags=["Custom Actions"])
def export_users_csv(db: Session = Depends(get_db)):
    users = db.query(User).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "username", "email", "is_active", "created_at"])
    for user in users:
        writer.writerow([user.id, user.username, user.email, user.is_active, user.created_at])
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )

@app.post("/api/users/bulk_delete", tags=["Custom Actions"])
def bulk_delete_users(ids: List[int] = Body(...), db: Session = Depends(get_db)):
    db.query(User).filter(User.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {"status": "success", "deleted_count": len(ids)}

# --- 3. Setup Visual Admin Interface (SQLAdmin) ---

admin = Admin(
    app, 
    engine, 
    authentication_backend=authentication_backend,
    title="Dashboard",
    templates_dir="templates"
)

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.is_active, User.created_at]
    column_searchable_list = [User.username, User.email]
    column_filters = [User.is_active, User.created_at]
    column_labels = {
        User.id: "ID",
        User.username: "用户名",
        User.email: "电子邮箱",
        User.is_active: "激活状态",
        User.created_at: "创建时间",
    }
    icon = "fa-solid fa-user"
    name = "用户"
    name_plural = "用户管理"

class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id, Item.title, Item.owner_id]
    column_searchable_list = [Item.title]
    column_filters = [Item.owner_id]
    column_labels = {
        Item.id: "ID",
        Item.title: "物品名称",
        Item.owner_id: "所属用户ID",
    }
    icon = "fa-solid fa-box"
    name = "物品"
    name_plural = "物品管理"

admin.add_view(UserAdmin)
admin.add_view(ItemAdmin)

@app.get("/")
def read_root():
    return {
        "message": "欢迎使用 SQL Server API & 后台管理演示系统！",
        "docs_url": "/docs",
        "admin_url": "/admin"
    }