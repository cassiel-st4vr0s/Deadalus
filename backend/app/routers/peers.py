from fastapi import APIRouter
from core.block_class import Transaction, Block
import requests

router = APIRouter()

peers = set()

@router.post("/register")
def register_peer(peer_url: str):
    peers.add(peer_url)
    return {"peers": list(peers)}

@router.get("/")
def list_peers():
    return {"peers": list(peers)}

@router.get("/sync")
def sync_with_peers():
    global blockchain
    longest_chain = blockchain.blocks
    for peer in peers:
        try:
            response = requests.get(f"{peer}/export")
            peer_chain = response.json()
            if len(peer_chain) > len(longest_chain):
                longest_chain = peer_chain
        except Exception:
            continue
    if len(longest_chain) > len(blockchain.blocks):
        new_chain = []
        for b in longest_chain:
            transactions = [Transaction(**tx) for tx in b["transactions"]]
            new_block = Block(
                index=b["index"],
                timestamp=b["timestamp"],
                previous_hash=b["previous_hash"],
                transactions=transactions,
                nonce=b["nonce"]
            )
            new_chain.append(new_block)
        blockchain.blocks = new_chain
        blockchain.save()
        return {"message": "Blockchain sincronizada com sucesso!"}
    return {"message": "Nenhuma cadeia mais longa encontrada."}