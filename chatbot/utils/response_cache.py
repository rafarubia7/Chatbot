#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de cache para respostas frequentes
"""

import json
import os
import hashlib
from typing import Dict, Optional

class ResponseCache:
    def __init__(self, cache_file: str = "sistema_de_cache.json"):
        self.cache_file = cache_file
        self.cache: Dict[str, str] = {}
        self.load_cache()
    
    def load_cache(self):
        """Carrega o cache do arquivo"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
        except Exception:
            self.cache = {}
    
    def save_cache(self):
        """Salva o cache no arquivo"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def get_cache_key(self, query: str) -> str:
        """Gera uma chave normalizada para a consulta (texto em minúsculas)."""
        return (query or "").strip().lower()
    
    def get(self, query: str) -> Optional[str]:
        """Obtém resposta do cache"""
        key = self.get_cache_key(query)
        return self.cache.get(key)
    
    def set(self, query: str, response: str):
        """Armazena resposta no cache"""
        key = self.get_cache_key(query)
        self.cache[key] = response
        self.save_cache()
    
    def clear(self):
        """Limpa o cache"""
        self.cache = {}
        self.save_cache()

# Instância global do cache
response_cache = ResponseCache()

# Respostas pré-definidas para consultas muito comuns
PREDEFINED_RESPONSES = {
    "ola": "Olá! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",
    "oi": "Oi! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",
    "bom dia": "Bom dia! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",
    "boa tarde": "Boa tarde! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",
    "boa noite": "Boa noite! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",
    "obrigado": "De nada! Fico feliz em ajudar. Estou sempre à disposição para esclarecer suas dúvidas sobre o SENAI São Carlos.",
    "obrigada": "De nada! Fico feliz em ajudar. Estou sempre à disposição para esclarecer suas dúvidas sobre o SENAI São Carlos.",
    "tchau": "Até mais! Foi um prazer ajudar. Se precisar de mais informações sobre o SENAI São Carlos, é só voltar!",
    "ate mais": "Até mais! Foi um prazer ajudar. Se precisar de mais informações sobre o SENAI São Carlos, é só voltar!",
    "qual seu nome": "Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",
    "quem é você": "Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",
    "endereco": "O SENAI São Carlos está localizado na Rua Cândido Padim, 25 - Vila Prado, São Carlos - SP, CEP 13574-320.",
    "telefone": "O telefone/WhatsApp do SENAI São Carlos é (16) 2106-8700.",
    "horario": "O horário de funcionamento da secretaria: Segunda a sexta-feira, das 8h às 20h, e aos sábados, das 8h às 13h e das 14h às 16h.",
    "cursos": "O SENAI São Carlos oferece cursos técnicos, superiores, de aprendizagem industrial e de qualificação. Para informações específicas, entre em contato pelo telefone (16) 2106-8700.",
}

def get_cached_response(query: str) -> Optional[str]:
    """Obtém resposta do cache ou respostas pré-definidas"""
    query_lower = query.lower().strip()
    
    # NÃO usar respostas pré-definidas se for pergunta sobre horários de aulas/professores/turmas
    # (essas perguntas devem ser tratadas pelo sistema de horários)
    from utils.chat_manager import _eh_pergunta_sobre_horarios, _deve_usar_lm_studio
    if _eh_pergunta_sobre_horarios(query):
        # Verificar apenas cache, não respostas pré-definidas
        return response_cache.get(query)
    
    # NÃO usar respostas pré-definidas se a pergunta deveria usar LM Studio
    # (perguntas complexas devem passar pelo LM para respostas mais detalhadas)
    if _deve_usar_lm_studio(query, []):
        # Verificar apenas cache, não respostas pré-definidas
        return response_cache.get(query)
    
    # Verificar respostas pré-definidas primeiro (busca exata primeiro)
    if query_lower in PREDEFINED_RESPONSES:
        resposta = PREDEFINED_RESPONSES[query_lower]
        response_cache.set(query, resposta)
        return resposta
    
    # Verificar respostas pré-definidas (busca por substring) - APENAS para perguntas simples
    # Não usar para perguntas complexas que contêm palavras como "me fale", "quais são", etc.
    palavras_complexas = ['me fale', 'quais são', 'quais sao', 'conte sobre', 'fale sobre', 
                          'explique', 'detalhe', 'informe sobre', 'me informe']
    e_pergunta_simples = not any(palavra in query_lower for palavra in palavras_complexas)
    
    # Casos especiais: perguntas sobre número da secretaria devem usar resposta de telefone
    if 'numero' in query_lower and 'secretaria' in query_lower:
        resposta = PREDEFINED_RESPONSES.get("telefone")
        if resposta:
            response_cache.set(query, resposta)
            return resposta
    
    if e_pergunta_simples:
        import re
        for key, response in PREDEFINED_RESPONSES.items():
            pattern = r"\b" + re.escape(key) + r"\b"
            if re.search(pattern, query_lower):
                response_cache.set(query, response)
                return response
    
    # Verificar cache
    return response_cache.get(query)

def cache_response(query: str, response: str):
    """Armazena resposta no cache"""
    response_cache.set(query, response)
