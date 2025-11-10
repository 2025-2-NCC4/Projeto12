from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db

class Perfil(db.Model):
    __tablename__ = "perfil"
    id_perfil = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(3), nullable=False, index=True) 
    usuarios = db.relationship("Usuario", back_populates="perfil")

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_perfil_fk = db.Column(db.Integer, db.ForeignKey("perfil.id_perfil"), nullable=False)
    nome = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(300), nullable=False)

    perfil = db.relationship("Perfil", back_populates="usuarios")

    
    def get_id(self):
        return str(self.id_usuario)


    def set_password(self, pwd: str):
        self.senha = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self.senha, pwd)


class Transacao(db.Model):
    __tablename__ = "transacao"
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)      
    valor = db.Column(db.Numeric(12,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
