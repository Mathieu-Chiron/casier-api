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


@app.get("/debug")
def debug():
    import subprocess, glob
    pw_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH", "non défini")
    binary_pattern = f"{pw_path}/chromium*/chrome-headless-shell-linux64/chrome-headless-shell"
    binaries = glob.glob(binary_pattern)
    glib_check = subprocess.run(["find", "/usr", "-name", "libglib-2.0.so.0"], capture_output=True, text=True)
    ldconfig = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
    glib_in_ldconfig = [l for l in ldconfig.stdout.splitlines() if "libglib-2.0" in l]
    return {
        "PLAYWRIGHT_BROWSERS_PATH": pw_path,
        "binaries_found": binaries,
        "libglib_locations": glib_check.stdout.strip().splitlines(),
        "libglib_in_ldconfig": glib_in_ldconfig,
    }


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
