"""
Templates de respostas para diferentes tipos de perguntas
"""
from typing import Dict, Any
import random

class ResponseTemplates:
    # Templates para localização
    LOCALIZACAO = [
        "O {nome} {conector} {local}. {referencia}",
        "Você pode encontrar o {nome} {conector} {local}. {referencia}",
        "Para chegar ao {nome}, {conector} {local}. {referencia}",
        "O {nome} está situado {conector} {local}. {referencia}"
    ]

    # Templates para horários
    HORARIO = [
        "O {nome} {conector} {dias}, {periodo}, das {hora_inicio} às {hora_fim}. {observacoes}",
        "O horário de funcionamento do {nome} é {dias}, {periodo}, das {hora_inicio} às {hora_fim}. {observacoes}",
        "Você pode utilizar o {nome} {dias}, {periodo}, das {hora_inicio} às {hora_fim}. {observacoes}"
    ]

    # Templates para cursos
    CURSO = [
        "O curso de {nome} tem duração de {duracao} e {descricao}",
        "Sobre o curso de {nome}: {descricao} A duração é de {duracao}.",
        "O curso de {nome} oferece {descricao} e tem duração de {duracao}."
    ]

    # Templates para valores
    VALOR = [
        "O investimento para o {nome} é de {valor}. {condicoes}",
        "O {nome} tem um valor de {valor}. {condicoes}",
        "Para participar do {nome}, o investimento é de {valor}. {condicoes}"
    ]

    # Templates para contato
    CONTATO = [
        "Para mais informações sobre {assunto}, entre em contato pelo telefone {telefone} ou email {email}.",
        "Você pode obter informações sobre {assunto} através do telefone {telefone} ou email {email}.",
        "Dúvidas sobre {assunto}? Entre em contato: Tel: {telefone} / Email: {email}"
    ]

    # Templates para não encontrado
    NAO_ENCONTRADO = [
        "Desculpe, não encontrei informações específicas sobre {termo}. Posso ajudar com algo mais?",
        "Não tenho dados sobre {termo} no momento. Que tal tentar outra pergunta?",
        "Infelizmente não tenho informações sobre {termo}. Como posso ajudar de outra forma?"
    ]

    @staticmethod
    def get_template(tipo: str, data: Dict[str, Any]) -> str:
        """Retorna um template aleatório do tipo especificado"""
        templates = getattr(ResponseTemplates, tipo.upper(), ResponseTemplates.NAO_ENCONTRADO)
        template = random.choice(templates)
        
        # Trata valores ausentes
        for key in data:
            if data[key] is None:
                data[key] = ""
        
        return template.format(**data)

    @staticmethod
    def format_response(tipo: str, data: Dict[str, Any]) -> str:
        """Formata uma resposta com base no tipo e dados fornecidos"""
        template = ResponseTemplates.get_template(tipo, data)
        
        # Remove espaços extras e pontuação duplicada
        response = " ".join(template.split())
        response = response.replace(" .", ".")
        response = response.replace(" ,", ",")
        
        return response 