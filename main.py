import os
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

# Import from our modules
from database import engine
from models import Base, Pswd
from routers import pswd

# --- Configuration ---
ADMIN_USERNAME = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-me")

# --- Database Initialization ---
# Create tables in SQLite (since we are local now)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to database to create tables. Error: {e}")

app = FastAPI(title="SQL Server API & Admin Demo (Modularized)")

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

# --- Register Routers (Modularized API) ---
app.include_router(pswd.router)

@app.get("/")
def read_root():
    return {
        "message": "欢迎使用模块化后的 API 系统！数据已切换为本地 SQLite。",
        "docs_url": "/docs",
        "admin_url": "/admin"
    }

# --- Setup Visual Admin Interface (SQLAdmin) ---
admin = Admin(
    app, 
    engine, 
    authentication_backend=authentication_backend,
    title="Dashboard",
    templates_dir="templates"
)

class PswdAdmin(ModelView, model=Pswd):
    column_list = [Pswd.USR, Pswd.NAME]
    column_searchable_list = [Pswd.NAME]
    column_labels = {
        Pswd.USR: "用户ID",
        Pswd.NAME: "用户名称",
    }
    icon = "fa-solid fa-key"
    name = "密码表"
    name_plural = "密码表管理"

admin.add_view(PswdAdmin)
