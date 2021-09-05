import asyncio

from elasticsearch import AsyncElasticsearch


async def populate_es_from_factory(es_client: AsyncElasticsearch, entities: list, index: str):
    await es_client.indices.delete(index, ignore=[400, 404])
    await es_client.indices.create(index)

    body = []
    for entity in entities:
        body.append({"index": {"_id": entity.id}})
        body.append(entity.json())

    await es_client.bulk(index=index, doc_type="doc", body=body)
    await asyncio.sleep(0.5)
