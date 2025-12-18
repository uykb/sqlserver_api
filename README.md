# SQL Server API & Admin Demo

This project provides a complete solution for instantly generating a RESTful API and a visual Admin interface for your SQL Server database. It is built with **FastAPI**, **SQLAlchemy**, and **SQLAdmin**, and now features enhanced UI/UX capabilities.

## Key Features

*   **RESTful API**: Automatically generated CRUD endpoints (Create, Read, Update, Delete) for your database tables.
*   **Visual Admin Dashboard**: A user-friendly interface to manage your data (`/admin`).
*   **Enhanced UI/UX**: Custom CSS beautification and improved interaction feedback (loading spinners, confirmation dialogs).
*   **Data Export**: One-click **CSV Export** for your data.
*   **Bulk Operations**: Support for **Bulk Delete** with multi-row selection.
*   **Authentication**: Built-in session-based authentication for the Admin panel.
*   **Docker Ready**: Fully containerized and automated builds via GitHub Actions.

## Quick Start (Docker)

The easiest way to run the application is using the pre-built Docker image from GitHub Container Registry.

### 1. Pull the Image
```bash
docker pull ghcr.io/uykb/sqlserver_api:latest
```

### 2. Run the Container
You need to provide your database credentials via environment variables.

```bash
docker run -d -p 8000:8000 \
  -e DB_SERVER="your_sql_server_host" \
  -e DB_NAME="your_database_name" \
  -e DB_USER="your_username" \
  -e DB_PASSWORD="your_password" \
  -e ADMIN_USER="admin" \
  -e ADMIN_PASSWORD="secure_password" \
  -e SECRET_KEY="random_secret_string" \
  ghcr.io/uykb/sqlserver_api:latest
```

*Note: Ensure your SQL Server is accessible from within the container. If using a local SQL Server on the host machine, use `host.docker.internal` (Windows/Mac) or your host's local IP (Linux) as the `DB_SERVER`.*

## Local Development

### 1. Installation
Cloning the repository and installing dependencies:

```bash
git clone https://github.com/uykb/sqlserver_api.git
cd sqlserver_api
pip install -r requirements.txt
```

### 2. Configuration (.env)
Create a `.env` file in the root directory (copy from `.env.example` if available) or set these environment variables in your shell:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DB_SERVER` | SQL Server Hostname/IP | `localhost` |
| `DB_NAME` | Database Name | `DemoDB` |
| `DB_USER` | Database Username | `sa` |
| `DB_PASSWORD` | Database Password | *(Required)* |
| `ADMIN_USER` | Admin Panel Username | `admin` |
| `ADMIN_PASSWORD` | Admin Panel Password | `admin123` |
| `SECRET_KEY` | Session Encryption Key | `super-secret...` |

### 3. Database Models
The project includes sample `User` and `Item` models in `models.py`. To use your own existing database schema, you can reverse-engineer the models:

```bash
pip install sqlacodegen
sqlacodegen "mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server" > models.py
```

### 4. Run the Server
```bash
uvicorn main:app --reload
```

*   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Admin Panel**: [http://localhost:8000/admin](http://localhost:8000/admin)

## Project Structure

*   `main.py`: Application entry point, API routing, and Admin configuration.
*   `models.py`: SQLAlchemy ORM models (table definitions).
*   `database.py`: Database connection and session management.
*   `templates/custom_list.html`: Custom template overriding default SQLAdmin list view for styles and JS logic.
*   `.github/workflows`: CI/CD configuration for automatic Docker builds.
