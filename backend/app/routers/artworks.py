from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import json
from schemas.artwork import ArtworkCreate, ArtworkRead
from services.artwork_service import insert_artwork, get_artwork_by_id, list_artworks

router = APIRouter()

@router.post("/", response_model=dict)
def create_artwork(payload: ArtworkCreate):
    artwork_id = insert_artwork(
        author_id=payload.author_id,
        file_hash=payload.file_hash,
        title=payload.title,
        description=payload.description
    )
    tx_data = json.dumps({
        "file_hash": payload.file_hash,
        "title": payload.title,
        "description": payload.description,
        "author_id": payload.author_id
    }, sort_keys=True, separators=(",", ":"))
    return {"artwork_id": artwork_id, "tx_data": tx_data}

@router.get("/{artwork_id}", response_model=ArtworkRead)
def get_artwork(artwork_id: int):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Obra não encontrada")
    return artwork

@router.get("/", response_model=List[ArtworkRead])
def list_all_artworks(
    author_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    return list_artworks(author_id, date_from, date_to)
