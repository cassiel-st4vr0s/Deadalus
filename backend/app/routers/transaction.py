from fastapi import APIRouter, Depends, Body, HTTPException
from schemas.transaction import SignData, TransactionData
from core.block_class import Block
from services.blockchain_service import get_blockchain
from services.user_service import get_user_by_id, update_user_wallet  # Import correto
from services.artwork_service import get_artwork_by_id  # Ajuste necessário
from services.token_service import update_token_status, get_token_by_id
from ecdsa import SigningKey

router = APIRouter()

@router.post("/sign", response_model=dict)
def sign_transaction(data: SignData):
    sk = SigningKey.from_pem(data.private_key.encode())
    tx_string = f"{data.sender}{data.recipient}{data.amount}"
    signature = sk.sign(tx_string.encode()).hex()
    return {"signature": signature}


@router.post("/send", response_model=dict)
def send_transaction(tx: TransactionData, blockchain=Depends(get_blockchain)):
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


@router.post("/buy")
def buy_token(token_id: int, buyer_id: int, password: str, signature: str, blockchain=Depends(get_blockchain)):
    """
    Compra de Token associado à Obra de Arte (assina manualmente e envia a assinatura)
    """

    # 1. Buscar comprador e token
    buyer = get_user_by_id(buyer_id)
    token = get_token_by_id(token_id)
    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado")
    
    artwork = get_artwork_by_id(token.artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Obra de arte associada ao token não encontrada")

    # Verificar se o token já foi comprado
    if token.status == "sold":
        raise HTTPException(status_code=400, detail="Token já foi vendido")

    # 2. Verificar saldo
    if buyer.wallet_balance < token.price_tokens:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    # 3. Criar transação
    tx_data = {
        "sender": buyer.public_key,
        "recipient": artwork.artist_public_key,  # Assume que artwork salva public_key do autor
        "amount": token.price_tokens,
        "public_key": buyer.public_key,
    }

    # 4. Validar assinatura
    tx_string = f'{tx_data["sender"]}{tx_data["recipient"]}{tx_data["amount"]}'
    sk = SigningKey.from_pem(buyer.private_key.encode())
    if not sk.verifying_key.verify(bytes.fromhex(signature), tx_string.encode()):
        raise HTTPException(status_code=400, detail="Assinatura inválida")

    transaction = Transaction(**tx_data)

    if not transaction.is_valid():
        raise HTTPException(status_code=400, detail="Transação inválida")

    # 5. Adicionar transação ao pool
    blockchain.add_transaction(transaction)

    # 6. Minerar bloco
    if not blockchain.transaction_pool:
        raise HTTPException(status_code=400, detail="Nenhuma transação para minerar")

    block = blockchain.mine_block()

    # 7. Atualizar wallets e salvar
    buyer.wallet_balance -= token.price_tokens
    update_user_wallet(buyer_id, buyer.wallet_balance)

    # Atualizar saldo do autor (que é o dono da obra)
    author = get_user_by_id(artwork.artist_id)  # Assume que a obra tem um `artist_id`
    author.wallet_balance += token.price_tokens
    update_user_wallet(author.id, author.wallet_balance)

    # 8. Atualizar o status do token para "sold"
    update_token_status(token_id, "sold")

    return {"message": "Compra de token realizada com sucesso", "block": block.to_dict()}
