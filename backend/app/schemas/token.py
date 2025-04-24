from pydantic import BaseModel, Field


class TokenMint(BaseModel):
    artwork_id: int = Field(..., gt=0)
    owner_id: int = Field(..., gt=0)


class TokenRead(BaseModel):
    id: int
    artwork_id: int
    owner_id: int
    status: str
    issued_at: str
