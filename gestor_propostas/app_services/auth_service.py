from __future__ import annotations

from typing import Optional

from ..infra.auth import AuthManager, User


class AuthService:
    def authenticate(self, username: str, password: str) -> Optional[User]:
        return AuthManager.authenticate(username, password)

    def create_user(self, username: str, password: str) -> Optional[User]:
        return AuthManager.create_user(username, password)

    def ensure_default_admin(self) -> User:
        return AuthManager.ensure_default_admin()
