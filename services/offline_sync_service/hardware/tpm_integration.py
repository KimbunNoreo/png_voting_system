"""TPM integration simulation for offline devices."""

from __future__ import annotations


class TPMIntegration:
    def attest(self) -> dict[str, str]:
        return {"status": "trusted", "source": "simulated-tpm"}
