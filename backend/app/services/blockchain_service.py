from fastapi import Request

def get_blockchain(request: Request):
    return request.app.state.blockchain
