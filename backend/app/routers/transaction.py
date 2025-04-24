from fastapi import APIRouter, Depends, Body, HTTPException
from schemas.transaction import SignData, TransactionData
from core.block_class import Block, Transaction
from services.blockchain_service import get_blockchain
from ecdsa import SigningKey

router = APIRouter()

@router.post("/sign", response_model=dict)
def sign_transaction(data: SignData):
    """
    RF04: Assinatura de Transação
    """
    sk = SigningKey.from_pem(data.private_key.encode())
    signature = sk.sign(data.tx_data.encode()).hex()
    return {"signature": signature}

@router.post("/send", response_model=dict)
def send_transaction(tx: TransactionData, blockchain=Depends(get_blockchain)):
    """
    RF05: Envio de Transação ao Nó
    """
    transaction = Transaction(**tx.model_dump())
    if not transaction.is_valid():
        raise HTTPException(status_code=400, detail="Transação inválida")
    blockchain.add_transaction(transaction)
    return {"message": "Transação adicionada ao pool"}

@router.post("/mine", response_model=dict)
def mine_block(blockchain=Depends(get_blockchain)):
    """
    RF06: Mineração de Blocos
    """
    #blockchain em Node8000 usa attribute transaction_pool
    if not getattr(blockchain, 'transaction_pool', None):
        raise HTTPException(status_code=400, detail="Nenhuma transação para minerar")
    block = blockchain.mine_block()
    return {"message": "Bloco minerado", "block": block.to_dict()}


@router.get("/chain")
def get_chain(blockchain=Depends(get_blockchain)):
    return [block.to_dict() for block in blockchain.blocks]


@router.get("/check")
def check_chain(blockchain=Depends(get_blockchain)):
    if blockchain.is_chain_valid():
        return {"valid": True}
    return {"valid": False, "message": "Blockchain foi corrompida!"}


@router.get("/hack")
def hack_block(blockchain=Depends(get_blockchain)):
    if len(blockchain.blocks) > 1:
        blockchain.blocks[1].transactions[0].amount = 9999
        blockchain.blocks[1].hash = blockchain.blocks[1].calculate_hash()
        return {"message": "Bloco adulterado com sucesso"}
    return {"message": "Não há bloco suficiente para adulterar."}


@router.get("/export")
def export_chain(blockchain=Depends(get_blockchain)):
    return [block.to_dict() for block in blockchain.blocks]


@router.post("/import")
def import_chain(received_chain: list = Body(...), blockchain=Depends(get_blockchain)):
    new_chain = []
    for b in received_chain:
        transactions = [Transaction(**tx) for tx in b["transactions"]]
        new_block = Block(
            index=b["index"],
            timestamp=b["timestamp"],
            previous_hash=b["previous_hash"],
            transactions=transactions,
            nonce=b.get("nonce", 0)
        )
        new_chain.append(new_block)

    #verifica validade da nova cadeia
    if not blockchain.is_chain_valid(new_chain):
        raise HTTPException(status_code=400, detail="Cadeia recebida é inválida")

    blockchain.blocks = new_chain
    blockchain.save()
    return {"message": "Cadeia importada com sucesso"}


