"""
Aplicação principal do chatbot do SENAI São Carlos
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime

from config import FLASK_SECRET_KEY, SQLALCHEMY_DATABASE_URI
from utils.chat_manager import process_message
from utils.session_manager import SessionManager
from utils.suggestions_manager import save_suggestion
from models.sqlalchemy_models import db, Usuario, Chat, Mensagem
from info import RESPOSTAS_PADRAO

app = Flask(__name__)
CORS(app)
app.secret_key = FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar tabelas do banco se não existirem
with app.app_context():
    db.create_all()
    
    # Criar usuários padrão para login social se não existirem
    usuarios_padrao = [
        {
            'username': 'usuario@gmail.com',
            'nome': 'Usuário Google',
            'email': 'usuario@gmail.com',
            'senha': 'senha123'
        },
        {
            'username': 'usuario@icloud.com',
            'nome': 'Usuário Apple',
            'email': 'usuario@icloud.com',
            'senha': 'senha123'
        },
        {
            'username': 'usuario@facebook.com',
            'nome': 'Usuário Facebook',
            'email': 'usuario@facebook.com',
            'senha': 'senha123'
        }
    ]
    
    for user_data in usuarios_padrao:
        if not Usuario.query.filter_by(username=user_data['username']).first():
            novo_usuario = Usuario(
                username=user_data['username'],
                nome=user_data['nome'],
                email=user_data['email'],
                senha=user_data['senha']
            )
            db.session.add(novo_usuario)
            print(f"Usuário padrão criado: {user_data['nome']}")
    
    db.session.commit()

# Instanciar o gerenciador de sessão
session_manager = SessionManager()

@app.route('/')
def index():
    """Rota principal que exibe a tela inicial"""
    return render_template('tela.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login do usuário"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('password', '').strip()

        print(f"Tentativa de login - username: {username}")  # Debug

        if not username or not senha:
            return render_template('login.html', error="Preencha todos os campos.")

        usuario = Usuario.query.filter_by(username=username, senha=senha).first()
        if usuario:
            print(f"Login bem-sucedido - Usuário: {usuario.nome}, Email: {usuario.email}")  # Debug
            session['username'] = usuario.username
            session['user_id'] = usuario.id
            session['user_nome'] = usuario.nome
            session['user_email'] = usuario.email
            return redirect(url_for('chat_page'))
        else:
            print("Login falhou - Usuário não encontrado ou senha incorreta")  # Debug
            return render_template('login.html', error="Usuário ou senha inválidos.")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Rota para registro de novos usuários"""
    if request.method == 'POST':
        nome = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        senha = request.form.get('password', '').strip()

        print(f"Recebido: nome={nome}, email={email}, username={username}")

        if not nome or not email or not username or not senha:
            print("Erro: campos obrigatórios faltando")
            return render_template('register.html', error="Preencha todos os campos obrigatórios.")

        if Usuario.query.filter_by(username=username).first():
            print("Erro: usuário já existe")
            return render_template('register.html', error="Nome de usuário já existe.")

        novo_usuario = Usuario(
            username=username,
            nome=nome,
            senha=senha,
            email=email,
            avatar_path=None
        )
        
        try:
            db.session.add(novo_usuario)
            db.session.commit()
            print("Usuário cadastrado com sucesso!")
            print("ID do novo usuário:", novo_usuario.id)
            
            # Após cadastrar, já loga o usuário
            session['username'] = username
            session['user_id'] = novo_usuario.id
            session['user_nome'] = novo_usuario.nome
            session['user_email'] = novo_usuario.email
            
            return redirect(url_for('chat_page'))
        except Exception as e:
            print("Erro ao cadastrar usuário:", str(e))
            db.session.rollback()
            return render_template('register.html', error="Erro ao cadastrar usuário. Tente novamente.")

    return render_template('register.html')

@app.route('/chat')
def chat_page():
    """Rota para a página do chat - permite acesso sem login"""
    # Criar ou obter session_id para usuários anônimos
    if 'session_id' not in session:
        import uuid
        session['session_id'] = str(uuid.uuid4())
    
    # Se o usuário está logado, usar dados do usuário
    if 'username' in session:
        user = Usuario.query.filter_by(username=session['username']).first()
        if user:
            user_data = {
                'id': user.id,
                'username': user.username,
                'nome': user.nome,
                'email': user.email,
                'avatar': user.avatar_path or url_for('static', filename='default-avatar.svg')
            }
            return render_template('chat.html', user=user_data, is_authenticated=True)
    
    # Usuário anônimo - usar dados padrão
    user_data = {
        'id': None,
        'username': 'Visitante',
        'nome': 'Visitante',
        'email': None,
        'avatar': url_for('static', filename='default-avatar.svg')
    }
    return render_template('chat.html', user=user_data, is_authenticated=False)

@app.route('/profile')
def profile_page():
    """Rota para a página de perfil"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('profile.html')

@app.route('/info')
def info_page():
    """Rota para a página de informações da aplicação"""
    return render_template('info.html')


@app.route('/api/chat', methods=['POST'])
@app.route('/chat', methods=['POST'])
def chat_api():
    """Endpoint da API para processamento de mensagens do chat"""
    try:
        if not request.is_json:
            return jsonify({"reply": "Erro: Content-Type deve ser application/json"}), 415
            
        data = request.get_json()
        # Aceita tanto 'message' quanto 'mensagem' por compatibilidade
        user_message = (data.get('message') or data.get('mensagem') or '').strip()
        chat_id = data.get('chat_id')
        
        if not user_message:
            return jsonify({"reply": "Por favor, digite uma mensagem."}), 400
            
        if not chat_id:
            return jsonify({"error": "Chat ID não fornecido"}), 400
        
        # Adicionar mensagem do usuário ao histórico (por usuário ou sessão anônima)
        user_id = session.get('user_id')
        session_id = session.get('session_id')
        user_nome = session.get('user_nome') or session.get('username') or 'Visitante'
        session_manager.add_message(chat_id, user_message, "user", user_id=user_id, session_id=session_id, nome_usuario=user_nome)
        
        # Processar a mensagem e gerar resposta
        chat_history = session_manager.get_chat_history(chat_id, user_id=user_id, session_id=session_id)
        ai_response = process_message(user_message, chat_history)
        
        # Adicionar resposta do AI ao histórico
        session_manager.add_message(chat_id, ai_response, "ai", user_id=user_id, session_id=session_id)
        
        # Responde com ambas as chaves para compatibilidade com diferentes frontends
        return jsonify({"reply": ai_response, "resposta": ai_response})
            
    except Exception as e:
        print(f"Erro no processamento da mensagem: {str(e)}")
        import traceback
        traceback.print_exc()  # Para debug
        return jsonify({"reply": RESPOSTAS_PADRAO["erro_geral"], "resposta": RESPOSTAS_PADRAO["erro_geral"]})

@app.route('/api/chat/history', methods=['GET'])
@app.route('/chat/history', methods=['GET'])
def get_chat_history():
    """Endpoint para recuperar o histórico do chat"""
    try:
        chat_id = request.args.get('chat_id')
        if not chat_id:
            return jsonify({"error": "Chat ID não fornecido"}), 400
            
        user_id = session.get('user_id')
        session_id = session.get('session_id')
        chat_history = session_manager.get_chat_history(chat_id, user_id=user_id, session_id=session_id)
        # Mapear também para formato PT (texto/remetente) para compatibilidade
        historico_pt = []
        for msg in chat_history:
            historico_pt.append({
                'texto': msg.get('text') if 'text' in msg else msg.get('texto'),
                'remetente': msg.get('sender') if 'sender' in msg else msg.get('remetente'),
                'timestamp': msg.get('timestamp')
            })
        return jsonify({"history": chat_history, "historico": historico_pt})
    except Exception as e:
        print(f"Erro ao recuperar histórico: {str(e)}")
        return jsonify({"error": "Erro ao recuperar histórico"}), 500

@app.route('/api/chat/save', methods=['POST'])
@app.route('/chat/save', methods=['POST'])
def save_chat():
    """Endpoint para salvar um chat"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        # Aceita 'title' e 'titulo'
        title = data.get('title') or data.get('titulo')
        messages = data.get('messages', [])
        
        if not chat_id:
            return jsonify({"error": "Chat ID não fornecido"}), 400
            
        # Normalizar mensagens (aceitar 'texto'/'remetente' e converter para 'text'/'sender')
        normalized_messages = []
        for m in messages or []:
            if isinstance(m, dict):
                text_val = m.get('text') if 'text' in m else m.get('texto')
                sender_val = m.get('sender') if 'sender' in m else m.get('remetente')
                normalized_messages.append({
                    'text': text_val,
                    'sender': sender_val,
                    'timestamp': m.get('timestamp')
                })

        # Se houver mensagens normalizadas, salva tudo; se não, apenas atualiza o título (evita apagar histórico)
        if normalized_messages:
            user_id = session.get('user_id')
            session_id = session.get('session_id')
            session_manager.save_chat(chat_id, title, normalized_messages, user_id=user_id, session_id=session_id)
        else:
            if title:
                user_id = session.get('user_id')
                session_id = session.get('session_id')
                session_manager.update_chat_title(chat_id, title, user_id=user_id, session_id=session_id)
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Erro ao salvar chat: {str(e)}")
        return jsonify({"error": "Erro ao salvar chat"}), 500

@app.route('/api/chat/list', methods=['GET'])
@app.route('/chat/list', methods=['GET'])
def list_chats():
    """Endpoint para listar todos os chats"""
    try:
        user_id = session.get('user_id')
        session_id = session.get('session_id')
        chats = session_manager.list_chats(user_id=user_id, session_id=session_id)
        # Adicionar aliases em PT para compatibilidade no mesmo objeto
        chats_with_aliases = []
        for c in chats:
            aliased = dict(c)
            aliased['titulo'] = c.get('title') or c.get('titulo') or 'Conversa'
            aliased['ultimaMensagem'] = c.get('lastMessage') or c.get('ultimaMensagem') or ''
            chats_with_aliases.append(aliased)
        return jsonify({"chats": chats_with_aliases})
    except Exception as e:
        print(f"Erro ao listar chats: {str(e)}")
        return jsonify({"error": "Erro ao listar chats"}), 500

@app.route('/api/chat/delete', methods=['POST'])
@app.route('/chat/delete', methods=['POST'])
def delete_chat():
    """Endpoint para deletar um chat"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        
        if not chat_id:
            return jsonify({"error": "Chat ID não fornecido"}), 400
            
        user_id = session.get('user_id')
        session_id = session.get('session_id')
        if session_manager.delete_chat(chat_id, user_id=user_id, session_id=session_id):
            # Retornar timestamp de atualização para sincronização em tempo real
            return jsonify({
                "status": "success",
                "deleted_at": datetime.utcnow().isoformat()
            })
        else:
            return jsonify({"error": "Chat não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao deletar chat: {str(e)}")
        return jsonify({"error": "Erro ao deletar chat"}), 500

@app.route('/api/chat/update_title', methods=['POST'])
def update_chat_title():
    """Endpoint para atualizar o título de um chat"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        title = data.get('title')
        if not chat_id or not title:
            return jsonify({"error": "ID do chat ou título não fornecido"}), 400
        user_id = session.get('user_id')
        session_manager.update_chat_title(chat_id, title, user_id=user_id)
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Erro ao atualizar título do chat: {str(e)}")
        return jsonify({"error": "Erro ao atualizar título do chat"}), 500

@app.route('/api/suggestions', methods=['POST'])
def submit_suggestion():
    """Registra sugestões de melhorias e informações faltantes do usuário."""
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type deve ser application/json"}), 415
    data = request.get_json() or {}
    descricao = (data.get('descricao') or '').strip()
    categoria = (data.get('categoria') or 'geral').strip()
    contexto = (data.get('contexto') or data.get('context') or '').strip()
    if not descricao:
        return jsonify({"success": False, "error": "Descreva brevemente sua sugestão."}), 400
    suggestion_payload = {
        "categoria": categoria,
        "descricao": descricao,
        "contexto": contexto,
        "chat_id": data.get('chat_id'),
        "ultima_pergunta": data.get('ultima_pergunta'),
        "user_id": session.get('user_id'),
        "username": session.get('username') or session.get('user_nome'),
        "session_id": session.get('session_id')
    }
    try:
        save_suggestion(suggestion_payload)
    except Exception as e:
        print(f"Erro ao salvar sugestão: {e}")
        return jsonify({"success": False, "error": "Não foi possível registrar sua sugestão agora."}), 500
    return jsonify({"success": True, "message": "Obrigado! Sua sugestão foi registrada e nossa equipe irá analisar."})

@app.route('/logout')
def logout():
    """Rota para fazer logout do usuário"""
    session.clear()
    return redirect(url_for('index'))



# Rotas da API de Perfil
@app.route('/api/profile')
def get_profile():
    """Obter dados do perfil do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não logado'})
    
    try:
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'})
        
        profile_data = {
            'id': usuario.id,
            'username': usuario.username,
            'nome': usuario.nome,
            'email': usuario.email,
            'telefone': usuario.telefone,
            'data_nascimento': usuario.data_nascimento.strftime('%Y-%m-%d') if usuario.data_nascimento else None,
            'curso': usuario.curso,
            'bio': usuario.bio,
            'avatar_path': usuario.avatar_path
        }
        
        return jsonify({'success': True, 'profile': profile_data})
    except Exception as e:
        print(f"Erro ao obter perfil: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'})

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    """Atualizar dados do perfil do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não logado'})
    
    try:
        data = request.get_json()
        usuario = Usuario.query.get(session['user_id'])
        
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'})
        
        # Atualizar campos
        if 'nome' in data:
            usuario.nome = data['nome']
        if 'email' in data:
            usuario.email = data['email']
        if 'telefone' in data:
            usuario.telefone = data['telefone']
        if 'data_nascimento' in data and data['data_nascimento']:
            usuario.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
        if 'curso' in data:
            usuario.curso = data['curso']
        if 'bio' in data:
            usuario.bio = data['bio']
        
        db.session.commit()
        
        # Atualizar sessão
        session['user_nome'] = usuario.nome
        session['user_email'] = usuario.email
        
        return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso'})
    except Exception as e:
        print(f"Erro ao atualizar perfil: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erro interno do servidor'})

@app.route('/api/upload-avatar', methods=['POST'])
def upload_avatar():
    """Upload da foto de perfil"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não logado'})
    
    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'})
        
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            # Criar diretório de uploads se não existir
            import os
            upload_dir = 'static/uploads/avatars'
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gerar nome único para o arquivo
            import uuid
            filename = f"{session['user_id']}_{uuid.uuid4().hex[:8]}.{file.filename.rsplit('.', 1)[1].lower()}"
            filepath = os.path.join(upload_dir, filename)
            
            # Salvar arquivo
            file.save(filepath)
            
            # Atualizar banco de dados
            usuario = Usuario.query.get(session['user_id'])
            if usuario:
                usuario.avatar_path = f"/{filepath.replace(os.sep, '/')}"
                usuario.updated_at = datetime.utcnow()
                db.session.commit()
                
                return jsonify({
                    'success': True, 
                    'avatar_url': usuario.avatar_path,
                    'updated_at': usuario.updated_at.isoformat() if usuario.updated_at else datetime.utcnow().isoformat(),
                    'message': 'Avatar atualizado com sucesso'
                })
            else:
                return jsonify({'success': False, 'error': 'Usuário não encontrado'})
        else:
            return jsonify({'success': False, 'error': 'Formato de arquivo não suportado'})
    
    except Exception as e:
        print(f"Erro no upload do avatar: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'})

@app.route('/api/check-updates', methods=['GET'])
def check_updates():
    """Verifica se há atualizações no perfil ou histórico do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não logado'})
    
    try:
        user_id = session['user_id']
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'})
        
        # Buscar último chat atualizado
        from models.sqlalchemy_models import Chat
        last_chat = Chat.query.filter_by(user_id=user_id).order_by(Chat.updated_at.desc()).first()
        
        return jsonify({
            'success': True,
            'profile_updated_at': usuario.updated_at.isoformat() if usuario.updated_at else None,
            'avatar_path': usuario.avatar_path,
            'last_chat_updated_at': last_chat.updated_at.isoformat() if last_chat and last_chat.updated_at else None
        })
    except Exception as e:
        print(f"Erro ao verificar atualizações: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
