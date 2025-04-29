from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str  # NOVO!

class UserLogin(BaseModel):
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    name: str
    email: str
    public_key: str
    wallet_balance: float
