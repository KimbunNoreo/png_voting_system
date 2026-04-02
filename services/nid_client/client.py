class NIDClient:
    def __init__(self, base_url: str, timeout_seconds: int = 5) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    def verify(self, payload: dict) -> dict:
        return {"status": "not_implemented", "operation": "verify", "payload": payload}

    def lookup(self, payload: dict) -> dict:
        return {"status": "not_implemented", "operation": "lookup", "payload": payload}
