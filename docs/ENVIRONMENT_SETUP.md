# 环境配置指南

## 当前环境配置

- **虚拟机 IP**: 192.168.85.66
- **MySQL**: 192.168.85.66:3306
- **Redis**: 192.168.85.66:6379
- **Elasticsearch**: 192.168.85.66:9200

## 前置要求

### 必需软件
- **Java 21+** - [Download](https://adoptium.net/) (推荐 Temurin)
- **Maven 3.9+** - [Download](https://maven.apache.org/download.cgi)
- **Python 3.12+** (Miniconda) - [Download](https://docs.conda.io/en/latest/miniconda.html)
- **Git** - [Download](https://git-scm.com/downloads)

### 虚拟机服务
- MySQL 8
- Redis 7
- Elasticsearch 8

## 快速启动

### 步骤 1: 创建数据库

在虚拟机 MySQL 中执行：
```bash
mysql -u root -p < java-service/src/main/resources/sql/01-create-database.sql
```

或手动执行：
```sql
CREATE DATABASE IF NOT EXISTS refund_agent
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

### 步骤 2: 启动 Java 服务

```bash
cd java-service
mvn spring-boot:run
```

### 步骤 3: 启动 Python Agent

```bash
cd python-agent
conda create -n refund-agent python=3.12
conda activate refund-agent
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 配置文件说明

### Java Service (`application.yml`)

```yaml
spring:
  datasource:
    url: jdbc:mysql://192.168.85.66:3306/refund_agent
    username: root
    password: ${DB_PASSWORD:root}  # 环境变量或默认值
  data:
    redis:
      host: 192.168.85.66
      port: 6379
```

### Python Agent (`.env`)

```bash
# 复制模板
cp .env.example .env

# 配置虚拟机地址
REDIS_URL=redis://192.168.85.66:6379/0
ELASTICSEARCH_URL=http://192.168.85.66:9200
```

## VSCode 配置

### 推荐扩展

- `Extension Pack for Java` (Microsoft)
- `Python` (Microsoft)
- `Docker` (Microsoft)
- `GitLens` (GitKraken)

### 启动调试

创建 `launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "java",
      "name": "Spring Boot",
      "request": "launch",
      "mainClass": "com.example.aftersale.AftersaleApplication",
      "projectName": "aftersale-service"
    },
    {
      "type": "python",
      "name": "FastAPI",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"]
    }
  ]
}
```

## 验证安装

```bash
# 检查 Java 服务
curl http://localhost:8080/health

# 检查 Python Agent
curl http://localhost:8000/health

# 检查虚拟机服务连通性
ping 192.168.85.66
```

## 常见问题

### 1. 无法连接虚拟机 MySQL

检查虚拟机防火墙和 MySQL 配置：
```bash
# 虚拟机上检查 MySQL 是否允许远程连接
sudo ufw allow 3306
# 或修改 MySQL 配置 bind-address = 0.0.0.0
```

### 2. Maven 依赖下载慢

使用阿里云镜像，在 `~/.m2/settings.xml` 中配置：
```xml
<mirrors>
  <mirror>
    <id>aliyun</id>
    <url>https://maven.aliyun.com/repository/public</url>
    <mirrorOf>central</mirrorOf>
  </mirror>
</mirrors>
```

### 3. Python 包安装失败

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
```

### 4. JDK 版本不对

确保使用 Java 21：
```bash
java -version  # 应显示 21.x.x
```

如有多版本，设置 `JAVA_HOME` 环境变量。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DB_PASSWORD` | MySQL 密码 | `root` |
| `JWT_SECRET` | JWT 密钥 | 需自行设置 |
| `OPENAI_API_KEY` | OpenAI API 密钥 | 需自行设置 |