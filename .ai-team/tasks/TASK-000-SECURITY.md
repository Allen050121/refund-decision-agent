---
title: "安全配置规范：API Key 与敏感信息管理"
task_id: "TASK-000-SECURITY"
status: "completed"
owner: "backend-engineer"
task_type: "infrastructure"
delivery_stage: "foundation"
mode: "standard"
work_mode: "sequential"
workflow_mode: "standard"
created: "2026-06-24"
dependencies:
verification_status: passed
last_run_id:
last_result:
blocked_reason:
branch:
github_issue:
github_pr:
ci_status:
tags:
  - ai-team/task
  - security
  - infrastructure
  - configuration
---

# Task: 安全配置规范 - API Key 与敏感信息管理

## Status

- Task ID: `TASK-000-SECURITY`
- Owner: `backend-engineer`
- Task Type: `infrastructure`
- Delivery Stage: `foundation`
- Status: `completed`
- Mode: `standard`
- Work Mode: `sequential`
- Workflow Mode: `standard`
- Dependencies: 无
- Verification Status: `passed`
- Last Run:
- Last Result:
- Blocked Reason:
- Branch:
- GitHub Issue:
- GitHub PR:
- CI Status:

## Goal

建立严格的安全配置规范，确保 API Key、密码、虚拟机地址等敏感信息不会被上传到 Git 仓库。

## 问题背景

在项目初始化阶段，虚拟机地址 `192.168.85.66` 被直接写入 `application.yml` 并上传到 Git 历史。虽然这是内网地址，但暴露了基础设施信息。

## 实施措施

### 1. 配置文件分离

| 文件 | 用途 | Git 状态 |
|------|------|---------|
| `application.yml` | 通用配置模板，使用环境变量占位符 | ✅ 可提交 |
| `application-local.yml` | 本地开发配置（实际地址、密码） | ❌ 已忽略 |
| `.env.example` | 环境变量模板（localhost 占位符） | ✅ 可提交 |
| `.env` | 实际环境变量（真实值） | ❌ 已忽略 |

### 2. .gitignore 增强

```gitignore
# Environment & Secrets
.env
.env.local
.env.*.local
*.env
!/.env.example
application-local.properties
application-local.yml
secrets/
*.pem
*.key
*.secret
credentials/
*.api.key
*.apikey
openai_key.txt
api_keys.txt
```

### 3. 环境变量使用

**Java Service：**
```bash
# 设置环境变量
set DB_PASSWORD=your-actual-password
set JWT_SECRET=your-actual-secret
set REDIS_HOST=192.168.85.66

# 启动服务
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

**Python Agent：**
```bash
# 复制模板并编辑
cd python-agent
copy .env.example .env
notepad .env  # 填入实际值

# 启动服务
python -m app.main
```

### 4. 安全规范文档

创建 [docs/SECURITY.md](docs/SECURITY.md)，包含：
- 绝对不能上传的内容清单
- 配置文件管理规范
- 环境变量使用方法
- 安全检查清单
- 泄露应急处理流程
- 最佳实践

## 关键规则

### 🔴 最高优先级（严禁上传）

- [ ] **API Key**（OpenAI、Langfuse 等）
- [ ] **密码**（数据库、Redis、JWT 密钥）
- [ ] **私钥**（SSH、SSL 证书）
- [ ] **Token**（GitHub、Service Account）

###  敏感信息（本地配置）

- 虚拟机 IP 地址（192.168.85.66）
- 内部服务地址
- 端口号（非标准端口）

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
# 重写历史示例
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

## File Boundaries

### Allowed To Modify

- `.gitignore` - 添加敏感文件忽略规则
- `docs/SECURITY.md` - 安全规范文档
- `*.example` - 配置模板文件（使用占位符）

### Must Not Modify

- `.env` - 实际环境变量文件（Git 忽略）
- `application-local.yml` - 本地配置文件（Git 忽略）
- 任何包含真实 API Key 或密码的文件

## Context To Read

- `docs/SECURITY.md` - 完整安全规范文档
- `.gitignore` - Git 忽略规则

## Acceptance Criteria

- [x] `.env` 文件在 `.gitignore` 中
- [x] `application-local.yml` 在 `.gitignore` 中
- [x] 代码中无硬编码的 API Key
- [x] `.env.example` 使用 localhost 占位符
- [x] `application.yml` 使用环境变量占位符
- [x] 安全规范文档已创建
- [x] 提交前检查清单已建立

## Verification

```bash
# 验证敏感文件未被提交
git ls-files | grep -E "\.env$|application-local\.yml"
# 应返回空

# 验证代码中无硬编码密钥
git grep -E "sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}"
# 应返回空

# 验证 .gitignore 规则
cat .gitignore | grep -A 20 "Environment & Secrets"
# 应包含所有敏感文件类型
```

## Handoff Notes

- Changed files:
  - `.gitignore` - 增强敏感文件忽略规则
  - `docs/SECURITY.md` - 新增安全规范文档
  - `python-agent/.env.example` - 移除虚拟机地址
  - `java-service/.env.example` - 新增环境变量模板
  - `java-service/src/main/resources/application.yml` - 改为环境变量占位符
  - `java-service/src/main/resources/application-local.yml` - 本地配置（Git 忽略）

- Verification result: 通过
- Known follow-ups: 无
- Memory updates needed: 已记录到 AI Team 任务卡
