# 安全配置规范

## 绝对不能上传的内容

### 🔴 最高优先级（严禁上传）
- [ ] **API Key**（OpenAI、Langfuse 等）
- [ ] **密码**（数据库、Redis、JWT 密钥）
- [ ] **私钥**（SSH、SSL 证书）
- [ ] **Token**（GitHub、Service Account）

### 🟡 敏感信息（本地配置）
- 虚拟机 IP 地址（192.168.85.66）
- 内部服务地址
- 端口号（非标准端口）

## 配置文件管理

### Java Service

| 文件 | 用途 | Git 状态 |
|------|------|---------|
| `application.yml` | 通用配置模板，使用环境变量占位符 | ✅ 可提交 |
| `application-local.yml` | 本地开发配置（实际地址、密码） | ❌ 已忽略 |
| `.env.example` | 环境变量模板（无实际值） | ✅ 可提交 |
| `.env` | 实际环境变量 | ❌ 已忽略 |

### Python Agent

| 文件 | 用途 | Git 状态 |
|------|------|---------|
| `.env.example` | 环境变量模板（localhost） | ✅ 可提交 |
| `.env` | 实际环境变量（虚拟机地址、API Key） | ❌ 已忽略 |

## 环境变量使用

### Java Service

```bash
# 设置环境变量
set DB_PASSWORD=your-actual-password
set JWT_SECRET=your-actual-secret
set REDIS_HOST=192.168.85.66

# 启动服务
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

### Python Agent

```bash
# 复制模板
cd python-agent
copy .env.example .env

# 编辑 .env 填入实际值
notepad .env

# 启动服务
python -m app.main
```

## 安全检查清单

提交代码前必须检查：

- [ ] `.env` 文件未提交
- [ ] `application-local.yml` 未提交
- [ ] 代码中无硬编码的 API Key
- [ ] 代码中无硬编码的密码
- [ ] `.env.example` 中使用占位符（非实际值）
- [ ] `application.yml` 中使用环境变量占位符

## 检测命令

```bash
# 检查是否有敏感文件被提交
git ls-files | grep -E "\.env$|application-local\.yml"

# 检查历史中是否有 API Key
git log -p | grep -E "sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}"

# 检查当前工作区
git status --ignored
```

## 泄露应急处理

如果发现 API Key 已上传：

1. **立即撤销**该 API Key（在对应平台）
2. **重写 Git 历史**清除敏感信息
3. **强制推送**到 GitHub
4. **生成新的** API Key 并妥善保管

```bash
# 重写历史示例（清除 application.yml 中的敏感信息）
git filter-branch --force --tree-filter '
  if [ -f java-service/src/main/resources/application.yml ]; then
    sed -i "s/192.168.85.66/localhost/g" java-service/src/main/resources/application.yml
  fi
' -- --all

# 强制推送
git push origin master --force
```

## 最佳实践

1. **永远不要**在代码中硬编码任何密钥
2. **永远不要**将 `.env` 文件提交到 Git
3. **永远不要**在日志中打印完整的 API Key
4. **使用**环境变量或密钥管理服务
5. **定期**检查 `.gitignore` 是否完整
6. **定期**轮转 API Key（建议每 90 天）
