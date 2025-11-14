"""
Gerenciador de sessão e histórico de chat usando MySQL
"""
from typing import Dict, List, Optional
from datetime import datetime
from models.sqlalchemy_models import db, Chat, Mensagem


class SessionManager:
    def __init__(self):
        """Inicializa o gerenciador de sessão usando MySQL"""
        pass
    
    def get_chat_history(self, chat_id: str, user_id: Optional[str] = None) -> List[Dict]:
        """Recupera o histórico de um chat específico (por usuário)."""
        try:
            chat = Chat.query.filter_by(chat_id=chat_id).first()
            if not chat:
                return []
            
            # Verificar se o chat pertence ao usuário
            if user_id and str(chat.user_id) != str(user_id):
                return []
            
            mensagens = Mensagem.query.filter_by(chat_id=chat.id).order_by(Mensagem.created_at).all()
            
            history = []
            for msg in mensagens:
                history.append({
                    "text": msg.text,
                    "sender": msg.sender,
                    "timestamp": msg.created_at.isoformat() if msg.created_at else datetime.now().isoformat(),
                    "nome_usuario": msg.nome_usuario
                })
            
            return history
        except Exception as e:
            print(f"Erro ao recuperar histórico: {e}")
            return []
    
    def save_chat(self, chat_id: str, title: str, messages: List[Dict], user_id: Optional[str] = None) -> None:
        """Salva ou atualiza um chat (por usuário)."""
        if not user_id:
            return
        
        try:
            # Buscar ou criar chat
            chat = Chat.query.filter_by(chat_id=chat_id).first()
            
            if not chat:
                # Criar novo chat
                chat = Chat(
                    chat_id=chat_id,
                    user_id=int(user_id),
                    title=title
                )
                db.session.add(chat)
                db.session.flush()  # Para obter o ID do chat
            else:
                # Verificar se o chat pertence ao usuário
                if str(chat.user_id) != str(user_id):
                    return
                # Atualizar título se fornecido
                if title:
                    chat.title = title
                    chat.updated_at = datetime.utcnow()
            
            # Se há mensagens para salvar, substituir todas as mensagens existentes
            if messages:
                # Deletar mensagens antigas
                Mensagem.query.filter_by(chat_id=chat.id).delete()
                
                # Adicionar novas mensagens
                for msg_data in messages:
                    msg = Mensagem(
                        chat_id=chat.id,
                        text=msg_data.get('text', '') or msg_data.get('texto', ''),
                        sender=msg_data.get('sender', '') or msg_data.get('remetente', ''),
                        nome_usuario=msg_data.get('nome_usuario')
                    )
                    # Se há timestamp, usar; senão usar agora
                    if 'timestamp' in msg_data:
                        try:
                            msg.created_at = datetime.fromisoformat(msg_data['timestamp'].replace('Z', '+00:00'))
                        except:
                            pass
                    db.session.add(msg)
            
            db.session.commit()
        except Exception as e:
            print(f"Erro ao salvar chat: {e}")
            db.session.rollback()
    
    def delete_chat(self, chat_id: str, user_id: Optional[str] = None) -> bool:
        """Deleta um chat (por usuário)."""
        if not user_id:
            return False
        
        try:
            chat = Chat.query.filter_by(chat_id=chat_id).first()
            if not chat:
                return False
            
            # Verificar se o chat pertence ao usuário
            if str(chat.user_id) != str(user_id):
                return False
            
            # Deletar chat (mensagens serão deletadas automaticamente por CASCADE)
            db.session.delete(chat)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Erro ao deletar chat: {e}")
            db.session.rollback()
            return False
    
    def list_chats(self, user_id: Optional[str] = None) -> List[Dict]:
        """Lista todos os chats do usuário logado (ou globais se None)."""
        if not user_id:
            return []
        
        try:
            chats = Chat.query.filter_by(user_id=int(user_id)).order_by(Chat.updated_at.desc()).all()
            
            result = []
            for chat in chats:
                # Buscar última mensagem
                last_msg = Mensagem.query.filter_by(chat_id=chat.id).order_by(Mensagem.created_at.desc()).first()
                last_message = ""
                if last_msg:
                    last_message = last_msg.text[:50]
                    if len(last_msg.text) > 50:
                        last_message += "..."
                
                result.append({
                    'id': chat.chat_id,
                    'title': chat.title,
                    'lastMessage': last_message,
                    'timestamp': chat.updated_at.isoformat() if chat.updated_at else datetime.now().isoformat()
                })
            
            return result
        except Exception as e:
            print(f"Erro ao listar chats: {e}")
            return []
    
    def add_message(self, chat_id: str, text: str, sender: str, user_id: Optional[str] = None, nome_usuario: Optional[str] = None) -> None:
        """Adiciona uma mensagem ao histórico do chat (por usuário)."""
        if not user_id:
            return
        
        try:
            # Buscar ou criar chat
            chat = Chat.query.filter_by(chat_id=chat_id).first()
            
            if not chat:
                # Criar novo chat se não existir
                chat = Chat(
                    chat_id=chat_id,
                    user_id=int(user_id),
                    title='Nova Conversa'
                )
                db.session.add(chat)
                db.session.flush()
            else:
                # Verificar se o chat pertence ao usuário
                if str(chat.user_id) != str(user_id):
                    return
            
            # Verificar se a última mensagem é igual (evitar duplicação)
            last_msg = Mensagem.query.filter_by(chat_id=chat.id).order_by(Mensagem.created_at.desc()).first()
            if last_msg and last_msg.text == text and last_msg.sender == sender:
                return
            
            # Adicionar nova mensagem
            msg = Mensagem(
                chat_id=chat.id,
                text=text,
                sender=sender,
                nome_usuario=nome_usuario if sender == 'user' else None
            )
            db.session.add(msg)
            
            # Atualizar timestamp do chat
            chat.updated_at = datetime.utcnow()
            
            db.session.commit()
        except Exception as e:
            print(f"Erro ao adicionar mensagem: {e}")
            db.session.rollback()
    
    def get_chat_title(self, chat_id: str, user_id: Optional[str] = None) -> Optional[str]:
        """Recupera o título de um chat (por usuário)."""
        try:
            chat = Chat.query.filter_by(chat_id=chat_id).first()
            if not chat:
                return None
            
            # Verificar se o chat pertence ao usuário
            if user_id and str(chat.user_id) != str(user_id):
                return None
            
            return chat.title
        except Exception as e:
            print(f"Erro ao recuperar título: {e}")
            return None
    
    def update_chat_title(self, chat_id: str, title: str, user_id: Optional[str] = None) -> None:
        """Atualiza o título de um chat (por usuário)."""
        if not user_id:
            return
        
        try:
            chat = Chat.query.filter_by(chat_id=chat_id).first()
            if not chat:
                return
            
            # Verificar se o chat pertence ao usuário
            if str(chat.user_id) != str(user_id):
                return
            
            chat.title = title
            chat.updated_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            print(f"Erro ao atualizar título: {e}")
            db.session.rollback()
