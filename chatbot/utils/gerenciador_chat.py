import requests
from typing import List, Dict, Optional
import time
from urllib.parse import urlparse, urlunparse
import unicodedata
from fuzzywuzzy import fuzz
from config import URL_LM_STUDIO, NOME_MODELO, TIMEOUT_REQUISICAO, MAX_TENTATIVAS, DELAY_TENTATIVA
from info.respostas import RESPOSTAS_PADRAO
from info.search import obter_informacao_especifica
from info import formatar_info_sao_carlos
from info.base_info import INFO_SENAI_SAO_CARLOS

# Prompts do sistema (sempre usando as informações oficiais do projeto)
_ENDERECO = INFO_SENAI_SAO_CARLOS.get('endereco', '')
_TELEFONE = INFO_SENAI_SAO_CARLOS.get('telefone', '')
_EMAIL = INFO_SENAI_SAO_CARLOS.get('email', '')
_HORARIO = INFO_SENAI_SAO_CARLOS.get('horario_funcionamento', '')

PROMPT_SISTEMA_BASE = f"""Você é um assistente virtual especializado na Escola SENAI São Carlos – "Antonio A. Lobbe", pertencente à rede SENAI São Paulo.
Você deve fornecer informações precisas e úteis sobre a instituição, cursos, processos administrativos e outros assuntos relacionados.

Informações oficiais do SENAI São Carlos (use sempre estes dados do sistema):
- Localização: {_ENDERECO}
- Telefone/WhatsApp: {_TELEFONE}
- Email: {_EMAIL}
- Horário de funcionamento: {_HORARIO}
- Site: https://sp.senai.br/unidade/saocarlos/

Características da unidade:
- Cursos Técnicos: Administração e Gestão
- Cursos Superiores: Mecatrônica Industrial e Análise e Desenvolvimento de Sistemas (noturnos, reconhecidos pelo MEC)
- Cursos de Aprendizagem Industrial gratuitos
- Cursos livres e de aperfeiçoamento profissional (presencial e online)
- Mural de Oportunidades para vagas de estágio e emprego

Responda de forma cordial e objetiva. Se não souber algo específico, indique o contato oficial acima."""

PROMPT_SISTEMA = f"{PROMPT_SISTEMA_BASE}\n\nHistórico da conversa:\n{{historico}}\n\nUsuário: {{mensagem}}\n\nSistema:"

DISCLAIMER = ("\n\nAs informações deste chat são baseadas no site oficial "
              "https://sp.senai.br/unidade/saocarlos/ e na equipe gestora. "
              "Para mais informações, consulte os canais oficiais.")

def _ajustar_url_endpoint(base_url: str, target: str) -> str:
    """Monta URL para endpoint alvo preservando esquema/host/porta da base."""
    try:
        parsed = urlparse(base_url)
        return urlunparse((parsed.scheme or 'http', parsed.netloc, target, '', '', ''))
    except Exception:
        base = base_url[:-1] if base_url.endswith('/') else base_url
        return base + target

def _chamar_lm_studio(prompt: str, stop: Optional[List[str]] = None, temperature: float = 0.7, max_tokens: int = 500) -> Optional[str]:
    """Tenta chamar LM Studio por chat e text completions com retentativas.

    Retorna texto da resposta ou None em falha.
    """
    endpoints = [
        ('auto', URL_LM_STUDIO),
        ('text', _ajustar_url_endpoint(URL_LM_STUDIO, '/v1/completions')),
        ('chat', _ajustar_url_endpoint(URL_LM_STUDIO, '/v1/chat/completions')),
    ]

    attempts = max(1, int(MAX_TENTATIVAS))
    delay_s = max(0, int(DELAY_TENTATIVA))

    for _ in range(attempts):
        for mode, url in endpoints:
            # Tentar chat completion primeiro quando aplicável
            try:
                if mode == 'chat' or url.endswith('/v1/chat/completions'):
                    payload_chat = {
                        "model": NOME_MODELO,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                    if stop:
                        payload_chat["stop"] = stop
                    r = requests.post(url, json=payload_chat, timeout=TIMEOUT_REQUISICAO)
                    if r.status_code == 200:
                        data = r.json() or {}
                        choices = data.get('choices') or []
                        if choices:
                            content = (choices[0].get('message') or {}).get('content')
                            if content:
                                return content
                # Text completion
                url_text = url if mode != 'chat' else _ajustar_url_endpoint(URL_LM_STUDIO, '/v1/completions')
                payload_text = {
                    "model": NOME_MODELO,
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if stop:
                    payload_text["stop"] = stop
                r = requests.post(url_text, json=payload_text, timeout=TIMEOUT_REQUISICAO)
                if r.status_code == 200:
                    data = r.json() or {}
                    text = (data.get('choices', [{}])[0].get('text') or '').strip()
                    if text:
                        return text
            except requests.exceptions.RequestException:
                pass
        if delay_s:
            time.sleep(delay_s)
    return None

def limpar_resposta(texto: str) -> str:
    """Remove caracteres desnecessários da resposta"""
    if not texto:
        return ""
    
    # Remove quebras de linha extras no início e fim
    texto = texto.strip()
    
    # Remove prefixos comuns de IA
    prefixos_para_remover = [
        "Sistema:", "Assistente:", "AI:", "Chatbot:", "Bot:",
        "Resposta:", "Resposta do assistente:", "Resposta da IA:"
    ]
    
    for prefixo in prefixos_para_remover:
        if texto.startswith(prefixo):
            texto = texto[len(prefixo):].strip()
    
    return texto

def _e_small_talk(mensagem_lower: str) -> bool:
    """Detecta agradecimentos, confirmações e despedidas simples."""
    return any(palavra in mensagem_lower for palavra in [
        'obrigado', 'obrigada', 'valeu', 'agradeço', 'agradeco',
        'tchau', 'até mais', 'ate mais', 'flw', 'falou',
        'qual seu nome', 'como você se chama', 'quem é você',
        'beleza', 'blz', 'tá bom', 'ta bom', 'ok', 'show'
    ])

def tratar_nome_usuario(resposta: str, nome_usuario: str) -> str:
    """Personaliza a resposta com o apelido do usuário, assina e anexa disclaimer."""
    assinatura = ""
    apelido = (nome_usuario or '').strip().split()[0] if nome_usuario else None
    if apelido:
        for termo in ["Olá!", "Olá", "Oi!", "Oi", "Bem-vindo", "Bem vindo", "Seja bem-vindo", "Seja bem vindo"]:
            if resposta.strip().startswith(termo):
                resposta = resposta.replace(termo, f"{termo} {apelido}", 1)
                # Força a identidade inline com 'sou o Cadu...' (sou em minúsculo)
                identidade_alvo = "sou o Cadu, assistente virtual do SENAI São Carlos – Escola SENAI 'Antônio Adolpho Lobbe'. Como posso ajudar?"
                variantes = [
                    "Sou o assistente virtual EXCLUSIVO do SENAI São Carlos – Escola SENAI 'Antônio Adolpho Lobbe'. Como posso ajudar?",
                    "Sou o assistente virtual do SENAI São Carlos – Escola SENAI 'Antônio Adolpho Lobbe'. Como posso ajudar?",
                    "Sou o assistente virtual do SENAI São Carlos. Como posso ajudar?",
                    "Sou o assistente virtual EXCLUSIVO do SENAI São Carlos. Como posso ajudar?"
                ]
                for v in variantes:
                    if v in resposta:
                        resposta = resposta.replace(v, identidade_alvo)
                break
    # Normaliza 'Sou o' para 'sou o' em qualquer posição
    if resposta.startswith("Sou o "):
        resposta = "s" + resposta[1:]
    resposta = resposta.replace("\nSou o ", "\nsou o ")
    resposta = resposta.replace(". Sou o ", ". sou o ")
    resposta = resposta.replace("! Sou o ", "! sou o ")
    resposta = resposta.replace("? Sou o ", "? sou o ")
    if resposta.strip().startswith("De nada!"):
            resposta = resposta.replace("De nada!", f"De nada, {apelido}!", 1)
    return resposta + DISCLAIMER

    try:
        mensagem_lower = (mensagem or '').lower()
        nome_usuario = None
        for msg in reversed(historico_chat):
            if msg.get('remetente') == 'usuario' and 'nome_usuario' in msg:
                nome_usuario = msg['nome_usuario']
                break
        if not nome_usuario and hasattr(historico_chat, '_nome_usuario'):
            nome_usuario = getattr(historico_chat, '_nome_usuario')

        if mensagem_lower.startswith('e sobre') and historico_chat and len(historico_chat) >= 2:
            ultima_mensagem = historico_chat[-2].get('texto', '').lower()
            if any(t in ultima_mensagem for t in ['empresa', 'parceira']):
                resposta = (
                    "O SENAI São Carlos realiza diversos eventos importantes ao longo do ano:\n\n"
                    "- Feira de Profissões: Apresentação dos cursos e oportunidades\n"
                    "- Semana da Tecnologia: Palestras, workshops e demonstrações\n"
                    "- Hackathon SENAI: Maratona de inovação e desenvolvimento\n"
                    "- Olimpíada do Conhecimento: Competição de habilidades técnicas\n"
                    "- Workshop com Empresas Parceiras"
                )
                return tratar_nome_usuario(resposta, nome_usuario)
        if any(t in mensagem_lower for t in ['transfer', 'mudar de curso', 'mudar de unidade']):
            resposta = (
                "Para transferência de curso ou unidade no SENAI São Carlos, siga estas orientações:\n\n"
                "1. Entre em contato com a secretaria para obter informações e procedimentos:\n"
                "   - Telefone: (16) 3373-9901\n"
                "   - Email: secretaria.saocarlos@sp.senai.br\n\n"
                "2. Documentos e procedimentos necessários serão informados conforme seu caso específico.\n\n"
                "Horário de atendimento da secretaria para orientações: Segunda a Sexta-feira, das 8h às 20h"
            )
            return tratar_nome_usuario(resposta, nome_usuario)
        if _e_small_talk(mensagem_lower):
            if any(p in mensagem_lower for p in ['obrigado', 'obrigada', 'valeu', 'agradeco', 'agradeço', 'perfeito', 'show', 'ok']):
                return tratar_nome_usuario(RESPOSTAS_PADRAO["agradecimento"], nome_usuario)
            if any(p in mensagem_lower for p in ['tchau', 'até', 'ate', 'flw', 'falou']):
                return tratar_nome_usuario(RESPOSTAS_PADRAO["despedida"], nome_usuario)
            if any(p in mensagem_lower for p in ['qual seu nome', 'como você se chama', 'quem é você']):
                return tratar_nome_usuario(RESPOSTAS_PADRAO["nome"], nome_usuario)
            if any(p in mensagem_lower for p in ['beleza', 'blz', 'tá bom', 'ta bom']):
                return tratar_nome_usuario(RESPOSTAS_PADRAO["confirmacao"], nome_usuario)
            return tratar_nome_usuario(obter_resposta_fallback(mensagem), nome_usuario)
        informacao_especifica = obter_informacao_especifica(mensagem)
        if informacao_especifica:
            return tratar_nome_usuario(informacao_especifica, nome_usuario)
        if 'resposta_intents_rapidas' in globals():
            resposta_rapida = resposta_intents_rapidas(mensagem_lower)
            if resposta_rapida:
                return tratar_nome_usuario(resposta_rapida, nome_usuario)
        if any(palavra in mensagem_lower for palavra in [
            'calendário acadêmico', 'calendario academico', 'calendário escolar', 'calendario escolar',
            'datas letivas', 'calendário', 'calendario', 'agenda', 'agenda escolar', 'datas', 'dias letivos', 'dias de aula', 'cronograma', 'programação escolar', 'programacao escolar', 'horário escolar', 'horario escolar', 'horário de aulas', 'horario de aulas', 'agenda acadêmica', 'agenda academica', 'calendário de aulas', 'calendario de aulas', 'calendário senai', 'calendario senai', 'calendário são carlos', 'calendario sao carlos', 'calendário', 'calendario']):
            return tratar_nome_usuario(RESPOSTAS_PADRAO["calendario_academico"], nome_usuario)
        if not eh_sobre_senai_sao_carlos(mensagem):
            classificacao = classificar_escopo_via_lm(mensagem)
            if classificacao == 'out_of_scope':
                return tratar_nome_usuario(RESPOSTAS_PADRAO["fora_escopo"], nome_usuario)
        try:
            historico_formatado = formatar_historico_chat_para_prompt(historico_chat)
            prompt = PROMPT_SISTEMA.format(
                historico=historico_formatado,
                mensagem=mensagem
            )
            texto = _chamar_lm_studio(prompt, stop=["Usuário:", "Sistema:"])
            if not texto:
                # Fallback amigável quando LM Studio está indisponível
                return tratar_nome_usuario(obter_resposta_fallback(mensagem), nome_usuario)
            resposta_limpa = limpar_resposta(texto)
            if not resposta_limpa.strip():
                return tratar_nome_usuario(RESPOSTAS_PADRAO["erro_geral"], nome_usuario)
            if len(resposta_limpa.strip()) < 10:
                return tratar_nome_usuario(RESPOSTAS_PADRAO["erro_geral"], nome_usuario)
            return tratar_nome_usuario(resposta_limpa, nome_usuario)
        except requests.exceptions.RequestException:
            return tratar_nome_usuario(RESPOSTAS_PADRAO["erro_geral"], nome_usuario)
    except Exception:
        return RESPOSTAS_PADRAO["erro_geral"]
    mensagem_sem_acentos = _remover_acentos(mensagem)
    
    # Palavras-chave relacionadas ao SENAI São Carlos
    palavras_chave_sao_carlos = [
        'senai', 'são carlos', 'sao carlos', 'escola', 'curso', 'cursos',
        'técnico', 'tecnico', 'qualificação', 'qualificacao', 'inscrição',
        'inscricao', 'matrícula', 'matricula', 'horário', 'horario',
        'preço', 'preco', 'valor', 'custo', 'mensalidade', 'biblioteca',
        'refeitório', 'refeitorio', 'secretaria', 'laboratório', 'laboratorio',
        'estágio', 'estagio', 'emprego', 'vaga', 'parceria', 'parcerias',
        'empresa', 'empresas', 'parceiro', 'parceiros', 'parceira', 'parceiras',
        'localização', 'localizacao', 'endereço', 'endereco', 'telefone', 'email', 'contato',
        'aluno', 'alunos', 'competição', 'competicoes', 'competicao', 'competi',
        'tecnologia', 'tecnológicas', 'tecnologicas', 'evento', 'eventos',
        'sala', 'banheiro', 'banheiros', 'hidrante', 'hidrantes', 'extintor', 'extintores',
        'alarme', 'bomba', 'escada', 'elevador', 'laboratório', 'laboratorio',
        'comandos', 'eletrônica', 'eletronica'
    ]
    
    # Palavras-chave específicas do SENAI
    palavras_chave_senai = [
        'senai', 'sena', 'antônio adolpho lobbe', 'antonio adolpho lobbe'
    ]
    
    # Verificar se contém palavras-chave do SENAI
    for palavra in palavras_chave_senai:
        if palavra in mensagem:
            return True
    
    # Verificar se contém palavras-chave gerais de escola/cursos
    for palavra in palavras_chave_sao_carlos:
        if palavra in mensagem:
            return True
    
    # Verificar saudações e perguntas gerais (mais permissivo)
    saudações = ['ola', 'olá', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'quem é vc', 'quem é você']
    for saudacao in saudações:
        if saudacao in mensagem:
            return True
    # Sinais de pergunta/assunto educacional genérico
    if '?' in mensagem_original:
        return True
    if any(t in mensagem for t in [
        'como', 'onde', 'quando', 'horas', 'horario', 'horário', 'inscrição', 'inscricao',
        'curso', 'cursos', 'estágio', 'estagio', 'matrícula', 'matricula', 'valor', 'preço', 'preco'
    ]):
        return True
    
    # Heurística por similaridade (fuzzy) com vocabulário do domínio
    vocabulario_dominios = [
        # Instituição/Unidade
        'senai sao carlos', 'senai', 'escola antonio adolpho lobbe', 'unidade',
        # Áreas e instalações
        'refeitorio', 'biblioteca', 'secretaria', 'laboratorio', 'mecanica', 'eletronica', 'comandos',
        'banheiro', 'hidrante', 'extintor', 'alarme de incendio', 'bomba de incendio', 'escada', 'elevador',
        # Processos/academico
        'curso', 'cursos', 'inscricao', 'matricula', 'horario', 'qualificacao', 'aprendizagem',
        # Atendimento/contatos
        'telefone', 'email', 'contato',
        # Outros
        'empresas parceiras', 'estagio', 'estagios', 'coordenacao de estagio', 'setor de apoio',
    ]

    # Se qualquer item do vocabulário tiver similaridade alta, considera in-scope
    for termo in vocabulario_dominios:
        termo_sem_acentos = _remover_acentos(termo)
        if fuzz.token_set_ratio(mensagem_sem_acentos, termo_sem_acentos) >= 55:
            return True

    # Por padrão, fora de escopo
    return False

def classificar_escopo_via_lm(mensagem: str) -> str:
    """Usa o LM Studio para classificar escopo: retorna 'in_scope', 'out_of_scope' ou 'uncertain'."""
    try:
        prompt_cls = (
            "Classifique a mensagem a seguir como relacionada (in_scope) ou não relacionada (out_of_scope) ao SENAI São Carlos, "
            "uma escola técnica específica. Responda apenas com: in_scope, out_of_scope ou uncertain.\n\n"
            f"Mensagem: {mensagem}\nResposta:"
        )
        texto = _chamar_lm_studio(prompt_cls, stop=["\n"], temperature=0.0, max_tokens=6)
        if not texto:
            return 'uncertain'
        t = (texto or '').strip().lower()
        if 'in_scope' in t or t == 'in' or 'scope: in' in t or t == 'in_scope':
            return 'in_scope'
        if 'out_of_scope' in t or t == 'out' or 'scope: out' in t or t == 'out_of_scope':
            return 'out_of_scope'
        return 'uncertain'
    except Exception:
        return 'uncertain'

def formatar_historico_chat_para_prompt(historico_chat: List[Dict]) -> str:
    """Formata o histórico do chat para incluir no prompt"""
    if not historico_chat:
        return ""
    
    historico_formatado = ""
    for msg in historico_chat[-5:]:  # Últimas 5 mensagens
        remetente = "Usuário" if msg.get('remetente') == 'usuario' else "Sistema"
        texto = msg.get('texto', '')
        historico_formatado += f"{remetente}: {texto}\n"
    
    return historico_formatado

def obter_resposta_fallback(mensagem: str) -> str:
    mensagem_lower = mensagem.lower()
    # Resposta para "Tem aula aos sábados?"
    if any(p in mensagem_lower for p in ['sábado', 'sabado', 'fim de semana']):
        return ("O SENAI São Carlos funciona aos sábados em horário especial. A secretaria atende das 8h às 13h e das 14h às 16h, e a biblioteca das 8h às 12h15 e das 12h30 às 14h15. Para informações sobre aulas específicas, entre em contato com a secretaria.")

    # Resposta para "como faço para chegar lá?"
    if any(frase in mensagem_lower for frase in ['como faço para chegar', 'como chegar lá', 'como chegar la', 'chegar la', 'chegar lá']):
        return (
            "A Escola SENAI São Carlos – 'Antonio A. Lobbe' está localizada na:\n\n"
            "Rua Cândido Padim, 25 – Vila Prado\n"
            "São Carlos/SP, CEP 13574-320\n\n"
            "📞 Telefone/WhatsApp para mais informações: (16) 2106-8700\n"
            "🌐 Site: https://sp.senai.br/unidade/saocarlos/\n\n"
            "Se precisar de orientações específicas sobre como chegar, estou à disposição para ajudar!"
        )

    # Respostas para agradecimentos e confirmações
    if any(p in mensagem_lower for p in ['obrigado', 'valeu', 'perfeito', 'ok']):
        return ("De nada! Estou sempre à disposição para ajudar. Se precisar de mais alguma coisa, é só chamar! Fico feliz em poder ajudar.")

    # Resposta para despedida
    if 'tchau' in mensagem_lower:
        return ("Tchau! Até mais! Sempre que precisar de ajuda, estarei à disposição. Tchau!")

    # Resposta para "qual seu nome?"
    if 'qual seu nome' in mensagem_lower or 'seu nome' in mensagem_lower:
        return ("Sou o assistente virtual do SENAI São Carlos. Meu nome é Luiz Carlos. Como posso ajudar?")

    # Resposta para transferência de curso ou unidade
    if 'transferir' in mensagem_lower or 'transferência' in mensagem_lower or 'transferencia' in mensagem_lower:
        return ("Para informações sobre transferência de curso ou unidade, entre em contato com a secretaria do SENAI São Carlos. Eles poderão fornecer todas as informações, orientações e procedimentos necessários para a transferência. O contato da secretaria está disponível no site.")

    # Resposta para eventos
    if 'evento' in mensagem_lower or 'eventos' in mensagem_lower or 'feira' in mensagem_lower or 'semana' in mensagem_lower or 'hackathon' in mensagem_lower or 'profissões' in mensagem_lower or 'profissoes' in mensagem_lower:
        return ("O SENAI São Carlos realiza vários eventos, como feira de profissões, semana de tecnologia, hackathon e outros eventos. Para saber mais sobre os próximos eventos, consulte nosso site ou entre em contato com a secretaria.")
    # Resposta para perguntas fora do escopo
    termos_senai = ['senai', 'são carlos', 'sao carlos', 'curso', 'cursos', 'secretaria', 'processo', 'matrícula', 'matricula', 'inscrição', 'inscricao', 'horário', 'horario', 'endereço', 'endereco', 'localização', 'localizacao', 'refeitório', 'biblioteca', 'sala', 'laboratório', 'laboratorio']
    if not any(t in mensagem_lower for t in termos_senai):
        return ("Sou o assistente virtual EXCLUSIVO do SENAI São Carlos. Só posso responder perguntas relacionadas à nossa unidade, como cursos, processos administrativos, secretaria, horários, localização, refeitório, biblioteca, salas e laboratórios. "
                "Por favor, reformule sua pergunta incluindo um desses temas para que eu possa te ajudar melhor!")

    # Resposta para "Tem aula aos sábados?"
    if 'sábado' in mensagem_lower or 'sabado' in mensagem_lower or 'fim de semana' in mensagem_lower:
        return ("O SENAI São Carlos não possui aulas regulares aos sábados. O funcionamento normal é de segunda a sexta-feira. Para mais informações sobre horários especiais, entre em contato com a secretaria.")

    # Respostas para agradecimentos e confirmações
    if any(p in mensagem_lower for p in ['obrigado', 'valeu', 'perfeito', 'ok']):
        return ("De nada! Estou sempre à disposição para ajudar. Se precisar de mais alguma coisa, é só chamar!")

    # Resposta para despedida
    if 'tchau' in mensagem_lower:
        return ("Tchau! Até mais! Sempre que precisar de ajuda, estarei por aqui.")

    # Resposta para transferência de curso ou unidade
    if 'transferir' in mensagem_lower or 'transferência' in mensagem_lower or 'transferencia' in mensagem_lower:
        return ("Para informações sobre transferência de curso ou unidade, entre em contato com a secretaria do SENAI São Carlos. Eles poderão orientar sobre o procedimento e fornecer todas as informações necessárias.")

    # Resposta para eventos
    if 'evento' in mensagem_lower or 'eventos' in mensagem_lower or 'feira' in mensagem_lower or 'semana' in mensagem_lower or 'hackathon' in mensagem_lower or 'profissões' in mensagem_lower or 'profissoes' in mensagem_lower:
        return ("O SENAI São Carlos realiza diversos eventos, como feira de profissões, semana de tecnologia e hackathon. Para saber mais sobre os próximos eventos, consulte nosso site ou entre em contato com a secretaria.")
    # Resposta para agradecimentos simples
    if any(palavra in mensagem_lower for palavra in ['obrigado', 'obrigada', 'valeu']):
        return "De nada! Fico à disposição para ajudar sempre que precisar do SENAI São Carlos. Se precisar de ajuda, é só chamar!"

    if any(palavra in mensagem_lower for palavra in ['perfeito', 'ok']):
        return "Que bom que pude ajudar! Se precisar de mais alguma coisa, estou à disposição para ajudar com o que precisar do SENAI São Carlos. De nada! Sempre à disposição para ajudar."

    # Resposta para despedidas
    if any(palavra in mensagem_lower for palavra in ['tchau', 'até mais', 'ate mais']):
        return "Até mais! Tchau! Se precisar de algo do SENAI São Carlos, é só chamar."

    # Resposta para pergunta sobre aula aos sábados
    if any(palavra in mensagem_lower for palavra in ['aula aos sábados', 'aula aos sabados', 'tem aula sábado', 'tem aula sabado', 'sábado', 'sabado', 'fim de semana']):
        return ("O SENAI São Carlos normalmente funciona de segunda a sexta-feira. Em geral, não tem aula aos sábados, mas alguns cursos podem ter atividades especiais ou aulas extras em sábados, conforme o calendário acadêmico. Para informações detalhadas sobre funcionamento aos sábados ou fim de semana, consulte a secretaria.\n\n"
                "⏰ Horário de funcionamento: Segunda a Sexta\n"
                "Se precisar de mais detalhes, posso te ajudar a encontrar o contato da secretaria!"
                "\nPalavras-chave: sábado, sabado, fim de semana, segunda a sexta, não tem aula, funcionamento.")

    # Resposta para pergunta genérica de localização
    if any(palavra in mensagem_lower for palavra in ['chegar lá', 'chegar la', 'como faço para chegar', 'como chegar la', 'como chegar lá']):
        return ("Para chegar ao SENAI São Carlos, vá até a escola localizada na Rua Cândido Padim, 25 - Vila Prado, São Carlos - SP. Caso queira chegar a um local específico dentro da escola, como refeitório, biblioteca ou laboratório, me diga qual é o destino desejado!")

    # Resposta para transferência de curso ou unidade
    if any(palavra in mensagem_lower for palavra in ['transferir', 'transferência', 'transferencia', 'mudança de curso', 'mudança de unidade', 'trocar de curso', 'trocar de unidade']):
        return ("Para solicitar a transferência de curso ou unidade no SENAI São Carlos, entre em contato com a secretaria. Eles fornecerão todas as informações, procedimentos e orientações necessárias para o processo de transferência. Este procedimento é feito diretamente na secretaria.\n\n"
                "Se possível, detalhe qual curso ou unidade deseja transferir para que eu possa te orientar melhor.\n"
                "Palavras-chave: transferência, secretaria, informações, contato, procedimento, orientação.\n"
                "📞 Telefone da secretaria: (16) 3373-9901\n"
                "📧 Email: secretaria.saocarlos@sp.senai.br")

    # Resposta para perguntas sobre eventos
    if any(palavra in mensagem_lower for palavra in ['evento', 'eventos', 'feira', 'semana', 'hackathon', 'profissões', 'profissoes']):
        return ("O SENAI São Carlos realiza diversos eventos ao longo do ano, como eventos, feiras de profissões, semana de tecnologia, hackathons e outras atividades relacionadas a profissões. Se quiser saber sobre um evento específico, por favor, envie uma pergunta mais detalhada! Para saber mais sobre os próximos eventos, consulte o site oficial ou entre em contato com a secretaria.\nPalavras-chave: evento, feira, semana, hackathon, profissões.")
    # Tratamento genérico para perguntas vagas ou que não retornam resposta adequada
    palavras_vagas = ['?', 'não sei', 'nao sei', 'me ajuda', 'ajuda', 'pode ajudar', 'me explique', 'explica', 'explicar', 'detalhe', 'detalhar', 'detalhado', 'detalhada']
    if any(p in mensagem_lower for p in palavras_vagas):
        return "Poderia, por favor, detalhar um pouco mais sua pergunta? Assim consigo te ajudar melhor! Se possível, inclua o tema, local ou contexto desejado."
    # Resposta para perguntas sobre eventos
    if any(palavra in mensagem_lower for palavra in ['evento', 'eventos', 'feira', 'semana', 'hackathon', 'profissões', 'profissoes']):
        return (
            "O SENAI São Carlos realiza diversos eventos ao longo do ano, como feiras de profissões, semana de tecnologia, hackathons e outros encontros voltados para o desenvolvimento profissional e acadêmico. "
            "Para saber mais sobre os próximos eventos, consulte o site oficial ou entre em contato com a secretaria."
        )
    # Resposta para transferência de curso ou unidade
    if any(palavra in mensagem_lower for palavra in ['transferir', 'transferência', 'transferencia', 'mudança de curso', 'mudança de unidade', 'trocar de curso', 'trocar de unidade']):
        return (
            "Para solicitar a transferência de curso ou unidade no SENAI São Carlos, é necessário entrar em contato com a secretaria da escola. "
            "Eles fornecerão todas as informações, procedimentos e orientações necessárias para o processo de transferência.\n\n"
            "📞 Telefone da secretaria: (16) 3373-9901\n"
            "📧 Email: secretaria.saocarlos@sp.senai.br"
        )
    # Resposta genérica para perguntas como "como faço para chegar lá?"
    if any(palavra in mensagem_lower for palavra in ['chegar lá', 'chegar la', 'como faço para chegar', 'como chegar la', 'como chegar lá']):
        return (
            "Para chegar ao SENAI São Carlos, vá até a escola localizada na Rua Cândido Padim, 25 - Vila Prado, São Carlos - SP. "
            "Se precisar de instruções para um local específico dentro da escola, como refeitório, biblioteca ou laboratório, me diga qual é o destino desejado!"
        )
    # Resposta específica para aulas aos sábados
    if any(palavra in mensagem_lower for palavra in ['aula aos sábados', 'aula aos sabados', 'tem aula sábado', 'tem aula sabado', 'sábado', 'sabado', 'fim de semana']):
        return (
            "O SENAI São Carlos normalmente funciona de segunda a sexta-feira, mas alguns cursos podem ter aulas aos sábados, conforme o calendário acadêmico. "
            "Recomendo consultar o calendário oficial ou entrar em contato com a secretaria para informações detalhadas sobre aulas aos sábados e funcionamento nos fins de semana."
            "\n\n⏰ Horário de funcionamento: " + horario + "\n\nSe precisar de mais detalhes, posso te ajudar a encontrar o contato da secretaria!"
        )
    """Sistema de fallback melhorado com respostas mais completas"""
    mensagem_lower = mensagem.lower()
    # Agradecimentos, elogios e encerramentos (resposta mais humanizada)
    if any(p in mensagem_lower for p in [
        'obrigado', 'obrigada', 'valeu', 'agradeço', 'agradeco', 'perfeito', 'ótimo', 'otimo',
        'show', 'beleza', 'de nada?', 'ok', 'tá bom', 'ta bom', 'blz'
    ]):
        return RESPOSTAS_PADRAO["agradecimento"]

    # Despedidas
    if any(p in mensagem_lower for p in [
        'tchau', 'até mais', 'ate mais', 'falou', 'flw', 'até logo', 'ate logo', 'até breve', 'ate breve'
    ]):
        return RESPOSTAS_PADRAO["despedida"]

    endereco = INFO_SENAI_SAO_CARLOS.get('endereco', '')
    telefone = INFO_SENAI_SAO_CARLOS.get('telefone', '')
    email = INFO_SENAI_SAO_CARLOS.get('email', '')
    horario = INFO_SENAI_SAO_CARLOS.get('horario_funcionamento', '')
    
    # Respostas específicas para perguntas comuns
    if any(palavra in mensagem_lower for palavra in ['quem é vc', 'quem é você', 'quem voce', 'quem vc']):
        return RESPOSTAS_PADRAO["nome"]
    
    elif any(palavra in mensagem_lower for palavra in ['onde', 'fica', 'localização', 'localizacao', 'endereço', 'endereco']):
        return RESPOSTAS_PADRAO["endereco"]
    
    elif any(palavra in mensagem_lower for palavra in ['telefone', 'fone', 'contato', 'ligar']):
        return (
            f"Para entrar em contato com o SENAI São Carlos:\n\n"
            f"📞 Telefone/WhatsApp: {telefone}\n"
            f"📧 Email: {email}\n\n"
            f"Horário de atendimento: {horario}\n\n"
            f"Posso te ajudar com mais alguma informação? 😊"
        )
    
    elif any(palavra in mensagem_lower for palavra in ['curso', 'cursos', 'estudar', 'aprender']):
        return """O SENAI São Carlos oferece diversos cursos:

🎓 **Cursos Técnicos:**
- Técnico em Administração e Gestão

🎓 **Cursos Superiores:**
- Tecnologia em Mecatrônica Industrial
- Tecnologia em Análise e Desenvolvimento de Sistemas
(Ambos presenciais, período noturno e reconhecidos pelo MEC)

👨‍🏭 **Cursos de Aprendizagem Industrial (Gratuitos):**
- Assistente Técnico de Vendas (800h)
- Eletricista de Manutenção Eletroeletrônica (1.600h)
- Mecânico de Manutenção (1.600h)
- Operador de Suporte Técnico em TI (800h)
- Auxiliar de Linha de Produção (800h)
- Eletricista Industrial (800h)
- Mecânico de Usinagem (1.600h)
- Soldador (800h)
- Assistente de Logística (980h)
- Assistente Administrativo (400h)
- Montador de Produtos Eletroeletrônicos (800h)

📚 **Cursos Livres e de Aperfeiçoamento:**
- Diversos cursos presenciais e online
- Curta duração
- Áreas técnicas e administrativas

Para informações sobre valores, horários e inscrições, entre em contato pelo telefone (16) 3371-9500 ou email saocarlos@sp.senai.br"""
    
    elif any(palavra in mensagem_lower for palavra in ['inscrição', 'inscricao', 'matrícula', 'matricula', 'inscrever']):
        return f"""Para se inscrever nos cursos do SENAI São Carlos:

📋 **Processo de Inscrição:**
1. Entre em contato pelo telefone {telefone}
2. Ou envie um email para {email}
3. Visite nossa unidade em {endereco}

⏰ **Horário de atendimento:** {horario}

Posso te ajudar com mais alguma informação sobre os cursos? 😊"""
    
    elif any(palavra in mensagem_lower for palavra in ['preço', 'preco', 'valor', 'custo', 'mensalidade', 'quanto custa']):
        return """Os valores dos cursos variam conforme o tipo e duração:

💰 **Informações sobre valores:**
- Cursos de Aprendizagem Industrial: **GRATUITOS** (em parceria com empresas)
- Cursos Técnicos: Valores variam conforme o curso
- Cursos de Qualificação: Valores a partir de R$ 200/mês

📞 Para saber o valor específico do curso que você tem interesse, entre em contato:
- Telefone/WhatsApp: {telefone}
- Email: {email}

💡 **Dica:** O SENAI oferece bolsas de estudo e parcerias com empresas para facilitar o acesso à educação!"""
    
    elif any(palavra in mensagem_lower for palavra in ['horário', 'horario', 'abre', 'fecha', 'funciona']):
        return f"""⏰ **Horários de Funcionamento do SENAI São Carlos:**

Secretaria e Recepção:
- Segunda a sexta-feira: 8h às 20h
- Sábados: 8h às 13h e 14h às 16h

Biblioteca:
- Segunda a quinta-feira: 8h30 às 13h30 e 15h às 22h
- Sextas-feiras: 8h30 às 13h30 e 15h às 21h
- Sábados: 8h às 12h15 e 12h30 às 14h15

📍 **Localização:** {endereco}
📞 **Telefone/WhatsApp:** {telefone}
📧 **Email:** {email}
🌐 **Site:** https://sp.senai.br/unidade/saocarlos/

Posso te ajudar com mais alguma informação? 😊"""
    
    # Benefícios de estudar no SENAI São Carlos (vantagens)
    elif any(palavra in mensagem_lower for palavra in [
        'benefício', 'beneficios', 'benefício', 'beneficios', 'vantagens', 'por que estudar', 'porque estudar', 'por que senai', 'porque senai'
    ]):
        return (
            "Estudar no SENAI São Carlos traz diversos benefícios:\n\n"
            "- Parcerias com empresas da região (estágios e oportunidades)\n"
            "- Laboratórios modernos e bem equipados para aulas práticas\n"
            "- Alta empregabilidade dos alunos formados\n"
            "- Docentes com experiência na indústria e projetos reais\n\n"
            f"Para saber mais, entre em contato pelo telefone {telefone} ou email {email}."
        )
    
    elif any(palavra in mensagem_lower for palavra in ['senai', 'sena', 'o que é']):
        return """🏭 **Sobre o SENAI São Carlos**

A Escola SENAI São Carlos – "Antonio A. Lobbe" pertence à rede SENAI São Paulo e oferece educação profissional de qualidade.

**Nossa unidade oferece:**

🎓 **Formação Completa:**
- Curso Técnico em Administração e Gestão
- Cursos Superiores em Mecatrônica Industrial e ADS
- Cursos de Aprendizagem Industrial Gratuitos
- Cursos Livres e de Aperfeiçoamento

📚 **Estrutura:**
- Biblioteca com horário estendido
- Laboratórios modernos
- Mural de Oportunidades
- Plataforma SENAI Online

🏢 **Infraestrutura Completa:**
- Laboratórios de Mecânica, Eletrônica e Mecatrônica
- Biblioteca
- Refeitório
- Salas de aula modernas

💼 **Oportunidades:**
- Estágios em empresas parceiras
- Bolsas de estudo
- Certificados reconhecidos pelo mercado
- Networking com profissionais da área

📍 **Nossa unidade:** {endereco}
📞 **Contato:** {telefone}

Posso te ajudar com informações sobre cursos específicos? 😊"""
    
    else:
        return f"""Olá! Sou o assistente virtual do SENAI São Carlos. 

Posso te ajudar com informações sobre:
🎓 Cursos técnicos e de qualificação
📍 Localização e horários
📞 Contatos e inscrições
💰 Valores e bolsas
🏭 O que é o SENAI

É só perguntar! 😊

Para informações específicas, entre em contato:
📞 {telefone}
📧 {email}"""

def eh_sobre_senai_sao_carlos(mensagem: str) -> bool:
    """Verifica se a mensagem é sobre o SENAI São Carlos"""
    mensagem_lower = mensagem.lower()
    
    palavras_chave = [
        'senai', 'são carlos', 'sao carlos', 'escola', 'curso', 'antonio a lobbe',
        'técnico', 'tecnico', 'superior', 'mecatrônica', 'mecatronica', 'sistemas',
        'administração', 'administracao', 'gestão', 'gestao', 'aprendizagem',
        'biblioteca', 'secretaria', 'estágio', 'estagio', 'mural', 'online'
    ]
    
    return any(palavra in mensagem_lower for palavra in palavras_chave)

def resposta_intents_rapidas(mensagem_lower: str) -> str:
    """Processa intents rápidas com respostas predefinidas"""
    if 'horário biblioteca' in mensagem_lower or 'horario biblioteca' in mensagem_lower:
        return ("Horário da Biblioteca:\n"
                "- Segunda a quinta-feira: 8h30 às 13h30 e 15h às 22h\n"
                "- Sextas-feiras: 8h30 às 13h30 e 15h às 21h\n"
                "- Sábados: 8h às 12h15 e 12h30 às 14h15")
    
    if 'cursos gratuitos' in mensagem_lower or 'curso gratuito' in mensagem_lower:
        return ("O SENAI São Carlos oferece cursos de Aprendizagem Industrial gratuitos, como:\n"
                "- Assistente Técnico de Vendas (800h)\n"
                "- Eletricista de Manutenção (1.600h)\n"
                "- Mecânico de Manutenção (1.600h)\n"
                "Entre outros. Consulte a secretaria para mais informações!")
    
    return ""

def processar_mensagem(mensagem: str, historico_chat: List[Dict]) -> str:
    """Processa a mensagem e retorna uma resposta"""
    try:
        mensagem_lower = (mensagem or '').lower()
        # Extrair nome do usuário do histórico, se houver
        nome_usuario = None
        if historico_chat:
            for msg in reversed(historico_chat):
                if msg.get('remetente') == 'usuario' and msg.get('nome_usuario'):
                    nome_usuario = msg.get('nome_usuario')
                    break
        
        # Verificar se é uma pergunta de continuação sobre eventos
        if mensagem_lower.startswith('e sobre') and historico_chat and len(historico_chat) >= 2:
            ultima_mensagem = historico_chat[-2].get('texto', '').lower()
            if any(t in ultima_mensagem for t in ['empresa', 'parceira']):
                return tratar_nome_usuario(
                    "A Escola SENAI São Carlos oferece várias oportunidades e serviços:\n\n"
                    "- Cursos Técnicos: Administração e Gestão\n"
                    "- Cursos Superiores: Mecatrônica Industrial e Análise e Desenvolvimento de Sistemas\n"
                    "- Cursos de Aprendizagem Industrial (gratuitos)\n"
                    "- Cursos livres e de aperfeiçoamento profissional\n"
                    "- Plataforma SENAI Online para cursos à distância\n"
                    "- Mural de Oportunidades para vagas de estágio e emprego",
                    nome_usuario
                )
                
        # Verificar se é sobre transferência
        if any(t in mensagem_lower for t in ['transfer', 'mudar de curso', 'mudar de unidade']):
            return tratar_nome_usuario(
                "Para transferência de curso ou unidade no SENAI São Carlos, siga estas orientações:\n\n"
                "1. Entre em contato com a secretaria para obter informações e procedimentos:\n"
                "   - Telefone: (16) 2106-8700\n"
                "   - Email: saocarlos@sp.senai.br\n\n"
                "2. Documentos e procedimentos necessários serão informados conforme seu caso específico.\n\n"
                "Horário de atendimento da secretaria: Segunda a sexta-feira, das 8h às 20h, e aos sábados, das 8h às 13h e das 14h às 16h",
                nome_usuario
            )
                
        # 0) Small-talk: tratar imediatamente (antes de qualquer roteamento)
        if _e_small_talk(mensagem_lower):
            # Agradecimentos
            if any(p in mensagem_lower for p in ['obrigado', 'obrigada', 'valeu', 'agradeco', 'agradeço', 'perfeito', 'show', 'ok']):
                return tratar_nome_usuario(RESPOSTAS_PADRAO["agradecimento"], nome_usuario)
            # Despedidas
            if any(p in mensagem_lower for p in ['tchau', 'até', 'ate', 'flw', 'falou']):
                return tratar_nome_usuario(RESPOSTAS_PADRAO["despedida"], nome_usuario)
            # Nome do bot
            if any(p in mensagem_lower for p in ['qual seu nome', 'como você se chama', 'quem é você']):
                return tratar_nome_usuario(RESPOSTAS_PADRAO["nome"], nome_usuario)
            # Confirmações simples
            if any(p in mensagem_lower for p in ['beleza', 'blz', 'tá bom', 'ta bom']):
                return tratar_nome_usuario(RESPOSTAS_PADRAO["confirmacao"], nome_usuario)
            # Default fallback para outros casos de small talk
            return tratar_nome_usuario(obter_resposta_fallback(mensagem), nome_usuario)

        # 1) Tentar recuperar informação específica primeiro (antes do filtro de escopo)
        informacao_especifica = obter_informacao_especifica(mensagem)
        if informacao_especifica:
            return tratar_nome_usuario(informacao_especifica, nome_usuario)

        # 1b) Intenções rápidas determinísticas
        resposta_rapida = resposta_intents_rapidas(mensagem_lower)
        if resposta_rapida:
            return tratar_nome_usuario(resposta_rapida, nome_usuario)

        # NOVO: Forçar resposta oficial para calendário acadêmico
        if any(palavra in mensagem_lower for palavra in [
            'calendário acadêmico', 'calendario academico', 'calendário escolar', 'calendario escolar',
            'datas letivas', 'calendário', 'calendario', 'agenda', 'agenda escolar', 'datas', 'dias letivos', 'dias de aula', 'cronograma', 'programação escolar', 'programacao escolar', 'horário escolar', 'horario escolar', 'horário de aulas', 'horario de aulas', 'agenda acadêmica', 'agenda academica', 'calendário de aulas', 'calendario de aulas', 'calendário senai', 'calendario senai', 'calendário são carlos', 'calendario sao carlos', 'calendário', 'calendario']):
            return RESPOSTAS_PADRAO["calendario_academico"]

        # 2) Verificar se a pergunta é sobre o SENAI São Carlos (filtro mais permissivo)
        if not eh_sobre_senai_sao_carlos(mensagem):
            classificacao = classificar_escopo_via_lm(mensagem)
            if classificacao == 'out_of_scope':
                return tratar_nome_usuario(RESPOSTAS_PADRAO["fora_escopo"], nome_usuario)
            # in_scope ou uncertain: segue o fluxo para tentar responder

        # 3) Se chegou aqui, é uma pergunta aberta sobre o SENAI: usar LM Studio
        try:
            historico_formatado = formatar_historico_chat_para_prompt(historico_chat)
            prompt = PROMPT_SISTEMA.format(
                historico=historico_formatado,
                mensagem=mensagem
            )
            texto = _chamar_lm_studio(prompt, stop=["Usuário:", "Sistema:"])
            if not texto:
                # Fallback amigável quando LM Studio está indisponível
                return tratar_nome_usuario(obter_resposta_fallback(mensagem), nome_usuario)
            resposta_limpa = limpar_resposta(texto)
            # Garante que a resposta não seja genérica ou vazia
            if not resposta_limpa.strip():
                return tratar_nome_usuario(RESPOSTAS_PADRAO["erro_geral"], nome_usuario)
            if len(resposta_limpa.strip()) < 10:
                return tratar_nome_usuario(RESPOSTAS_PADRAO["erro_geral"], nome_usuario)
            return tratar_nome_usuario(resposta_limpa, nome_usuario)
        except requests.exceptions.RequestException:
            return tratar_nome_usuario(RESPOSTAS_PADRAO["erro_geral"], nome_usuario)
    except Exception:
        return tratar_nome_usuario(RESPOSTAS_PADRAO["erro_geral"], None)
