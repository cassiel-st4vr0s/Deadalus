from fastapi import APIRouter, HTTPException
from schemas.user import UserCreate, UserRead
from services.user_service import insert_user, get_user_by_id
from ecdsa import SigningKey

router = APIRouter()

@router.post("/register", response_model=dict)
def register_user(payload: UserCreate):
    # Gerar par de chaves
    sk = SigningKey.generate()
    vk = sk.verifying_key
    private_key_pem = sk.to_pem().decode()
    public_key_pem = vk.to_pem().decode()

    # Inserir no banco de dados
    user_id = insert_user(payload.name, public_key_pem)

    return {
        "user_id": user_id,
        "public_key": public_key_pem,
        "private_key": private_key_pem
    }

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user
