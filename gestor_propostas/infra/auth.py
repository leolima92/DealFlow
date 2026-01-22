import json
import os
from dataclasses import dataclass
from typing import Dict, Optional

from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
PASSWORD_HASH_METHOD = "argon2"


@dataclass
class User:
    username: str
    password: str

    def check_password(self, raw_password: str) -> bool:
        if AuthManager.is_hashed(self.password):
            try:
                return check_password_hash(self.password, raw_password)
            except ValueError:
                return False
        return self.password == raw_password


class AuthManager:
    HASH_PREFIXES = ("pbkdf2:", "scrypt:", "argon2:")

    @classmethod
    def is_hashed(cls, password: str) -> bool:
        return isinstance(password, str) and password.startswith(cls.HASH_PREFIXES)

    @classmethod
    def _hash_password(cls, password: str) -> str:
        try:
            return generate_password_hash(password, method=PASSWORD_HASH_METHOD)
        except ValueError:
            return generate_password_hash(password)

    @classmethod
    def _load_raw_data(cls) -> Dict:
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
    def _save_raw_data(cls, data: Dict):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_users(cls) -> Dict[str, User]:
        data = cls._load_raw_data()
        users: Dict[str, User] = {}

        if not isinstance(data, dict):
            return users

        for username, info in data.items():
            if isinstance(info, dict):
                pwd = info.get("password", "")
            elif isinstance(info, str):
                pwd = info
            else:
                pwd = ""
            users[username] = User(username=username, password=pwd)

        return users

    @classmethod
    def save_users(cls, users: Dict[str, User]):
        data: Dict[str, Dict] = {}
        for username, user in users.items():
            data[username] = {"password": user.password}
        cls._save_raw_data(data)

    @classmethod
    def ensure_default_admin(cls) -> User:
        users = cls.load_users()
        if "admin" not in users:
            admin = User(
                username="admin",
                password=cls._hash_password("admin"),
            )
            users["admin"] = admin
            cls.save_users(users)
        return users["admin"]

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional[User]:
        cls.ensure_default_admin()
        users = cls.load_users()
        user = users.get(username)
        if not user:
            return None
        if user.check_password(password):
            if not cls.is_hashed(user.password):
                user.password = cls._hash_password(password)
                users[username] = user
                cls.save_users(users)
            return user
        return None

    @classmethod
    def login(cls, username: str, password: str) -> Optional[User]:
        return cls.authenticate(username, password)

    @classmethod
    def validate_credentials(cls, username: str, password: str) -> bool:
        """Mantém compatibilidade com a UI desktop retornando apenas um booleano."""

        return cls.authenticate(username, password) is not None

    @classmethod
    def create_user(cls, username: str, password: str) -> Optional[User]:
        username = username.strip()
        if not username:
            return None

        users = cls.load_users()
        if username in users:
            return None

        user = User(username=username, password=cls._hash_password(password))
        users[username] = user
        cls.save_users(users)
        return user

    @classmethod
    def change_password(cls, username: str, new_password: str) -> bool:
        users = cls.load_users()
        user = users.get(username)
        if not user:
            return False
        user.password = cls._hash_password(new_password)
        users[username] = user
        cls.save_users(users)
        return True
