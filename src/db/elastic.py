from functools import lru_cache

from elasticsearch import AsyncElasticsearch

from src.services.base_storage import ElasticsearchStorage

es: AsyncElasticsearch = None


@lru_cache()
def get_elastic() -> ElasticsearchStorage:
    return ElasticsearchStorage(es)
