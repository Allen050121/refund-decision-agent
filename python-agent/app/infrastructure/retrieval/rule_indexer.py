"""
规则索引管理工具
用于创建 ES 索引和导入规则数据
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from elasticsearch import AsyncElasticsearch

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 索引映射
INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "ruleId": {"type": "keyword"},
            "version": {"type": "integer"},
            "title": {"type": "text", "analyzer": "standard"},
            "content": {"type": "text", "analyzer": "standard"},
            "scenario": {"type": "keyword"},
            "reasonCode": {"type": "keyword"},
            "riskLevel": {"type": "keyword"},
            "effectiveFrom": {"type": "date"},
            "effectiveTo": {"type": "date"},
            "maxRefundPercent": {"type": "integer"},
            "approvalRequired": {"type": "boolean"},
            "approvalThreshold": {"type": "integer"},
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    }
}


async def create_index(es: AsyncElasticsearch, index_name: str) -> None:
    """创建索引（如果不存在）"""
    exists = await es.indices.exists(index=index_name)
    if not exists:
        await es.indices.create(index=index_name, body=INDEX_MAPPING)
        logger.info(f"索引 {index_name} 创建成功")
    else:
        logger.info(f"索引 {index_name} 已存在")


async def index_rules(es: AsyncElasticsearch, index_name: str, rules: List[Dict[str, Any]]) -> int:
    """导入规则数据"""
    count = 0
    for rule in rules:
        doc_id = f"{rule.get('ruleId', '')}_v{rule.get('version', 1)}"
        await es.index(index=index_name, id=doc_id, body=rule)
        count += 1
        logger.info(f"索引规则: {rule.get('ruleId')} v{rule.get('version')}")

    await es.indices.refresh(index=index_name)
    return count


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="规则索引管理")
    parser.add_argument("--import", dest="import_file", help="导入规则数据文件")
    parser.add_argument("--create-index", action="store_true", help="创建索引")
    parser.add_argument("--list", action="store_true", help="列出所有规则")
    args = parser.parse_args()

    es = AsyncElasticsearch(hosts=[settings.ELASTICSEARCH_URL])
    index_name = settings.ELASTICSEARCH_INDEX

    try:
        if args.create_index or not args.import_file:
            await create_index(es, index_name)

        if args.import_file:
            file_path = Path(args.import_file)
            if not file_path.exists():
                logger.error(f"文件不存在：{args.import_file}")
                return

            with open(file_path, "r", encoding="utf-8") as f:
                rules = json.load(f)

            count = await index_rules(es, index_name, rules)
            logger.info(f"成功导入 {count} 条规则")

        if args.list:
            response = await es.search(index=index_name, body={"size": 100})
            hits = response["hits"]["hits"]
            logger.info(f"索引中共有 {len(hits)} 条规则")
            for hit in hits:
                source = hit["_source"]
                logger.info(
                    f"  {source.get('ruleId')} v{source.get('version')} | "
                    f"{source.get('scenario')} | {source.get('title', '')[:30]}"
                )

    finally:
        await es.close()


if __name__ == "__main__":
    asyncio.run(main())
