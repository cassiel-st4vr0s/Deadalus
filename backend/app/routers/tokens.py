from fastapi import APIRouter, HTTPException, Depends
from schemas.token import TokenMint, TokenRead
from services.token_service import insert_token, get_token_by_id
from services.artwork_service import get_artwork_by_id
from routers.dependencies import get_current_user
from services.user_service import get_user_by_id

router = APIRouter()


@router.post("/mint", response_model=dict, dependencies=[Depends(get_current_user)])
def mint_token(payload: TokenMint):
    """
    RF07: Emissão de Token
    """
    # valida existência de obra e usuário
    if not get_artwork_by_id(payload.artwork_id):
        raise HTTPException(status_code=400, detail="Obra não encontrada")
    if not get_user_by_id(payload.owner_id):
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    token_id = insert_token(payload.artwork_id, payload.owner_id)
    return {"token_id": token_id, "status": "available"}


@router.get(
    "/{token_id}", response_model=TokenRead, dependencies=[Depends(get_current_user)]
)
def get_token(token_id: int):
    """
    RF10: Consulta de Token
    """
    token = get_token_by_id(token_id)
    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado")
    return token
