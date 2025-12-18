import os
from fastapi import FastAPI
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Import from our modules
from database import engine, get_db
from models import User, Item, Base

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

# --- 3. Setup Visual Admin Interface (SQLAdmin) ---

admin = Admin(
    app, 
    engine, 
    authentication_backend=authentication_backend,
    title="Dashboard"
)

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.is_active, User.created_at]
    column_searchable_list = [User.username, User.email]
    column_filters = [User.is_active, User.created_at]
    icon = "fa-solid fa-user"
    name = "User"
    name_plural = "Users"

class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id, Item.title, Item.owner_id]
    column_searchable_list = [Item.title]
    column_filters = [Item.owner_id]
    icon = "fa-solid fa-box"
    name = "Item"
    name_plural = "Items"

admin.add_view(UserAdmin)
admin.add_view(ItemAdmin)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the SQL Server API & Admin Demo!",
        "docs_url": "/docs",
        "admin_url": "/admin"
    }