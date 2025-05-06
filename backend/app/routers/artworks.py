from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
import hashlib
import os
from uuid import uuid4
from typing import Optional, List
from schemas.artwork import ArtworkRead
from services.artwork_service import insert_artwork, get_artwork_by_id, list_artworks, get_artworks_by_author_id, get_artwork_with_token
from services.user_service import get_user_by_id
from core.block_class import ArtworkRecord
from core.blockchain import Blockchain

router = APIRouter()
UPLOAD_DIR = "uploads/previews"
os.makedirs(UPLOAD_DIR, exist_ok=True)

blockchain = Blockchain()

@router.post("/", response_model=dict)
def create_artwork(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    author_id: int = Form(...),
):
    try:
        # 1. Processar o arquivo
        content = file.file.read()
        file_hash = hashlib.sha256(content).hexdigest()

        ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid4().hex}{ext}"
        save_path = os.path.join(UPLOAD_DIR, unique_filename).replace("\\", "/")
        with open(save_path, "wb") as f:
            f.write(content)

        # 2. Verificar se autor existe
        author = get_user_by_id(author_id)

        if not author:
            raise HTTPException(status_code=404, detail="Autor não encontrado")

        # 3. Inserir obra no banco de dados (sem blockchain)
        artwork_id = insert_artwork(
            author_id=author_id,
            file_hash=file_hash,
            title=title,
            description=description,
            preview_path=save_path,
            author_name= author["name"],
        )

        
        # 4. Criar o ArtworkRecord
        artwork_record = ArtworkRecord(
            artwork_id=artwork_id,
            title=title,
            description=description,
            author_id=author_id,
            author_name=author["name"],
            file_hash=file_hash
        )

        # 5. Adicionar o registro de obra à blockchain
        blockchain.add_artwork(artwork_record)

        return {
            "message": "Obra criada com sucesso e registrada na blockchain",
            "artwork_id": artwork_id,
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
    artworks = get_artworks_by_author_id(author_id)
    if not artworks:
        raise HTTPException(status_code=404, detail="Nenhuma obra encontrada para este autor")
    return artworks

@router.get("/", response_model=List[ArtworkRead])
def list_all_artworks(
    title: Optional[str] = Query(None),
    author_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    return list_artworks(title, author_id, date_from, date_to)


