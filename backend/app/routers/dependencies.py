from fastapi import Header, Depends, HTTPException
from services.user_service import get_user_by_public_key


def get_current_user(x_user_public_key: str = Header(None)):
    if not x_user_public_key:
        raise HTTPException(status_code=401, detail="Chave pública não fornecida")
    user = get_user_by_public_key(x_user_public_key)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário inválido")
    return user
