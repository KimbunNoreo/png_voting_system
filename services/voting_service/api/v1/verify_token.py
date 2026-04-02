def verify_token(token: str) -> dict:
    return {"status": "pending", "token_received": bool(token)}
