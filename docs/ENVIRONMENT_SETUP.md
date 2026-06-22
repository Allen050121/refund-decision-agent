# 环境配置指南

## 前置要求

### 必需软件
- **Java 21+** - [Download](https://www.oracle.com/java/technologies/downloads/)
- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Maven 3.9+** - [Download](https://maven.apache.org/download.cgi)
- **Docker & Docker Compose** - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads)

### 推荐软件
- **IntelliJ IDEA** (Java 开发)
- **PyCharm** (Python 开发)
- **Node.js** (如果需要前端开发)

## IDE 配置

### IntelliJ IDEA 设置

1. **打开项目**
   - File → Open → 选择 `java-service` 目录

2. **配置 Maven**
   - File → Settings → Build, Execution, Deployment → Build Tools → Maven
   - 确保 Maven home directory 正确

3. **配置 JDK**
   - File → Project Structure → Project
   - 设置 SDK 为 Java 21
   - 设置 Language level 为 21

4. **导入 Spring Boot**
   - 等待 Maven 依赖下载完成
   - 运行 `AftersaleApplication.main()`

5. **配置数据库连接**
   - Database → + → Data Source → MySQL
   - Host: localhost, Port: 3306
   - Database: refund_agent
   - User: root, Password: root

### PyCharm 设置

1. **打开项目**
   - File → Open → 选择 `python-agent` 目录

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   ```

3. **选择解释器**
   - File → Settings → Project: python-agent → Python Interpreter
   - 选择 `.venv/bin/python` (Linux/Mac) 或 `.venv\Scripts\python.exe` (Windows)

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **运行应用**
   - 右键 `app/main.py` → Run 'main'
   - 或者使用 uvicorn: `uvicorn app.main:app --reload`

## 快速启动

### 方式一：Docker Compose（推荐）

```bash
# 启动所有基础设施服务
docker-compose up -d mysql redis elasticsearch

# 等待服务就绪后，启动应用服务
docker-compose up -d java-service python-agent
```

### 方式二：本地开发

#### 终端 1 - 启动基础设施
```bash
docker-compose up -d mysql redis elasticsearch
```

#### 终端 2 - 启动 Java 服务
```bash
cd java-service
mvn spring-boot:run
```

#### 终端 3 - 启动 Python Agent
```bash
cd python-agent
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload
```

## 验证安装

### 检查服务状态
```bash
# 健康检查
curl http://localhost:8080/health      # Java Service
curl http://localhost:8000/health      # Python Agent

# 检查 Docker 容器
docker-compose ps
```

### 访问服务
- Java Service API: http://localhost:8080
- Python Agent API: http://localhost:8000
- MySQL: localhost:3306
- Redis: localhost:6379
- Elasticsearch: http://localhost:9200

## 常见问题

### 1. Maven 依赖下载慢
在 `pom.xml` 中添加阿里云镜像：
```xml
<mirrors>
  <mirror>
    <id>aliyun</id>
    <url>https://maven.aliyun.com/repository/public</url>
  </mirror>
</mirrors>
```

### 2. Python 包安装失败
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
```

### 3. Docker 容器启动失败
```bash
# 查看日志
docker-compose logs -f

# 清理并重启
docker-compose down -v
docker-compose up -d
```

### 4. 端口被占用
修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8081:8080"  # 将主机端口改为 8081
```

## 环境变量配置

### Java Service
复制模板文件并修改：
```bash
cp application-template.properties application-local.properties
```

需要配置的敏感信息：
- `spring.datasource.password` - 数据库密码
- `jwt.secret` - JWT 密钥（使用强随机字符串）

### Python Agent
复制模板文件并修改：
```bash
cp .env.example .env
```

需要配置的敏感信息：
- `JAVA_API_TOKEN` - 与 Java 服务通信的 Token
- `OPENAI_API_KEY` - OpenAI API 密钥
- `LANGFUSE_SECRET_KEY` - Langfuse 观测平台密钥（可选）

## 测试运行

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

### API 测试
```bash
# 创建任务
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"userId":"U1001","content":"课程打不开，订单号O20260622001"}'
```
