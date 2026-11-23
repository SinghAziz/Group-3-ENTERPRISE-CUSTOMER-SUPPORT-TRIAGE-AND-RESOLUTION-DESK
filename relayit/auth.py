from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass


class AuthenticationError(ValueError):
    pass


class AuthorizationError(PermissionError):
    pass


@dataclass(frozen=True)
class User:
    username: str
    role: str


SYSTEM_USER = User("relayit-workflow", "system")


def require_user(user: User | None) -> User:
    if user is None:
        raise AuthorizationError("An authenticated user is required.")
    return user


def hash_password(password: str, salt: bytes | None = None) -> str:
    if not password:
        raise ValueError("Password must not be empty.")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds)
        ).hex()
        return hmac.compare_digest(candidate, digest_hex)
    except (ValueError, TypeError):
        return False


def configured_users() -> dict[str, dict[str, str]]:
    raw = os.getenv("RELAYIT_AUTH_USERS_JSON", "").strip()
    if not raw:
        return {}
    try:
        users = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AuthenticationError("RELAYIT_AUTH_USERS_JSON is not valid JSON.") from exc
    if not isinstance(users, dict):
        raise AuthenticationError("RELAYIT_AUTH_USERS_JSON must be an object.")
    return users


def authenticate(username: str, password: str) -> User:
    record = configured_users().get(username)
    if not isinstance(record, dict) or not verify_password(password, record.get("password_hash", "")):
        raise AuthenticationError("Invalid username or password.")
    role = record.get("role", "")
    if role not in {"admin", "analyst", "reviewer"}:
        raise AuthenticationError("Configured user has an invalid role.")
    return User(username=username, role=role)


def require_role(user: User, *roles: str) -> None:
    if user.role != "system" and user.role not in roles:
        raise AuthorizationError("Your role is not allowed to perform this action.")


if __name__ == "__main__":
    import getpass

    print(hash_password(getpass.getpass("Password: ")))
