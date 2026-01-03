import json
import os
from dataclasses import dataclass
from typing import Dict, Optional

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

BASE_DIR = os.path.dirname(__file__)
USERS_FILE = os.path.join(BASE_DIR, "users.json")


@dataclass
class User:
    username: str
    password: str

    def check_password(self, raw_password: str) -> bool:
        return self.password == raw_password


class AuthManager:
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
            admin = User(username="admin", password="admin")
            users["admin"] = admin
            cls.save_users(users)
        return users["admin"]

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional[User]:
        cls.ensure_default_admin()
        users = cls.load_users()
        user = users.get(username)
        if user and user.check_password(password):
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

        user = User(username=username, password=password)
        users[username] = user
        cls.save_users(users)
        return user

    @classmethod
    def change_password(cls, username: str, new_password: str) -> bool:
        users = cls.load_users()
        user = users.get(username)
        if not user:
            return False
        user.password = new_password
        users[username] = user
        cls.save_users(users)
        return True

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = AuthManager.login(username, password)
        if user:
            session["user"] = user.username
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("ui.index")) 
        else:
            flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html")


@bp.route("/logout")
def logout_view():
    session.pop("user", None)
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login_view"))


@bp.route("/register", methods=["GET", "POST"])
def register_view():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Preencha usuário e senha.", "warning")
            return render_template("register.html")

        if password != confirm:
            flash("As senhas não conferem.", "warning")
            return render_template("register.html")

        user = AuthManager.create_user(username, password)
        if not user:
            flash("Nome de usuário já existe.", "danger")
            return render_template("register.html")

        flash("Usuário criado com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login_view"))

    return render_template("register.html")
