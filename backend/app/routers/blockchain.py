from fastapi import APIRouter, Depends, HTTPException
from services.blockchain_service import get_blockchain
from routers.dependencies import get_current_user

router = APIRouter()


@router.post("/mine", response_model=dict, dependencies=[Depends(get_current_user)])
def mine_block(blockchain=Depends(get_blockchain)):
    if not getattr(blockchain, "transaction_pool", None):
        raise HTTPException(400, "Nenhuma transação para minerar")
    block = blockchain.mine_block()
    return {"message": "Bloco minerado", "block": block.to_dict()}


@router.get("/chain", dependencies=[Depends(get_current_user)])
def get_chain(blockchain=Depends(get_blockchain)):
    return [block.to_dict() for block in blockchain.blocks]
