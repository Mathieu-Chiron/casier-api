import os
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from scraper import get_condamnations
from cache import get_cache, set_cache

app = FastAPI(
    title="Casier API",
    description="API de scraping casier-politique.fr",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)




@app.get("/")
def root():
    return {"message": "Casier API — GET /condamnations?name=Prénom+Nom"}


@app.get("/condamnations")
async def condamnations(
    name: str = Query(..., min_length=2, description="Nom complet du politique"),
    refresh: bool = Query(False),
):
    if not refresh:
        cached = get_cache(name)
        if cached:
            return cached

    result = await get_condamnations(name)
    set_cache(name, result)
    return result
