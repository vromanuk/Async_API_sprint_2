import logging
from logging import config as logging_config

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.core import config
from src.core.logger import LOGGING
from src.db import elastic, redis
from src.routes import api_router

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
)


@app.on_event("startup")
async def startup():
    logging_config.dictConfig(LOGGING)
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)
    elastic.es = AsyncElasticsearch(hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"])


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(api_router, prefix=config.API_V1_PREFIX)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
