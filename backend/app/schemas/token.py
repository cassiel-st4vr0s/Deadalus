from pydantic import BaseModel, Field


class TokenMint(BaseModel):
    artwork_id: int = Field(..., gt=0)
    price_tokens: int = Field(..., gt=0)


class TokenRead(BaseModel):
    id: int
    artwork_id: int
    owner_id: int
    status: str
    issued_at: str
    price_tokens: int
