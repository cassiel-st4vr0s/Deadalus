from pydantic import BaseModel

class SignData(BaseModel):
    sender: str
    recipient: str
    amount: float
    private_key: str

class TransactionData(BaseModel):
    sender: str
    recipient: str
    amount: float
    signature: str
    public_key: str
