from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from schemas.token import TokenMint, TokenRead
from services.token_service import insert_token, get_token_by_id, get_token_by_artwork_id
from services.artwork_service import get_artwork_by_id
from services.user_service import get_user_by_id
from utils.config import SECRET_KEY, ALGORITHM  # Ajuste aqui: certifique-se de ter essas variáveis no config.py

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return user_id
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

@router.post("/mint", response_model=dict)
def mint_token(payload: TokenMint, user_id: int = Depends(get_current_user_id)):
    """
    RF07: Emissão de Token
    """
    if not get_artwork_by_id(payload.artwork_id):
        raise HTTPException(status_code=400, detail="Obra não encontrada")

    if not get_user_by_id(user_id):
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    token_id = insert_token(payload.artwork_id, user_id, payload.price_tokens)
    return {"token_id": token_id, "status": "available","artwork_id": payload.artwork_id, "price": payload.price_tokens}

 


@router.get("/{token_id}", response_model=TokenRead)
def get_token(token_id: int):
    """
    RF10: Consulta de Token
    """
    token = get_token_by_id(token_id)
    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado")
    return token

@router.get("/by_artwork/{artwork_id}", response_model=TokenRead)
def get_token_by_artwork(artwork_id: int):
    """
    Buscar token associado a uma obra
    """
    token = get_token_by_artwork_id(artwork_id)
    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado para esta obra")
    return token