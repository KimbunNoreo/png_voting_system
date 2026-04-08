def require_observer(role: str) -> None:
    if role != "observer": raise PermissionError("Observer privileges are required")