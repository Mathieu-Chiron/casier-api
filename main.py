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
    ms_contents = glob.glob("/ms-playwright/*") if os.path.isdir("/ms-playwright") else []
    app_contents = glob.glob("/app/playwright/*") if os.path.isdir("/app/playwright") else []
    all_chromium = subprocess.run(["find", "/", "-name", "chrome-headless-shell", "-type", "f"], capture_output=True, text=True, timeout=5)
    ms_chromium = glob.glob("/ms-playwright/chromium_headless_shell-*/*")
    app_chromium = glob.glob("/app/playwright/chromium_headless_shell-*/*")
    sys_chromium = subprocess.run(["find", "/usr/bin", "/usr/lib/chromium*", "-name", "chrom*", "-type", "f"], capture_output=True, text=True, timeout=5)
    return {
        "PLAYWRIGHT_BROWSERS_PATH": pw_path,
        "/ms-playwright/chromium_headless_shell-* contents": ms_chromium,
        "/app/playwright/chromium_headless_shell-* contents": app_chromium,
        "system chromium": sys_chromium.stdout.strip().splitlines(),
        "chrome-headless-shell found at": all_chromium.stdout.strip().splitlines(),
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
