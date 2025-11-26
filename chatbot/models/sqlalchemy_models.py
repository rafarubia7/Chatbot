from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    nome = db.Column(db.String(100), nullable=True)
    senha = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    curso = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com chats
    chats = db.relationship('Chat', backref='usuario', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Usuario {self.username}>"


class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(100), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Permite NULL para usuários anônimos
    session_id = db.Column(db.String(100), nullable=True)  # ID de sessão para usuários anônimos
    title = db.Column(db.String(255), nullable=False, default='Nova Conversa')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com mensagens
    mensagens = db.relationship('Mensagem', backref='chat', lazy=True, cascade='all, delete-orphan', order_by='Mensagem.created_at')

    def __repr__(self):
        return f"<Chat {self.chat_id} - {self.title}>"


class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' ou 'ai'
    nome_usuario = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Mensagem {self.id} - {self.sender}>" 