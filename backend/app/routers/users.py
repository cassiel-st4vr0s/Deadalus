from fastapi import APIRouter
from ecdsa import SigningKey, NIST384p

router = APIRouter()

@router.get("/generate_keys")
def generate_keys():
    sk = SigningKey.generate(curve=NIST384p)
    vk = sk.verifying_key
    return {
        "private_key": sk.to_pem().decode(),
        "public_key": vk.to_pem().decode()
    }
