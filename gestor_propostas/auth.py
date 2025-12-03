import json
import os
import hashlib
from dataclasses import dataclass
from typing import Dict, Optional

BASE_DIR = os.path.dirname(__file__)
USERS_FILE = os.path.join(BASE_DIR, "users.json")


@dataclass
class User:
    username: str


class AuthManager:
    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def _load_users(cls) -> Dict[str, str]:
        if not os.path.isfile(USERS_FILE):
            return {}
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    @classmethod
    def _save_users(cls, users: Dict[str, str]) -> None:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

    @classmethod
    def ensure_default_admin(cls) -> None:
        """
        Garante que exista pelo menos um usuário admin/admin (apenas para uso didático).
        """
        users = cls._load_users()
        if "admin" not in users:
            users["admin"] = cls._hash_password("admin")
            cls._save_users(users)

    @classmethod
    def validate_credentials(cls, username: str, password: str) -> bool:
        users = cls._load_users()
        if username not in users:
            return False
        expected_hash = users[username]
        return expected_hash == cls._hash_password(password)

    @classmethod
    def create_user(cls, username: str, password: str) -> bool:
        """
        Cria um novo usuário. Retorna False se já existir.
        """
        username = username.strip()
        if not username:
            return False

        users = cls._load_users()
        if username in users:
            return False

        users[username] = cls._hash_password(password)
        cls._save_users(users)
        return True
