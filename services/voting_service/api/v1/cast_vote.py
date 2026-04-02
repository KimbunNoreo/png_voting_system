def cast_vote(token: str, encrypted_vote: str, device_signature: str) -> dict:
    return {
        "status": "queued",
        "token_hash_only": True,
        "device_signature_present": bool(device_signature),
    }
