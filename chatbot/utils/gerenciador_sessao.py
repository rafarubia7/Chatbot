from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class GerenciadorSessao:
    def __init__(self):
        self.historicos_chat = {}
        self.titulos_chat = {}
        self.arquivo_dados = 'chat_data.json'
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega dados salvos do arquivo"""
        try:
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.historicos_chat = dados.get('historicos', {})
                    self.titulos_chat = dados.get('titulos', {})
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.historicos_chat = {}
            self.titulos_chat = {}
    
    def salvar_dados(self):
        """Salva dados no arquivo"""
        try:
            dados = {
                'historicos': self.historicos_chat,
                'titulos': self.titulos_chat
            }
            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def obter_historico_chat(self, id_chat: str) -> List[Dict]:
        """Obtém o histórico de mensagens de um chat"""
        return self.historicos_chat.get(id_chat, [])
    
    def salvar_chat(self, id_chat: str, titulo: str, mensagens: List[Dict]):
        """Salva um chat com seu histórico"""
        self.historicos_chat[id_chat] = mensagens
        self.titulos_chat[id_chat] = titulo
        self.salvar_dados()
    
    def deletar_chat(self, id_chat: str):
        """Deleta um chat"""
        if id_chat in self.historicos_chat:
            del self.historicos_chat[id_chat]
        if id_chat in self.titulos_chat:
            del self.titulos_chat[id_chat]
        self.salvar_dados()
    
    def listar_chats(self) -> List[Dict]:
        """Lista todos os chats salvos"""
        chats = []
        for id_chat, titulo in self.titulos_chat.items():
            historico = self.historicos_chat.get(id_chat, [])
            ultima_mensagem = ""
            if historico:
                ultima_mensagem = historico[-1].get('texto', '')[:50]
                if len(historico[-1].get('texto', '')) > 50:
                    ultima_mensagem += "..."
            
            chats.append({
                'id': id_chat,
                'titulo': titulo,
                'ultimaMensagem': ultima_mensagem,
                'timestamp': datetime.now().isoformat()
            })
        
        # Ordenar por timestamp (mais recente primeiro)
        chats.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return chats
    
    def adicionar_mensagem(self, id_chat: str, texto: str, remetente: str):
        """Adiciona uma mensagem ao histórico de um chat"""
        if id_chat not in self.historicos_chat:
            self.historicos_chat[id_chat] = []
        
        mensagem = {
            'texto': texto,
            'remetente': remetente,
            'timestamp': datetime.now().isoformat()
        }
        
        self.historicos_chat[id_chat].append(mensagem)
        self.salvar_dados()
    
    def obter_titulo_chat(self, id_chat: str) -> str:
        """Obtém o título de um chat"""
        return self.titulos_chat.get(id_chat, "Nova Conversa")
    
    def atualizar_titulo_chat(self, id_chat: str, titulo: str):
        """Atualiza o título de um chat"""
        self.titulos_chat[id_chat] = titulo
        self.salvar_dados()
