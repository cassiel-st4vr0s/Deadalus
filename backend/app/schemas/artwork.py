from pydantic import BaseModel, Field
#from typing import Optional

class ArtworkCreate(BaseModel):
    file_hash: str = Field(..., min_length=64, max_length=64)
    title: str = Field(..., max_length=200)
    description: str
    author_id: int = Field(..., gt=0)

class ArtworkRead(BaseModel):
    id: int
    author_id: int
    hash: str
    title: str
    description: str
    created_at: str
