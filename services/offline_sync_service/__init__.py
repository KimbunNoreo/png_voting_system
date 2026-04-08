"""Offline sync service package."""

__all__ = ["SyncEngine", "OfflineSyncOperatorAPI", "OfflineSyncDependencies", "build_offline_sync_dependencies"]


def __getattr__(name: str):
    if name == "SyncEngine":
        from services.offline_sync_service.sync.engine import SyncEngine

        return SyncEngine
    if name == "OfflineSyncOperatorAPI":
        from services.offline_sync_service.api.operator import OfflineSyncOperatorAPI

        return OfflineSyncOperatorAPI
    if name in {"OfflineSyncDependencies", "build_offline_sync_dependencies"}:
        from services.offline_sync_service.factory import OfflineSyncDependencies, build_offline_sync_dependencies

        return {
            "OfflineSyncDependencies": OfflineSyncDependencies,
            "build_offline_sync_dependencies": build_offline_sync_dependencies,
        }[name]
    raise AttributeError(name)
