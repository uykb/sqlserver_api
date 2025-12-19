# SQL Server API & Admin Demo

This project provides a complete solution for instantly generating a RESTful API and a visual Admin interface for your SQL Server database. It is built with **FastAPI**, **SQLAlchemy**, and **SQLAdmin**, and now features enhanced UI/UX capabilities.

## Key Features

*   **Modular API Architecture**: Clean and scalable project structure for managing multiple API endpoints.
*   **Visual Admin Dashboard**: A user-friendly interface to manage your data (`/admin`).
*   **Enhanced UI/UX**: Custom CSS beautification and improved interaction feedback.
*   **Data Export**: One-click **CSV Export** for your data.
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

## 项目结构 (Project Structure)

经过模块化重构，项目结构更加清晰：

*   `main.py`: **入口文件**。只负责组装各个模块，不包含具体业务逻辑。
*   `routers/`: **API 路由文件夹**。所有的 API 业务逻辑都在这里。
    *   `pswd.py`: PSWD 表的 API 接口示例。
*   `schemas.py`: **数据模型 (Pydantic)**。定义 API 的输入/输出数据格式。
*   `models.py`: **数据库模型 (SQLAlchemy)**。定义数据库表结构。
*   `database.py`: 数据库连接配置。

## 如何新增 API (How to Add API)

本项目已采用模块化架构，新增 API 非常简单，只需遵循以下 4 步：

### 第一步：定义数据模型 (schemas.py)
在 `schemas.py` 中定义 API 返回或接收的数据格式（使用 Pydantic）。

```python
# schemas.py
from pydantic import BaseModel

# 定义一个返回给前端的数据结构
class OrderResponse(BaseModel):
    order_id: int
    product_name: str
    price: float
```

### 第二步：定义数据库表 (models.py)
如果这是一张新表，需要在 `models.py` 中定义它（使用 SQLAlchemy）。

```python
# models.py
from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    product = Column(String(50))
    price = Column(Float)
```

### 第三步：编写 API 逻辑 (routers/xxx.py)
在 `routers/` 文件夹下新建一个文件，例如 `order.py`，编写业务逻辑。

```python
# routers/order.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Order
from schemas import OrderResponse

# 定义路由，设置前缀和标签
router = APIRouter(
    prefix="/api/orders",
    tags=["订单管理"]
)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    # 查询数据库
    order = db.query(Order).filter(Order.id == order_id).first()
    return {"order_id": order.id, "product_name": order.product, "price": order.price}
```

### 第四步：注册路由 (main.py)
最后，在 `main.py` 中把写好的路由注册进去。

```python
# main.py
# 1. 导入
from routers import order

# 2. 注册
app.include_router(order.router)
```

**完成！** 重启服务后，您就可以在 `/docs` 文档中看到新接口，并直接调用了。
