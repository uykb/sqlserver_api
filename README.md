# SQL Server API & Admin Demo

This project demonstrates how to automatically generate a RESTful API and a visual Admin interface for an existing SQL Server database using FastAPI, SQLAlchemy, and SQLAdmin.

## Prerequisites

1.  **SQL Server**: Ensure you have access to a SQL Server instance.
2.  **ODBC Driver**: Install the Microsoft ODBC Driver for SQL Server (e.g., `msodbcsql17` or `msodbcsql18`) on your system.

## Installation

1.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Workflow

### 1. Generate Models (`sqlacodegen`)

Instead of writing SQLAlchemy models manually, you can reverse-engineer them from your existing SQL Server database.

Run the following command (adjust connection string as needed):

```bash
# General format
sqlacodegen "mssql+pyodbc://<username>:<password>@<host>/<database>?driver=ODBC+Driver+17+for+SQL+Server" > models.py

# Example
sqlacodegen "mssql+pyodbc://sa:YourStrongPassword123@localhost/MyDatabase?driver=ODBC+Driver+17+for+SQL+Server" > models.py
```

*Note: The `models.py` included in this demo is a simulation of what this command would output.*

### 2. Configure Database Connection

Open `database.py` and update the `SERVER`, `DATABASE`, `USERNAME`, and `PASSWORD` constants with your actual SQL Server credentials.

### 3. Run the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

## Features

1.  **RESTful API (`fastapi-crudrouter`)**:
    *   Visit `http://localhost:8000/docs` to see the automatically generated Swagger UI.
    *   You will see standard CRUD endpoints for your tables (e.g., `/users`, `/items`).

2.  **Visual Admin Interface (`sqladmin`)**:
    *   Visit `http://localhost:8000/admin` to access the management dashboard.
    *   You can view, create, edit, and delete records with a user-friendly UI.
