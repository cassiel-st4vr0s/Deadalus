import hashlib
import json
from ecdsa import VerifyingKey, BadSignatureError
from datetime import datetime
import hashlib
import json
from ecdsa import VerifyingKey, BadSignatureError


class ArtworkRecord:
    def __init__(self, artwork_id, title, description, author_id, author_name, file_hash, timestamp=None):
        self.artwork_id = artwork_id
        self.title = title
        self.description = description
        self.author_id = author_id
        self.author_name = author_name
        self.file_hash = file_hash
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "artwork_id": self.artwork_id,
            "title": self.title,
            "description": self.description,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "file_hash": self.file_hash,
            "timestamp": self.timestamp,
        }
    
class Block:
    def __init__(self, index, timestamp, previous_hash, artworks, nonce=0, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.artworks = artworks  # Lista de ArtworkRecord
        self.nonce = nonce
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "artworks": [art.to_dict() for art in self.artworks],
            "nonce": self.nonce,
        }
        block_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def proof_of_work(self, difficulty):
        prefix = "0" * difficulty
        while not self.calculate_hash().startswith(prefix):
            self.nonce += 1
        self.hash = self.calculate_hash()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "artworks": [art.to_dict() for art in self.artworks],
            "nonce": self.nonce,
            "hash": self.hash,
        }