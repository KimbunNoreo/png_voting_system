from services.voting_service.models.daily_audit_hash import DailyAuditHash
def prepare_upload(audit_hash: DailyAuditHash) -> dict[str, str]:
    return {"device_id": audit_hash.device_id, "day": audit_hash.day, "digest": audit_hash.digest}