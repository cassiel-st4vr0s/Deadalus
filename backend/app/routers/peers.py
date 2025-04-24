from fastapi import APIRouter, Request, Depends
import requests
from services.blockchain_service import get_blockchain
from core.block_class import Block, Transaction

router = APIRouter()


@router.post("/register", response_model=dict)
def register_peer(request: Request, peer_url: str):
    """
    RF12: Registro de Peer
    """
    peers = request.app.state.peers
    if peer_url in peers:
        return {"peers": list(peers)}
    peers.add(peer_url)
    return {"peers": list(peers)}


@router.get("", response_model=dict)
def list_peers(request: Request):
    """
    Lista peers registrados
    """
    return {"peers": list(request.app.state.peers)}


@router.get("/sync", response_model=dict)
def sync_peers(request: Request, blockchain=Depends(get_blockchain)):
    """
    RF13: Sincronização com Peers
    """
    peers = request.app.state.peers
    # Obtém a cadeia local em formato dict
    local_chain = [block.to_dict() for block in blockchain.blocks]
    longest_chain = local_chain

    for peer in peers:
        try:
            response = requests.get(f"{peer}/export")
            response.raise_for_status()
            peer_chain = response.json()
            if len(peer_chain) > len(longest_chain):
                longest_chain = peer_chain
        except Exception:
            continue

    if len(longest_chain) > len(blockchain.blocks):
        # Reconstrói blocos a partir da maior cadeia
        new_blocks = []
        for b in longest_chain:
            txs = [Transaction(**tx) for tx in b.get("transactions", [])]
            block = Block(
                index=b["index"],
                timestamp=b["timestamp"],
                previous_hash=b.get("previous_hash"),
                transactions=txs,
                nonce=b.get("nonce", 0),
                hash=b.get("hash"),
            )
            new_blocks.append(block)
        blockchain.blocks = new_blocks
        try:
            blockchain.save()
        except Exception:
            pass
        return {"message": "Blockchain sincronizada com sucesso!"}

    return {"message": "Nenhuma cadeia mais longa encontrada."}
