from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from ..app_context import get_context

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _auth_service():
    return get_context().auth_service


@bp.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = _auth_service().authenticate(username, password)
        if user:
            session["username"] = user.username
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("ui.index"))
        else:
            flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html")


@bp.route("/logout")
def logout_view():
    session.pop("username", None)
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

        user = _auth_service().create_user(username, password)
        if not user:
            flash("Nome de usuário já existe.", "danger")
            return render_template("register.html")

        flash("Usuário criado com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login_view"))

    return render_template("register.html")
