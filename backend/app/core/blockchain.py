import time
from .block_class import Block
import json
import os

class Blockchain:
    def __init__(self, difficulty=2):
        self.difficulty = difficulty
        self.blocks = []
        self.artwork_pool = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, time.time(), None, [])
        genesis.proof_of_work(self.difficulty)
        self.blocks.append(genesis)

    def latest_block(self):
        return self.blocks[-1]

    def add_artwork(self, artwork_record):
        # Adiciona a obra à blockchain criando um novo bloco
        new_block = Block(
            index=self.latest_block().index + 1,
            timestamp=time.time(),
            previous_hash=self.latest_block().hash,
            artworks=[artwork_record]  # Aqui estamos passando um único ArtworkRecord
        )
        new_block.proof_of_work(self.difficulty)
        self.blocks.append(new_block)
        self.save()  # Salvar o estado da blockchain
        return new_block

    def mine_block(self):
        new_block = Block(
            index=self.latest_block().index + 1,
            timestamp=time.time(),
            previous_hash=self.latest_block().hash,
            artworks=self.artwork_pool.copy()
        )
        new_block.proof_of_work(self.difficulty)
        self.blocks.append(new_block)
        self.artwork_pool.clear()
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.blocks)):
            current = self.blocks[i]
            previous = self.blocks[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True
    
    def save(self, filepath="data/blockchain.json"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump([block.to_dict() for block in self.blocks], f, indent=4)