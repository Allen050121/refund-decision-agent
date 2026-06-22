# 售后退款决策 Agent

面向在线教育场景的售后退款决策 Agent，结合 RAG、Tool Calling 和 Human-in-the-loop。

## 项目结构

- `java-service/` - Spring Boot 3 业务服务（订单、课程、退款资格校验）
- `python-agent/` - FastAPI + LangGraph Agent 服务（工单理解、规则检索、建议生成）
- `docker/` - Docker Compose 配置和基础设施配置
- `docs/` - 项目文档
- `tests/` - 集成测试和评测集

## 技术栈

### Java Service
- Java 21
- Spring Boot 3
- Spring Security + JWT
- MySQL 8
- Redis

### Python Agent
- Python 3.12
- FastAPI
- LangGraph
- Pydantic v2
- Elasticsearch

## 快速开始

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 开发阶段

- [x] 阶段 0：问题与评测先行
- [ ] 阶段 1：Java 确定性业务底座
- [ ] 阶段 2：Python Agent 最小链路
- [ ] 阶段 3：RAG 与证据
- [ ] 阶段 4：Redis Streams 与持久执行
- [ ] 阶段 5：评测、成本和安全
- [ ] 阶段 6：展示与简历证据

## 许可证

MIT
