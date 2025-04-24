from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.blockchain import Blockchain
from routers import (
    artworks as artworks_router,
    tokens as tokens_router,
    users as users_router,
    transaction as transaction_router,
    peers as peers_router,
)

import os

app = FastAPI(
    title="Deadalus DApp",
    description="DApp para registro e autenticação de obras digitais",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compartilhar objetos entre rotas
app.state.blockchain = Blockchain()
app.state.peers = set()

# Static & Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Home Page
@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Views
@app.get("/upload", include_in_schema=False)
def upload_view(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})


@app.get("/user", include_in_schema=False)
def user_view(request: Request):
    return templates.TemplateResponse("user_form.html", {"request": request})


@app.get("/transacao", include_in_schema=False)
def tx_view(request: Request):
    return templates.TemplateResponse("tx_form.html", {"request": request})


@app.get("/cadeia", include_in_schema=False)
def chain_view(request: Request):
    return templates.TemplateResponse("chain_view.html", {"request": request})


@app.get("/token", include_in_schema=False)
def token_view(request: Request):
    return templates.TemplateResponse("token_view.html", {"request": request})


# Health Check
@app.get("/health", tags=["status"])
def health_check():
    return {"status": "ok", "blocks": len(app.state.blockchain.blocks)}


# Routers
app.include_router(users_router.router, prefix="/users", tags=["users"])
app.include_router(artworks_router.router, prefix="/artworks", tags=["artworks"])
app.include_router(tokens_router.router, prefix="/tokens", tags=["tokens"])
app.include_router(
    transaction_router.router, prefix="/transaction", tags=["transaction"]
)
app.include_router(peers_router.router, prefix="/peers", tags=["peers"])

# Execução local direta
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
