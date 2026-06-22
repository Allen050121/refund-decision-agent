# 项目开发文档

## 环境要求

- Java 21+
- Python 3.12+
- Maven 3.9+
- Docker & Docker Compose
- MySQL 8
- Redis 7
- Elasticsearch 8

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd refund-decision-agent
```

### 2. 启动基础设施

```bash
docker-compose up -d mysql redis elasticsearch
```

### 3. 初始化数据库

数据库会自动执行初始化脚本。

### 4. 启动 Java 服务

```bash
cd java-service
mvn spring-boot:run
```

### 5. 启动 Python Agent

```bash
cd python-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API 文档

### Java Service

- `GET /health` - 健康检查
- `POST /api/orders/query` - 查询订单
- `POST /api/learning/query` - 查询学习进度
- `POST /api/courses/status` - 查询课程状态
- `POST /api/refund/check-eligibility` - 退款资格校验

### Python Agent

- `GET /health` - 健康检查
- `POST /tasks` - 创建任务
- `GET /tasks/{task_id}` - 查询任务状态

## 测试

### Java 单元测试

```bash
cd java-service
mvn test
```

### Python 测试

```bash
cd python-agent
pytest
```

## 开发规范

### Java

- 遵循 Spring Boot 最佳实践
- 使用 Lombok 简化代码
- 所有业务规则必须有单元测试

### Python

- 使用 Ruff 进行代码检查
- 使用 mypy 进行类型检查
- Pydantic v2 定义数据模型

## 部署

使用 Docker Compose 部署所有服务：

```bash
docker-compose up -d
```
