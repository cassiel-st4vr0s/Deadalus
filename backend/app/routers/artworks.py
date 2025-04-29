from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
import hashlib
import json
from typing import Optional, List
from schemas.artwork import ArtworkRead
from services.artwork_service import insert_artwork, get_artwork_by_id, list_artworks, get_artworks_by_author_id
import os
from uuid import uuid4

router = APIRouter()


UPLOAD_DIR = "uploads/previews"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=dict)
def create_artwork(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    author_id: int = Form(...),
):
    try:
        # Ler o conteúdo do arquivo
        content = file.file.read()

        # Calcular o hash do conteúdo
        file_hash = hashlib.sha256(content).hexdigest()

        # Salvar o arquivo com nome único
        ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid4().hex}{ext}"
        save_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(save_path, "wb") as f:
            f.write(content)

        # Inserir no banco de dados com o caminho do preview
        artwork_id = insert_artwork(
            author_id=author_id,
            file_hash=file_hash,
            title=title,
            description=description,
            preview_path=save_path  # novo campo
        )

        # Preparar os dados para assinar na blockchain
        tx_data = json.dumps(
            {
                "file_hash": file_hash,
                "title": title,
                "description": description,
                "author_id": author_id
            },
            sort_keys=True,
            separators=(",", ":"),
        )

        return {
            "artwork_id": artwork_id,
            "tx_data": tx_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{artwork_id}", response_model=ArtworkRead)
def get_artwork(artwork_id: int):
    artwork = get_artwork_by_id(artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Obra não encontrada")
    return artwork

@router.get("/author/{author_id}", response_model=List[ArtworkRead])
def get_artworks_by_author(author_id: int):
    """
    Retorna todas as obras de um autor especificado pelo `author_id`.
    """
    artworks = get_artworks_by_author_id(author_id)
    if not artworks:
        raise HTTPException(status_code=404, detail="Nenhuma obra encontrada para este autor")
    return artworks


@router.get("/", response_model=List[ArtworkRead])
def list_all_artworks(
    author_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    return list_artworks(author_id, date_from, date_to)
