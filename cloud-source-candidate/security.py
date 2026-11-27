import hmac
import os

from fastapi import Header, HTTPException


def validate_api_key(provided: str | None, expected: str | None) -> None:
    """Validate an API key without revealing either value in error messages."""
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Autenticacion no configurada",
        )

    if not provided or not hmac.compare_digest(
        provided.encode("utf-8"),
        expected.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=401,
            detail="Credenciales no validas",
        )


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    validate_api_key(x_api_key, os.getenv("SHOPFAST_API_KEY"))
