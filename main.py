import os
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

# Import from our modules
from database import engine
from models import Base
from routers import refresh_customer

# --- Configuration ---
ADMIN_USERNAME = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-me")

# --- Database Initialization ---
# Create tables if they don't exist
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to database to create tables. Error: {e}")

app = FastAPI(title="SQL Server API & Admin Demo (Modularized)")
templates = Jinja2Templates(directory="templates")

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
app.include_router(refresh_customer.router)

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Setup Visual Admin Interface (SQLAdmin) ---
admin = Admin(
    app, 
    engine, 
    authentication_backend=authentication_backend,
    title="Dashboard"
)


