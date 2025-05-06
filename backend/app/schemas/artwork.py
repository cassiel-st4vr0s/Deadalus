from pydantic import BaseModel, Field

class ArtworkCreate(BaseModel):
    file_hash: str = Field(..., min_length=64, max_length=64)  # Renomeado para 'hash'
    title: str = Field(..., max_length=200)
    description: str
    author_id: int = Field(..., gt=0)
    


class ArtworkRead(BaseModel):
    id: int
    author_id: int
    author_name: str
    file_hash: str
    title: str
    description: str
    created_at: str
    preview_path: str
    class Config:
        orm_mode = True
