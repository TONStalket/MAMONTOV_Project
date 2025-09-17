from __future__ import annotations

from functools import wraps
from datetime import datetime
from typing import Any, Dict, List

from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import desc

from . import db
from .models import Message, User
from .sanitizer import sanitize_message

bp = Blueprint("main", __name__)


def get_current_user() -> User | None:
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return db.session.get(User, user_id)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            flash("Пожалуйста, войдите в аккаунт, чтобы продолжить.", "warning")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapped


@bp.context_processor
def inject_user() -> Dict[str, Any]:
    return {
        "current_user": get_current_user(),
        "current_year": datetime.utcnow().year,
    }


@bp.route("/")
def home() -> str:
    return render_template("home.html")


@bp.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        display_name = request.form.get("display_name", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors: List[str] = []

        if not email or not display_name or not password:
            errors.append("Все поля обязательны для заполнения.")

        if email and not email.endswith("@gmail.com"):
            errors.append("Регистрация доступна только с адресами Gmail.")

        if password and len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов.")

        if password != confirm_password:
            errors.append("Пароли не совпадают.")

        if User.query.filter_by(email=email).first():
            errors.append("Аккаунт с таким email уже существует.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html", email=email, display_name=display_name)

        user = User(email=email, display_name=display_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        flash("Добро пожаловать в Mamontov!", "success")
        return redirect(url_for("main.messenger"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Неверный email или пароль.", "danger")
            return render_template("login.html", email=email)

        session["user_id"] = user.id
        flash("Рады видеть вас снова!", "success")
        return redirect(url_for("main.messenger"))

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout() -> Response:
    session.pop("user_id", None)
    flash("Вы успешно вышли из аккаунта.", "info")
    return redirect(url_for("main.home"))


@bp.route("/messenger")
@login_required
def messenger() -> str:
    return render_template("messenger.html")


@bp.route("/api/messages", methods=["GET"])
@login_required
def api_messages() -> Response:
    messages = Message.query.order_by(desc(Message.created_at)).limit(100).all()
    payload = [
        {
            "id": message.id,
            "author": message.author.display_name,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        }
        for message in reversed(messages)
    ]
    return jsonify(payload)


@bp.route("/api/messages", methods=["POST"])
@login_required
def api_create_message() -> Response:
    data = request.get_json(silent=True) or {}
    raw_content = str(data.get("content", "")).strip()
    sanitized = sanitize_message(raw_content)

    if not sanitized:
        return jsonify({"error": "Сообщение не может быть пустым."}), 400

    if len(sanitized) > 500:
        return jsonify({"error": "Сообщение слишком длинное."}), 400

    user = get_current_user()
    if not user:
        return jsonify({"error": "Требуется авторизация."}), 401

    message = Message(author=user, content=sanitized)
    db.session.add(message)
    db.session.commit()

    return (
        jsonify(
            {
                "id": message.id,
                "author": message.author.display_name,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
        ),
        201,
    )
