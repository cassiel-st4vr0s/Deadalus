from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None

class UserRead(BaseModel):
    id: int
    name: str
    public_key: str
    registered_at: str
