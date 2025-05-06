import hashlib
import json
from ecdsa import VerifyingKey, BadSignatureError

import hashlib
import json
from ecdsa import VerifyingKey, BadSignatureError


class Transaction:
    def __init__(self, sender, recipient, amount, signature=None, public_key=None, data=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.public_key = public_key
        self.data = data  # agora está definido corretamente

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature,
            "public_key": self.public_key,
            "data": self.data,
        }

    def to_sign_string(self):
        amt = int(self.amount) if self.amount == int(self.amount) else self.amount
        return f'{{"sender":"{self.sender}","recipient":"{self.recipient}","amount":{amt}}}'

    def is_valid(self):
        if not self.signature or not self.public_key:
            return False
        try:
            tx_data_json = self.to_sign_string()
            print("[VALIDAÇÃO] dados para verificação:", tx_data_json)
            vk = VerifyingKey.from_pem(self.public_key.encode())
            vk.verify(bytes.fromhex(self.signature), tx_data_json.encode())
            return True
        except BadSignatureError:
            print("[VALIDAÇÃO] Signature verification failed")
            return False
        except Exception as e:
            print("[VALIDAÇÃO] Exceção inesperada:", e)
            return False



class Block:
    def __init__(
        self, index, timestamp, previous_hash, transactions, nonce=0, hash=None
    ):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.transactions = transactions  # Lista de Transaction
        self.nonce = nonce
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
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
            "transactions": [tx.to_dict() for tx in self.transactions],
            "nonce": self.nonce,
            "hash": self.hash,
        }
