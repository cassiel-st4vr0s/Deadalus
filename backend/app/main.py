from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.blockchain import Blockchain
from routers import artworks as artworks_router
from routers import tokens as tokens_router
from routers import users as users_router
from routers import transaction as transaction_router
from routers import peers as peers_router

app = FastAPI(
    title="Deadalus DApp",
    description="DApp para registro e autenticação de obras digitais",
    version="0.1.0",
)
app.state.peers = set()

# habilitando CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrinjir para ["http://localhost:8000"] se necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# instânciando a blockchain que será compartilhada entre as rotas
blockchain = Blockchain()

# expor blockchain para uso nos endpoints via app state
app.state.blockchain = blockchain


# status check do DApp e da blockchain
@app.get("/health", tags=["status"])
def health_check():
    return {"status": "ok", "blocks": len(app.state.blockchain.blocks)}


# Registro dos routers (controllers)
app.include_router(users_router.router, prefix="/users", tags=["users"])
app.include_router(artworks_router.router, prefix="/artworks", tags=["artworks"])
app.include_router(tokens_router.router, prefix="/tokens", tags=["tokens"])
app.include_router(
    transaction_router.router, prefix="/transaction", tags=["transaction"]
)
app.include_router(peers_router.router, prefix="/peers", tags=["peers"])

# ponto de entrada para execução (uvicorn app.main:app)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
