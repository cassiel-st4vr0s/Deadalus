from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
import hashlib
import json
from typing import Optional, List
from schemas.artwork import ArtworkRead
from services.artwork_service import insert_artwork, get_artwork_by_id, list_artworks

router = APIRouter()


@router.post("/", response_model=dict)
def create_artwork(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    author_id: int = Form(...),
):
    try:
        content = file.file.read()
        file_hash = hashlib.sha256(content).hexdigest()

        artwork_id = insert_artwork(
            author_id=author_id,
            file_hash=file_hash,
            title=title,
            description=description,
        )

        tx_data = json.dumps(
            {
                "file_hash": file_hash,
                "title": title,
                "description": description,
                "author_id": author_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

        return {"artwork_id": artwork_id, "tx_data": tx_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    date_to: Optional[str] = Query(None),
):
    return list_artworks(author_id, date_from, date_to)
