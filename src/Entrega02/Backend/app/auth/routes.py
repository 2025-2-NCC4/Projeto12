from flask import request, jsonify
from flask_login import login_user, logout_user, current_user
from . import auth_bp
from ..extensions import db
from ..models import Usuario

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    senha = (data.get("senha") or "").strip()

    if not email or not senha:
        return jsonify({"ok": False, "error": "email_e_senha_obrigatorios"}), 400

    user: Usuario = Usuario.query.filter_by(email=email).first()
    if not user or not user.check_password(senha):
        return jsonify({"ok": False, "error": "credenciais_invalidas"}), 401

    login_user(user)  # sessão de login do Flask-Login
    return jsonify({
        "ok": True,
        "perfil": user.perfil.tipo,
        "nome": user.nome,
        "email": user.email
    })

@auth_bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return jsonify({"ok": True})
