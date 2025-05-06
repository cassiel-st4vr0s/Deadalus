from fastapi import APIRouter, HTTPException, Depends
from schemas.user import UserCreate, UserRead, UserLogin
from services.user_service import insert_user, get_user_by_id, get_user_by_email, update_user_wallet
from utils.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES  # Ajuste aqui: certifique-se de ter essas variáveis no config.py
from ecdsa import SigningKey
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import secrets
from cryptography.fernet import Fernet
import base64
import hashlib
from fastapi import Body

router = APIRouter()

# Configuração do JWT

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/register", response_model=dict)
def register_user(payload: UserCreate):
    # Verificar se o email já está registrado
    existing_user = get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já registrado")

   # Gerar par de chaves
    sk = SigningKey.generate()
    vk = sk.verifying_key

    private_key_pem = sk.to_pem()
    public_key_pem = vk.to_pem().decode()

    # Criar chave de criptografia baseada na senha do usuário
    password_key = hashlib.sha256(payload.password.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(password_key[:32])
    fernet = Fernet(fernet_key)

    # Criptografar a chave privada
    encrypted_private_key = fernet.encrypt(private_key_pem).decode()

    # Hash da senha
    hashed_password = get_password_hash(payload.password)

    # Inserir no banco de dados e criar a carteira com 100 tokens
    user_id = insert_user(
    name=payload.name,
    public_key=public_key_pem,
    private_key_encrypted=encrypted_private_key,  # novo campo
    email=payload.email,
    password_hash=hashed_password
    )


    # Criar o token JWT
    access_token = create_access_token(data={"sub": str(user_id)})

    return {
        "user_id": user_id,
        "public_key": public_key_pem,
        "access_token": access_token,
        "wallet_balance": 100  # Saldo inicial
    }

@router.post("/login", response_model=dict)
def login_user(payload: UserLogin):
    # Verificar se o usuário existe
    user = get_user_by_email(payload.email)
    print(user)
    if not user:
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    # Verificar a senha usando o hash armazenado
    if not verify_password(payload.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    # Criar o token JWT para o usuário
    access_token = create_access_token(data={"sub": str(user['id'])})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user['id'],
        "user_name": user['name'],
        "wallet_balance": user['wallet_balance']
    }


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.post("/private_key", response_model=dict)
def get_private_key(payload: UserLogin):
    user = get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=403, detail="Senha incorreta")

    try:
        print("Usuário encontrado:", user)

        password_key = hashlib.sha256(payload.password.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(password_key[:32])
        print("Fernet Key (base64):", fernet_key)

        fernet = Fernet(fernet_key)

        encrypted_private_key = user["private_key_encrypted"]
        print("Chave Privada Criptografada (Base64):", encrypted_private_key)
        


        private_key_pem = fernet.decrypt(encrypted_private_key.encode()).decode()

        return {"private_key": private_key_pem}

    except Exception as e:
        print("Erro ao descriptografar a chave privada:", str(e))
        raise HTTPException(status_code=500, detail="Erro ao descriptografar a chave privada")
