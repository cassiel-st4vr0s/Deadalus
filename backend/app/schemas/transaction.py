from pydantic import BaseModel

class SignData(BaseModel):
    tx_data: str
    private_key: str

class TransactionData(BaseModel):
    sender: str
    recipient: str
    amount: float
    signature: str
    public_key: str