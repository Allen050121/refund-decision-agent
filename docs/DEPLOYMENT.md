# Server Deployment

Target runtime for the project demo:

- Java service runs as a jar on port `8080`.
- Python Agent runs in a conda env on port `8001`.
- Nginx exposes `http://your-domain/demo`.
- MySQL, Redis, and Elasticsearch can run locally with Docker Compose.

## Server Layout

```text
/opt/refund-decision-agent/
  app/       # git repo
  env/       # real env files, not committed
```

## First Deploy

Install Java 21, Maven, Git, Miniconda, Docker, Docker Compose v2, and Nginx.

```bash
sudo mkdir -p /opt/refund-decision-agent
sudo chown -R "$USER:$USER" /opt/refund-decision-agent
cd /opt/refund-decision-agent
git clone https://github.com/Allen050121/refund-decision-agent.git app
cd app
```

Start local middleware:

```bash
cp .env.production.example .env
vi .env
docker compose up -d
```

Build the Java jar:

```bash
cd /opt/refund-decision-agent/app/java-service
mvn clean package -DskipTests
```

Create the Python conda env. This server uses `/home/ubuntu/miniconda3`; adjust
the systemd unit if your conda path is different.

```bash
conda create -y -n refund-agent python=3.12
conda run -n refund-agent pip install -r /opt/refund-decision-agent/app/python-agent/requirements.txt
```

Create server env files:

```bash
mkdir -p /opt/refund-decision-agent/env
cp /opt/refund-decision-agent/app/deploy/env/refund-java.env.example /opt/refund-decision-agent/env/refund-java.env
cp /opt/refund-decision-agent/app/deploy/env/refund-python.env.example /opt/refund-decision-agent/env/refund-python.env
vi /opt/refund-decision-agent/env/refund-java.env
vi /opt/refund-decision-agent/env/refund-python.env
```

Install systemd services:

```bash
sudo cp /opt/refund-decision-agent/app/deploy/systemd/refund-java.service /etc/systemd/system/
sudo cp /opt/refund-decision-agent/app/deploy/systemd/refund-python.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now refund-java refund-python
```

Import RAG rules after Elasticsearch and Python dependencies are ready:

```bash
cd /opt/refund-decision-agent/app/python-agent
conda run -n refund-agent python -m app.infrastructure.retrieval.rule_indexer --import data/refund_rules.json
```

Install Nginx reverse proxy:

```bash
sudo cp /opt/refund-decision-agent/app/deploy/nginx/default.conf /etc/nginx/conf.d/refund-agent.conf
sudo nginx -t
sudo systemctl reload nginx
```

Open:

```text
http://your-domain/demo
```

## Verify

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/health/ready
curl http://127.0.0.1:9201/_cluster/health
curl http://127.0.0.1/demo
```

From the repo root:

```bash
conda run -n refund-agent python scripts/service_smoke.py --java-url http://127.0.0.1:8080 --python-url http://127.0.0.1:8001
conda run -n refund-agent python scripts/real_llm_agent_smoke.py --timeout 45
```

## Update Deploy

```bash
cd /opt/refund-decision-agent/app
git pull --ff-only
cd java-service
mvn clean package -DskipTests
sudo systemctl restart refund-java
conda run -n refund-agent pip install -r /opt/refund-decision-agent/app/python-agent/requirements.txt
sudo systemctl restart refund-python
cd /opt/refund-decision-agent/app/python-agent
conda run -n refund-agent python -m app.infrastructure.retrieval.rule_indexer --import data/refund_rules.json
```

## Logs And Rollback

```bash
systemctl status refund-java refund-python
journalctl -u refund-java -f
journalctl -u refund-python -f
docker compose ps
```

Rollback for this MVP is to redeploy the previous Git commit, rebuild the jar, and restart both services.
