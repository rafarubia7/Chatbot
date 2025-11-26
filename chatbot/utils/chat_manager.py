import requests
from typing import List, Dict, Optional
import time
import re
from urllib.parse import urlparse, urlunparse
import unicodedata
from fuzzywuzzy import fuzz
from config import URL_LM_STUDIO, NOME_MODELO, TIMEOUT_REQUISICAO, MAX_TENTATIVAS, DELAY_TENTATIVA
from info import RESPOSTAS_PADRAO
from info.search import obter_informacao_especifica
from info import formatar_info_sao_carlos
from info.base_info import INFO_SENAI_SAO_CARLOS
from info.info_manager import (
    get_senai_context_for_lm,
    get_complete_senai_info,
    format_senai_info_for_prompt
)

# Prompts do sistema (sempre usando as informações oficiais do projeto)
_ENDERECO = INFO_SENAI_SAO_CARLOS.get('endereco', '')
_TELEFONE = INFO_SENAI_SAO_CARLOS.get('telefone', '')
_EMAIL = INFO_SENAI_SAO_CARLOS.get('email', '')
_HORARIO = INFO_SENAI_SAO_CARLOS.get('horario_funcionamento', '')

PROMPT_SISTEMA_BASE = f"""Você é o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos.
Você deve fornecer informações precisas e úteis sobre a instituição SENAI, cursos, processos administrativos e outros assuntos relacionados.

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

DISCLAIMER = ("\n\n(As informações deste chat são baseadas no site oficial "
             "https://sp.senai.br/unidade/saocarlos/ e na equipe gestora. "
             "Para mais informações, consulte os canais oficiais.)")

def _ajustar_url_endpoint(base_url: str, target: str) -> str:
    """Monta URL para endpoint alvo preservando esquema/host/porta da base."""
    try:
        parsed = urlparse(base_url)
        return urlunparse((parsed.scheme or 'http', parsed.netloc, target, '', '', ''))
    except Exception:
        base = base_url[:-1] if base_url.endswith('/') else base_url
        return base + target

def _chamar_lm_studio(prompt: str, stop: Optional[List[str]] = None, temperature: float = 0.7, max_tokens: int = 500) -> Optional[str]:
    """Tenta chamar LM Studio por chat e text completions com retentativas melhoradas.

    Retorna texto da resposta ou None em falha.
    """
    # URLs corretas baseadas no exemplo do curl
    base_url = "http://localhost:1234"
    chat_url = f"{base_url}/v1/chat/completions"
    text_url = f"{base_url}/v1/completions"

    attempts = max(1, int(MAX_TENTATIVAS))
    delay_s = max(0, int(DELAY_TENTATIVA))

    for attempt in range(attempts):
        # Tentar chat completion primeiro (recomendado)
        try:
            payload_chat = {
                "model": NOME_MODELO,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens if max_tokens > 0 else -1,  # -1 para sem limite
                "stream": False
            }
            if stop:
                payload_chat["stop"] = stop
            
            headers = {
                "Content-Type": "application/json"
            }
            
            r = requests.post(chat_url, json=payload_chat, headers=headers, timeout=TIMEOUT_REQUISICAO)
            
            # Verificar se a resposta é válida
            if r.status_code == 200:
                try:
                    data = r.json() or {}
                    choices = data.get('choices') or []
                    if choices and len(choices) > 0:
                        choice = choices[0]
                        if isinstance(choice, dict):
                            message = choice.get('message', {})
                            if isinstance(message, dict):
                                content = message.get('content', '')
                                if content and content.strip():
                                    return content.strip()
                except (ValueError, KeyError, TypeError) as e:
                    # Erro ao processar JSON da resposta
                    pass
            else:
                # Log do erro para debug
                print(f"LM Studio Chat Error: {r.status_code} - {r.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("LM Studio Chat Timeout")
        except requests.exceptions.ConnectionError:
            print("LM Studio Chat Connection Error")
        except requests.exceptions.RequestException as e:
            print(f"LM Studio Chat Request Error: {e}")
        except Exception as e:
            print(f"LM Studio Chat Unexpected Error: {e}")
        
        # Tentar text completion como fallback
        try:
            payload_text = {
                "model": NOME_MODELO,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens if max_tokens > 0 else -1,  # -1 para sem limite
                "stream": False
            }
            if stop:
                payload_text["stop"] = stop
            
            headers = {
                "Content-Type": "application/json"
            }
            
            r = requests.post(text_url, json=payload_text, headers=headers, timeout=TIMEOUT_REQUISICAO)
            
            if r.status_code == 200:
                try:
                    data = r.json() or {}
                    choices = data.get('choices', [])
                    if choices and len(choices) > 0:
                        choice = choices[0]
                        if isinstance(choice, dict):
                            text = choice.get('text', '')
                            if text and text.strip():
                                return text.strip()
                except (ValueError, KeyError, TypeError) as e:
                    # Erro ao processar JSON da resposta
                    pass
            else:
                # Log do erro para debug
                print(f"LM Studio Text Error: {r.status_code} - {r.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("LM Studio Text Timeout")
        except requests.exceptions.ConnectionError:
            print("LM Studio Text Connection Error")
        except requests.exceptions.RequestException as e:
            print(f"LM Studio Text Request Error: {e}")
        except Exception as e:
            print(f"LM Studio Text Unexpected Error: {e}")
        
        # Aguardar antes da próxima tentativa
        if attempt < attempts - 1 and delay_s:
            time.sleep(delay_s)
    
    return None

def limpar_resposta(texto: str) -> str:
    """Remove caracteres desnecessários da resposta e melhora formatação"""
    if not texto:
        return ""

    # Remove quebras de linha extras no início e fim
    texto = texto.strip()

    # Remove prefixos comuns de IA
    prefixos_para_remover = [
        "Sistema:", "Assistente:", "AI:", "Chatbot:", "Bot:",
        "Resposta:", "Resposta do assistente:", "Resposta da IA:",
        "Assistente SENAI:", "SENAI:", "Resposta SENAI:"
    ]

    for prefixo in prefixos_para_remover:
        if texto.startswith(prefixo):
            texto = texto[len(prefixo):].strip()
    
    # Melhorar formatação de espaçamentos
    # Remover quebras de linha excessivas (mais de 2 consecutivas)
    texto = re.sub(r'\n\s*\n\s*\n+', '\n\n', texto)
    
    # Remover espaços em branco excessivos
    texto = re.sub(r' +', ' ', texto)
    
    # Remover espaços no início e fim de cada linha
    linhas = texto.split('\n')
    linhas_limpas = []
    for linha in linhas:
        linha_limpa = linha.strip()
        if linha_limpa:  # Não adicionar linhas vazias desnecessárias
            linhas_limpas.append(linha_limpa)
    
    # Reconstruir texto com formatação adequada
    texto = '\n'.join(linhas_limpas)
    
    # Garantir que não há espaços excessivos entre parágrafos
    texto = re.sub(r'\n\s*\n\s*\n', '\n\n', texto)
    
    # Remover espaços no início e fim
    texto = texto.strip()
    
    return texto

def _e_small_talk(mensagem_lower: str) -> bool:
    """Detecta cumprimentos, agradecimentos, confirmações e despedidas simples."""
    mensagem_limpa = mensagem_lower.strip()
    mensagem_sem_acentos = _remover_acentos(mensagem_limpa)
    
    # NÃO tratar como small talk se menciona locais específicos (ex: "area dois", "sala 315")
    palavras_locais = ['area', 'área', 'sala', 'banheiro', 'biblioteca', 'secretaria', 'refeitorio']
    if any(palavra in mensagem_limpa for palavra in palavras_locais):
        return False
    
    # Verificar cumprimentos (exatos ou como início da mensagem)
    cumprimentos = ['olá', 'ola', 'oi', 'bom dia', 'boa tarde', 'boa noite']
    for cumprimento in cumprimentos:
        cumprimento_sem_acentos = _remover_acentos(cumprimento)
        # Verificar exato
        if mensagem_limpa == cumprimento or mensagem_sem_acentos == cumprimento_sem_acentos:
            return True
        # Verificar como início
        if (mensagem_limpa.startswith(cumprimento + ' ') or 
            mensagem_sem_acentos.startswith(cumprimento_sem_acentos + ' ') or
            mensagem_limpa.startswith(cumprimento + '!') or 
            mensagem_sem_acentos.startswith(cumprimento_sem_acentos + '!')):
            return True
        # Verificar se contém (para casos como "olá, tudo bem?")
        if cumprimento in mensagem_limpa or cumprimento_sem_acentos in mensagem_sem_acentos:
            return True
    
    # Verificar outras palavras-chave
    palavras_chave = [
        # Agradecimentos
        'obrigado', 'obrigada', 'valeu', 'agradeço', 'agradeco',
        # Despedidas
        'tchau', 'até mais', 'ate mais', 'flw', 'falou', 'até logo', 'ate logo',
        # Nome do bot
        'qual seu nome', 'como você se chama', 'quem é você',
        # Confirmações simples
        'beleza', 'blz', 'tá bom', 'ta bom', 'ok', 'show'
    ]
    
    # Verificar com e sem acentos
    for palavra in palavras_chave:
        palavra_sem_acentos = _remover_acentos(palavra)
        if palavra in mensagem_limpa or palavra_sem_acentos in mensagem_sem_acentos:
            return True
    
    return False

def tratar_nome_usuario(resposta: str, nome_usuario: str) -> str:
    """Personaliza a resposta com o apelido do usuário e assina como Cadu."""
    assinatura = ""
    if not nome_usuario:
        return resposta + assinatura + DISCLAIMER

    # Prefira apelido (primeira palavra) para soar mais natural
    apelido = (nome_usuario or '').strip().split()[0]
    for termo in ["Olá!", "Olá", "Oi!", "Oi", "Bem-vindo", "Bem vindo", "Seja bem-vindo", "Seja bem vindo"]:
        if resposta.strip().startswith(termo):
            resposta = resposta.replace(termo, f"{termo} {apelido}", 1)
            # Corrigir capitalização: após o nome, a próxima palavra deve começar com minúscula
            # Procura por padrões como "rafael Sou" e converte para "rafael sou"
            # Padrão: nome seguido de espaço e letra maiúscula seguida de minúsculas (ex: "rafael Sou")
            padrao = rf"({re.escape(apelido)})\s+([A-Z][a-z]+)"
            resposta = re.sub(padrao, lambda m: f"{m.group(1)} {m.group(2).lower()}", resposta, count=1)
            # Força a identidade no formato solicitado (sou o Cadu ...)
            identidade_alvo = "sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?"
            variantes = [
                "Sou o assistente virtual EXCLUSIVO do SENAI São Carlos – Escola SENAI 'Antônio Adolpho Lobbe'. Como posso ajudar?",
                "Sou o assistente virtual do SENAI São Carlos – Escola SENAI 'Antônio Adolpho Lobbe'. Como posso ajudar?",
                "Sou o assistente virtual do SENAI São Carlos. Como posso ajudar?",
                "Sou o assistente virtual EXCLUSIVO do SENAI São Carlos. Como posso ajudar?",
                "sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?"
            ]
            for v in variantes:
                if v in resposta:
                    resposta = resposta.replace(v, identidade_alvo)
            break
    # Garantir 'sou o' em minúsculo em casos remanescentes
    if resposta.startswith("Sou o "):
        resposta = "s" + resposta[1:]
    resposta = resposta.replace("\nSou o ", "\nsou o ")
    resposta = resposta.replace(". Sou o ", ". sou o ")
    resposta = resposta.replace("! Sou o ", "! sou o ")
    resposta = resposta.replace("? Sou o ", "? sou o ")
    if resposta.strip().startswith("De nada!"):
        resposta = resposta.replace("De nada!", f"De nada, {apelido}!", 1)
    
    # Verificar se já contém o disclaimer para evitar duplicação
    if DISCLAIMER not in resposta:
        return resposta + DISCLAIMER
    return resposta

def _remover_acentos(texto: str) -> str:
    """Remove acentos de uma string."""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def eh_sobre_senai_sao_carlos(mensagem: str) -> bool:
    """Verifica se a mensagem é sobre o SENAI São Carlos"""
    mensagem_lower = _remover_acentos(mensagem.lower())
    mensagem_original = mensagem.lower() # Manter original para '?'

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
        if palavra in mensagem_lower:
            return True

    # Verificar se contém palavras-chave gerais de escola/cursos
    for palavra in palavras_chave_sao_carlos:
        if palavra in mensagem_lower:
            return True

    # Verificar saudações e perguntas gerais (mais permissivo)
    saudações = ['ola', 'olá', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'quem é vc', 'quem é você']
    for saudacao in saudações:
        if saudacao in mensagem_lower:
            return True
    # Sinais de pergunta/assunto educacional genérico
    if '?' in mensagem_original:
        return True
    if any(t in mensagem_lower for t in [
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
        if fuzz.token_set_ratio(mensagem_lower, termo_sem_acentos) >= 55:
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
    """Formata o histórico do chat para incluir no prompt com melhor contexto"""
    if not historico_chat:
        return ""

    historico_formatado = ""
    # Pegar mais mensagens para melhor contexto (últimas 8 mensagens)
    for msg in historico_chat[-8:]:
        remetente = "Usuário" if msg.get('remetente') == 'usuario' else "Assistente SENAI"
        texto = msg.get('texto', '')
        # Limitar tamanho de cada mensagem para evitar prompt muito longo
        if len(texto) > 200:
            texto = texto[:200] + "..."
        historico_formatado += f"{remetente}: {texto}\n"

    return historico_formatado

def _compactar(texto: str, limite: int = 1800) -> str:
    """Compacta um texto para no máximo 'limite' caracteres preservando início e fim."""
    if not texto:
        return ''
    texto = texto.strip()
    if len(texto) <= limite:
        return texto
    metade = max(0, (limite - 20) // 2)
    return texto[:metade] + "\n...\n" + texto[-metade:]

def _montar_prompt_confiavel(mensagem: str, historico_formatado: str) -> str:
    """Monta um prompt que força o modelo a se basear na base oficial de info/."""
    # Usar informações contextuais mais concisas
    base_confiavel = format_senai_info_for_prompt(mensagem, include_all=False)
    
    # Limitar o tamanho do prompt para evitar overflow de contexto
    max_prompt_length = 2500  # Reduzido para dar mais espaço ao contexto
    
    # Instruções mais específicas para garantir uso das informações
    instrucoes = (
        "Você é o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. "
        "IMPORTANTE: Use APENAS as informações fornecidas abaixo. "
        "Responda de forma cordial, objetiva e profissional. "
        "Mantenha continuidade com a conversa anterior. "
        "Se não souber algo específico, oriente a entrar em contato com os canais oficiais."
    )
    
    # Montar prompt base
    prompt_base = f"{instrucoes}\n\n{base_confiavel}"
    
    # Se o prompt base for muito longo, truncar
    if len(prompt_base) > max_prompt_length:
        prompt_base = prompt_base[:max_prompt_length] + "..."
    
    # Adicionar histórico mais completo para manter continuidade
    historico_limpo = historico_formatado[-300:] if len(historico_formatado) > 300 else historico_formatado
    
    prompt = (
        f"{prompt_base}\n\n"
        f"[CONTEXTO DA CONVERSA]\n{historico_limpo}\n\n"
        f"[PERGUNTA ATUAL]\nUsuário: {mensagem}\n\n"
        f"[RESPOSTA]\nAssistente SENAI:"
    )
    
    return prompt

def _substituir_placeholders(texto: str) -> str:
    """Substitui tokens {endereco}, {telefone}, {email} por valores oficiais."""
    try:
        endereco = INFO_SENAI_SAO_CARLOS.get('endereco', '')
        telefone = INFO_SENAI_SAO_CARLOS.get('telefone', '')
        email = INFO_SENAI_SAO_CARLOS.get('email', '')
        return (texto or '').replace('{endereco}', endereco).replace('{telefone}', telefone).replace('{email}', email)
    except Exception:
        return texto

def _adicionar_informacoes_contato(resposta: str) -> str:
    """Adiciona informações de contato apenas quando especificamente solicitado"""
    try:
        # Verificar se já contém informações de contato
        resposta_lower = resposta.lower()
        tem_contato = any(info in resposta_lower for info in [
            '2106-8700', 'saocarlos@sp.senai.br', 'rua cândido padim',
            'vila prado', '13574-320', 'sp.senai.br/unidade/saocarlos'
        ])
        
        if tem_contato:
            return resposta
        
        # Não adicionar informações de contato automaticamente
        # As informações de contato só serão incluídas quando especificamente solicitadas
        return resposta
        
    except Exception:
        return resposta


def _corrigir_informacoes_banheiro(resposta: str) -> str:
    """Ajusta respostas do modelo que citam banheiro com sala incorreta."""
    try:
        if not resposta:
            return resposta

        lower = resposta.lower()
        if 'banheiro' not in lower:
            return resposta

        if 'sala 204' in lower or 'setor de apoio' in lower or re.search(r'sala\s*20\d', lower):
            correcao = (
                "Os banheiros principais ficam no corredor que começa no refeitório, no andar inferior. "
                "O Banheiro Masculino é a Sala 214 e o Banheiro Feminino é a Sala 213."
            )

            texto = resposta
            texto = re.sub(r'(?im)^.*sala\s*20\d.*$', '', texto)
            texto = re.sub(r'(?i)setor de apoio[^\.\n]*', '', texto)
            texto = re.sub(r'\n{3,}', '\n\n', texto).strip()

            if correcao.lower() not in texto.lower():
                if texto:
                    texto = f"{correcao}\n\n{texto}"
                else:
                    texto = correcao
            return texto
        return resposta
    except Exception:
        return resposta

def _eh_pergunta_sobre_horarios(mensagem: str) -> bool:
    """Detecta se a pergunta é sobre horários/aulas/professores/turmas (NÃO horário de funcionamento)"""
    mensagem_normalizada = _remover_acentos((mensagem or '').lower())
    mensagem_compacta = re.sub(r'\s+', ' ', mensagem_normalizada).strip()
    mensagem_sem_espacos = mensagem_compacta.replace(' ', '')
    
    # IMPORTANTE: NÃO tratar como horário escolar se for pergunta sobre horário de funcionamento
    # (secretaria, biblioteca, instituição em geral)
    horario_funcionamento_keywords = [
        'horario de funcionamento', 'horário de funcionamento', 'funcionamento do senai',
        'horario do senai', 'horário do senai', 'horario da secretaria', 'horário da secretaria',
        'horario da biblioteca', 'horário da biblioteca', 'abre', 'fecha', 'que horas abre',
        'que horas fecha', 'quando abre', 'quando fecha'
    ]
    # Se menciona horário de funcionamento sem mencionar sala/professor/turma específica
    if any(keyword in mensagem_compacta for keyword in horario_funcionamento_keywords):
        # Verificar se NÃO menciona sala/professor/turma (se mencionar, pode ser ambos)
        if not (re.search(r'\b(sala\s*)?(\d{2,3})\b', mensagem_compacta) or 
                'professor' in mensagem_compacta or 
                'turma' in mensagem_compacta or
                'aula' in mensagem_compacta):
            return False  # É horário de funcionamento, NÃO horário escolar
    
    # Verificar se menciona número de sala (3 dígitos) - com ou sem espaço
    # IMPORTANTE: Se a mensagem é APENAS um número (sem outras palavras), tratar como localização, não horário
    if mensagem_compacta.isdigit():
        # Número sozinho = pergunta de localização, não horário
        return False
    
    if re.search(r'\b(sala\s*)?(\d{3})\b', mensagem_compacta) or re.search(r'sala\d{3}', mensagem_sem_espacos) or re.search(r'\b\d{2,3}\b', mensagem_compacta):
        # Se menciona número de sala (mesmo sem palavra "aula", pode ser pergunta sobre horário)
        # Verificar se não é pergunta de localização
        if not any(palavra in mensagem_compacta for palavra in ['onde fica', 'como chegar', 'localização', 'localizacao']):
            # Verificar se há contexto de horário/aula/professor (se não houver, pode ser localização)
            tem_contexto_horario = any(palavra in mensagem_compacta for palavra in [
                'horario', 'horário', 'aula', 'professor', 'turma', 'quem', 'tem aula',
                'vai ter', 'ocupada', 'livre', 'disponivel', 'em uso', 'hoje', 'agora'
            ])
            # Se menciona número de sala E tem contexto de horário, é sobre horário
            if tem_contexto_horario:
                return True
            # Se menciona número mas NÃO tem contexto de horário, pode ser localização (não tratar como horário)
            return False
    
    # Verificar se menciona professores conhecidos (antes de verificar padrões gerais)
    from info.horarios import carregar_horarios_professores
    professores_disponiveis = list(carregar_horarios_professores().keys())
    for prof_nome in professores_disponiveis:
        prof_lower = _remover_acentos(prof_nome.lower())
        if prof_lower in mensagem_compacta:
            # Se menciona professor E tem palavras relacionadas a horário/localização de aula
            if any(palavra in mensagem_compacta for palavra in [
                'onde', 'esta', 'está', 'horario', 'horário', 'aula', 'dando', 'tem'
            ]):
                return True
    
    # Verificar fuzzy matching para professores (erros de digitação)
    try:
        from fuzzywuzzy import fuzz
        for prof_nome in professores_disponiveis:
            prof_lower = _remover_acentos(prof_nome.lower())
            # Verificar se há similaridade suficiente
            if fuzz.ratio(mensagem_compacta, prof_lower) >= 60 or fuzz.partial_ratio(mensagem_compacta, prof_lower) >= 70:
                # Se menciona professor (com similaridade) E tem palavras relacionadas
                if any(palavra in mensagem_compacta for palavra in [
                    'onde', 'esta', 'está', 'horario', 'horário', 'aula', 'dando', 'tem', 'professor', 'prof'
                ]):
                    return True
    except ImportError:
        pass
    
    # Verificar se menciona turmas conhecidas
    from info.horarios import carregar_horarios_turmas
    turmas_disponiveis = list(carregar_horarios_turmas().keys())
    for turma_nome in turmas_disponiveis:
        # Normalizar nome da turma para busca
        turma_normalizada = _remover_acentos(turma_nome.lower().replace('_', ' ').replace('-', ' '))
        turma_sem_espacos = turma_normalizada.replace(' ', '')
        mensagem_sem_espacos_turma = mensagem_compacta.replace(' ', '').replace('-', '').replace('_', '')
        
        # Verificar se menciona turma (com ou sem espaços/hífens)
        if (turma_normalizada in mensagem_compacta or 
            turma_sem_espacos in mensagem_sem_espacos_turma or
            _remover_acentos(turma_nome.lower()) in mensagem_sem_espacos_turma):
            # Se menciona turma, é pergunta sobre horário
            return True
    
    # Verificar se menciona período do dia (manhã, tarde, noite) combinado com sala/aula
    periodos_dia = ['manha', 'manhã', 'tarde', 'noite', 'manha', 'manhã']
    tem_periodo = any(periodo in mensagem_compacta for periodo in periodos_dia)
    # Se menciona sala + período OU quem dá aula + período, é sobre horário escolar
    if (re.search(r'\b(sala\s*)?(\d{2,3})\b', mensagem_compacta) or 'sala' in mensagem_compacta) and tem_periodo:
        return True
    if ('quem' in mensagem_compacta and 'aula' in mensagem_compacta) and tem_periodo:
        return True
    
    perguntas_horario = [
        # Padrões diretos de horário
        'qual professor', 'qual turma', 'onde está o professor', 'onde esta o professor', 
        'professor está', 'professor esta', 'turma está', 'turma esta', 'que dia', 
        'que período', 'que periodo', 'horário', 'horario', 'horarios', 'horários',
        # Padrões sobre quem dá aula
        'quem vai dar aula', 'quem vai dar', 'quem dá aula', 'quem da aula',
        'quem está dando aula', 'quem esta dando aula', 'quem vai estar',
        'quem está na sala', 'quem esta na sala', 'quem tem aula',
        'quem vai estar na sala', 'quem esta na sala', 'quem da aula na',
        'quem dá aula na', 'quem da aula em', 'quem dá aula em',
        # Padrões sobre aulas
        'tem aula', 'vai ter aula', 'tem professor', 'tem turma',
        'está ocupada', 'esta ocupada', 'está livre', 'esta livre',
        'está em uso', 'esta em uso', 'está sendo usada', 'esta sendo usada',
        'quem usa', 'quem está usando', 'quem esta usando',
        # Padrões sobre hoje/agora
        'hoje', 'agora', 'neste momento', 'neste horário', 'neste horario',
        'nesta hora', 'agora mesmo',
        # Padrões sobre ocupação
        'ocupada', 'livre', 'disponível', 'disponivel', 'em uso',
        'sendo usada', 'sendo utilizada'
    ]
    
    return any(pergunta in mensagem_compacta for pergunta in perguntas_horario)

def _deve_usar_lm_studio(mensagem: str, historico_chat: List[Dict]) -> bool:
    """
    Usa o LM Studio para TODAS as perguntas EXCETO:
    - Perguntas de localização (onde fica, como chegar, etc.)
    - Small talk (cumprimentos, despedidas, agradecimentos)
    - Perguntas sobre horários ESCOLARES (aulas, professores, turmas) - para não pesar no LM Studio
    - Perguntas sobre horário de funcionamento da secretaria/biblioteca (fallback responde)
    """
    mensagem_lower = mensagem.lower()
    mensagem_normalizada = _remover_acentos(mensagem_lower)
    
    # NÃO usar LM Studio para perguntas de localização
    if _eh_pergunta_localizacao(mensagem):
        return False
    
    # NÃO usar LM Studio para small talk (cumprimentos, despedidas, agradecimentos)
    if _e_small_talk(mensagem_lower):
        return False
    
    # NÃO usar LM Studio para perguntas sobre horários ESCOLARES (aulas, professores, turmas)
    if _eh_pergunta_sobre_horarios(mensagem):
        return False
    
    # NÃO usar LM Studio para perguntas sobre horário de funcionamento da secretaria/biblioteca
    # (fallback já tem essa informação)
    horario_funcionamento_keywords = [
        'horario de funcionamento', 'horário de funcionamento', 'funcionamento do senai',
        'horario do senai', 'horário do senai', 'horario da secretaria', 'horário da secretaria',
        'horario da biblioteca', 'horário da biblioteca', 'abre', 'fecha', 'que horas abre',
        'que horas fecha', 'quando abre', 'quando fecha'
    ]
    
    # NÃO usar LM Studio para perguntas simples sobre contato/telefone/número
    # (fallback já tem essas informações)
    contato_keywords = [
        'telefone', 'fone', 'contato', 'ligar', 'numero da secretaria', 'número da secretaria',
        'qual o numero', 'qual o número', 'numero do senai', 'número do senai'
    ]
    if any(keyword in mensagem_normalizada for keyword in contato_keywords):
        # Verificar se é uma pergunta simples (não complexa)
        palavras_complexas = ['me fale', 'quais são', 'quais sao', 'conte sobre', 'fale sobre', 
                              'explique', 'detalhe', 'informe sobre', 'me informe']
        e_pergunta_simples = not any(palavra in mensagem_normalizada for palavra in palavras_complexas)
        if e_pergunta_simples:
            return False
    if any(keyword in mensagem_normalizada for keyword in horario_funcionamento_keywords):
        # Verificar se NÃO menciona sala/professor/turma específica
        if not (re.search(r'\b(sala\s*)?(\d{2,3})\b', mensagem_normalizada) or 
                'professor' in mensagem_normalizada or 
                'turma' in mensagem_normalizada or
                'aula' in mensagem_normalizada):
            return False  # É horário de funcionamento, usar fallback
    
    # Todo o resto vai para LM Studio (incluindo perguntas gerais sobre cursos, diferenciais, etc.)
    return True

def _eh_pergunta_sobre_senai_geral(mensagem: str) -> bool:
    """
    Detecta se é uma pergunta geral sobre o SENAI que deve ser respondida pelo LM Studio
    com base nas informações do módulo info/
    """
    mensagem_lower = mensagem.lower()
    
    # Palavras-chave que indicam perguntas gerais sobre o SENAI
    palavras_chave_senai_geral = [
        'o que é o senai', 'o que e o senai', 'sobre o senai', 'me fale sobre o senai',
        'me explique sobre o senai', 'conte sobre o senai', 'fale sobre o senai',
        'senai são carlos', 'senai sao carlos', 'escola senai', 'unidade senai',
        'antônio adolpho lobbe', 'antonio adolpho lobbe', 'antônio adolfo lobbe',
        'antonio adolfo lobbe', 'quem é o senai', 'quem e o senai',
        'o que faz o senai', 'o que faz o senai', 'para que serve o senai',
        'missão do senai', 'missao do senai', 'objetivo do senai',
        'história do senai', 'historia do senai', 'fundação do senai',
        'fundacao do senai', 'quando foi criado o senai', 'quando foi fundado o senai'
    ]
    
    # Verificar se contém alguma das palavras-chave
    for palavra in palavras_chave_senai_geral:
        if palavra in mensagem_lower:
            return True
    
    # Verificar padrões de pergunta geral (incluindo continuações)
    padroes_pergunta_geral = [
        'me fale mais sobre', 'me explique mais sobre', 'conte mais sobre',
        'fale mais sobre', 'me diga mais sobre', 'quero saber mais sobre',
        'me informe sobre', 'me conte sobre', 'me explique sobre',
        'me fale mais', 'conte mais', 'fale mais', 'me diga mais',
        'quero saber mais', 'me informe mais', 'me conte mais'
    ]
    
    # Verificar padrões de continuação (mesmo sem mencionar SENAI explicitamente)
    for padrao in padroes_pergunta_geral:
        if padrao in mensagem_lower:
            # Se menciona SENAI, definitivamente é sobre SENAI
            if any(senai_word in mensagem_lower for senai_word in ['senai', 'sena']):
                return True
            # Se é uma pergunta de continuação curta, provavelmente é sobre SENAI
            if len(mensagem_lower.strip()) < 20:
                return True
    
    return False


def _eh_pergunta_localizacao(mensagem: str) -> bool:
    """Detecta perguntas explicitamente sobre localização/direções."""
    mensagem_normalizada = _remover_acentos((mensagem or '').lower())
    mensagem_compacta = re.sub(r'\s+', ' ', mensagem_normalizada).strip()
    tokens = mensagem_compacta.split()

    if not mensagem_compacta:
        return False

    # Somente números (ex: "214") devem ser tratados como pedido de localização
    if mensagem_compacta.isdigit():
        return True

    # NÃO tratar como localização se for pergunta sobre horários/aulas/professores
    perguntas_horario = [
        # Padrões diretos de horário
        'qual professor', 'qual turma', 'onde está o professor', 'onde esta o professor', 
        'professor está', 'professor esta', 'turma está', 'turma esta', 'que dia', 
        'que período', 'que periodo', 'horário', 'horario', 'horarios', 'horários',
        # Padrões sobre quem dá aula
        'quem vai dar aula', 'quem vai dar', 'quem dá aula', 'quem da aula',
        'quem está dando aula', 'quem esta dando aula', 'quem vai estar',
        'quem está na sala', 'quem esta na sala', 'quem tem aula',
        'quem vai estar na sala', 'quem esta na sala',
        # Padrões sobre aulas
        'tem aula', 'vai ter aula', 'tem professor', 'tem turma',
        'está ocupada', 'esta ocupada', 'está livre', 'esta livre',
        'está em uso', 'esta em uso', 'está sendo usada', 'esta sendo usada',
        'quem usa', 'quem está usando', 'quem esta usando',
        # Padrões sobre hoje/agora
        'hoje', 'agora', 'neste momento', 'neste horário', 'neste horario',
        'nesta hora', 'agora mesmo',
        # Padrões sobre ocupação
        'ocupada', 'livre', 'disponível', 'disponivel', 'em uso',
        'sendo usada', 'sendo utilizada'
    ]
    if any(pergunta in mensagem_compacta for pergunta in perguntas_horario):
        return False

    # Perguntas que claramente falam de conteúdo devem ser tratadas pelo LM Studio
    gatilhos_conteudo = ['o que tem', 'que tem', 'que existe', 'o que ha', 'que coisas tem']
    if any(gatilho in mensagem_compacta for gatilho in gatilhos_conteudo):
        return False

    frases_localizacao = [
        'onde fica', 'onde esta', 'onde está', 'fica onde', 'como chegar', 'como chego',
        'onde encontro', 'como encontro', 'sabe chegar', 'sabe encontrar', 'pode indicar o caminho'
    ]

    termos_localizacao = ['localizacao', 'localiza', 'localidade']

    # Verificação especial para "setor de apoio" e outras localizações específicas
    locais_especificos = ['setor de apoio', 'setor apoio', 'apoio', 'qualidade de vida', 
                          'sala 204', '204', 'biblioteca', 'secretaria', 'refeitorio', 
                          'banheiro', 'coordenacao', 'coordenação']
    
    # Se a mensagem contém uma frase de localização E um local específico, é definitivamente localização
    for frase in frases_localizacao:
        if frase in mensagem_compacta:
            # Verificar se menciona algum local específico
            tem_local_especifico = any(local in mensagem_compacta for local in locais_especificos)
            if tem_local_especifico:
                return True
            
            # Verificar se é pergunta composta (tem tanto localização quanto conteúdo)
            tem_contexto_extra = any(token in ['curso', 'cursos', 'valor', 'valores', 'quanto', 'horario', 'capacidade'] for token in tokens)
            # Verificar se há perguntas sobre conteúdo (ex: "quais são os cursos")
            tem_pergunta_conteudo = any(palavra in mensagem_compacta for palavra in ['quais são', 'quais sao', 'me fale sobre', 'conte sobre', 'fale sobre'])
            # Se for pergunta composta com conteúdo, deixar para LM Studio
            if tem_pergunta_conteudo or (tem_contexto_extra and len(tokens) > 5):
                return False
            return True

    # Detectar sinônimos aproximados (erros de digitação leves)
    palavras_chave_locais = [
        'banheiro', 'sanitario', 'sala', 'biblioteca', 'secretaria',
        'refeitorio', 'laboratorio', 'hidrante', 'extintor', 'coordenacao', 'auditorio',
        'area', 'área', 'area dois', 'área dois', 'area 2', 'área 2',
        'setor de apoio', 'setor apoio', 'apoio', 'qualidade de vida', 'analise de qualidade de vida',
        'análise de qualidade de vida', 'sala 204', '204'
    ]

    numero_presente = bool(re.search(r'\b\d{2,3}\b', mensagem_compacta))

    def possui_palavra_chave(chave: str) -> bool:
        if chave in mensagem_compacta:
            return True
        for token in tokens:
            if fuzz.ratio(token, chave) >= 85:
                return True
        return False

    # Verificar se tem palavra-chave local
    tem_palavra_local = any(possui_palavra_chave(chave) for chave in palavras_chave_locais)
    
    # Verificar se menciona "area dois" especificamente (caso especial)
    area_dois_keywords = ['area dois', 'área dois', 'area 2', 'área 2', 'area ii', 'área ii']
    tem_area_dois = any(keyword in mensagem_compacta for keyword in area_dois_keywords)
    
    # Se tem palavra-chave local E não é pergunta sobre conteúdo/horário, tratar como localização
    if tem_palavra_local or tem_area_dois:
        # Verificar se NÃO é pergunta sobre conteúdo (ex: "o que tem no banheiro")
        nao_e_conteudo = not any(palavra in mensagem_compacta for palavra in [
            'o que tem', 'que tem', 'que existe', 'o que ha', 'que coisas tem',
            'conteudo', 'conteúdo', 'tem o que', 'tem que'
        ])
        # Verificar se NÃO é pergunta sobre horário
        nao_e_horario = not any(palavra in mensagem_compacta for palavra in [
            'horario', 'horário', 'que horas', 'quando', 'periodo', 'período'
        ])
        # Se tem número OU é uma pergunta simples sobre local (ex: "banheiro masculino", "area dois")
        # OU menciona especificamente "area dois"
        if tem_area_dois or (numero_presente or len(tokens) <= 3) and nao_e_conteudo and nao_e_horario:
            return True

    if any(termo in mensagem_compacta for termo in termos_localizacao) and tem_palavra_local:
        return True

    if numero_presente and tem_palavra_local:
        return True

    return False


def _gerar_resposta_rica_sobre_senai(mensagem: str) -> str:
    """
    Gera uma resposta rica sobre o SENAI usando informações do módulo info/
    quando o LM Studio não está disponível
    """
    try:
        from info.info_manager import info_manager
        
        mensagem_lower = mensagem.lower()
        
        # Determinar o tipo de pergunta e gerar resposta apropriada
        if any(word in mensagem_lower for word in ['curso', 'cursos', 'técnico', 'superior', 'aprendizagem']):
            # Pergunta sobre cursos
            return f"""🏭 **Sobre o SENAI São Carlos**

A Escola SENAI São Carlos – "Antonio A. Lobbe" pertence à rede SENAI São Paulo e oferece educação profissional de qualidade.

{info_manager.get_courses_info()}

Para mais informações específicas sobre cursos, entre em contato conosco! 😊"""
        
        elif any(word in mensagem_lower for word in ['infraestrutura', 'laboratório', 'laboratorio', 'biblioteca', 'refeitório']):
            # Pergunta sobre infraestrutura
            return f"""🏭 **Sobre o SENAI São Carlos**

A Escola SENAI São Carlos – "Antonio A. Lobbe" pertence à rede SENAI São Paulo e oferece educação profissional de qualidade.

{info_manager.get_infrastructure_info()}

Venha nos visitar e conhecer nossa estrutura! 😊"""
        
        elif any(word in mensagem_lower for word in ['parceria', 'empresa', 'estágio', 'estagio', 'oportunidade']):
            # Pergunta sobre parcerias
            return f"""🏭 **Sobre o SENAI São Carlos**

A Escola SENAI São Carlos – "Antonio A. Lobbe" pertence à rede SENAI São Paulo e oferece educação profissional de qualidade.

{info_manager.get_partnerships_info()}

Conectamos nossos alunos às melhores oportunidades do mercado! 😊"""
        
        elif any(word in mensagem_lower for word in ['evento', 'feira', 'hackathon', 'semana', 'atividade']):
            # Pergunta sobre eventos
            return f"""🏭 **Sobre o SENAI São Carlos**

A Escola SENAI São Carlos – "Antonio A. Lobbe" pertence à rede SENAI São Paulo e oferece educação profissional de qualidade.

{info_manager.get_events_info()}

Participe dos nossos eventos e atividades! 😊"""
        
        else:
            # Resposta geral completa
            return f"""🏭 **Sobre o SENAI São Carlos**

A Escola SENAI São Carlos – "Antonio A. Lobbe" pertence à rede SENAI São Paulo e oferece educação profissional de qualidade.

{info_manager.get_basic_info()}

{info_manager.get_courses_info()}

{info_manager.get_differentials_info()}

Estamos prontos para ajudar você a construir seu futuro profissional! 😊"""
    
    except Exception:
        # Fallback para resposta básica se houver erro
        endereco = INFO_SENAI_SAO_CARLOS.get('endereco', '')
        telefone = INFO_SENAI_SAO_CARLOS.get('telefone', '')
        return f"""🏭 **Sobre o SENAI São Carlos**

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

def obter_resposta_fallback(mensagem: str) -> str:
    """Sistema de fallback melhorado com respostas mais completas"""
    mensagem_lower = mensagem.lower()
    # Agradecimentos, elogios e encerramentos (resposta mais humanizada)
    if any(p in mensagem_lower for p in [
        'obrigado', 'obrigada', 'valeu', 'agradeço', 'agradeco', 'perfeito', 'ótimo', 'otimo',
        'show', 'beleza', 'de nada?', 'ok', 'tá bom', 'ta bom', 'blz'
    ]):
        return "De nada! Fico à disposição para ajudar com o que precisar do SENAI São Carlos. 😊"

    # Despedidas
    if any(p in mensagem_lower for p in [
        'tchau', 'até mais', 'ate mais', 'falou', 'flw', 'até logo', 'ate logo', 'até breve', 'ate breve'
    ]):
        return "Até mais! Se precisar de algo do SENAI São Carlos, é só chamar. 👋"

    endereco = INFO_SENAI_SAO_CARLOS.get('endereco', '')
    telefone = INFO_SENAI_SAO_CARLOS.get('telefone', '')
    email = INFO_SENAI_SAO_CARLOS.get('email', '')
    horario = INFO_SENAI_SAO_CARLOS.get('horario_funcionamento', '')

    # Respostas sobre horários (fallback para não pesar no LM Studio)
    if _eh_pergunta_sobre_horarios(mensagem):
        import re
        from info.horarios import (
            buscar_horario_sala, formatar_horario_sala_para_resposta,
            buscar_horario_professor, formatar_horario_professor_para_resposta,
            buscar_horario_turma, formatar_horario_turma_para_resposta,
            carregar_horarios_professores, carregar_horarios_turmas
        )
        
        # 1) Tentar extrair número da sala da pergunta (com ou sem espaço após "sala")
        numero_sala = None
        # Primeiro, tentar padrão com espaço (ex: "sala 315")
        numeros_sala = re.findall(r'\b(sala\s*)?(\d{3})\b', mensagem)
        if numeros_sala:
            # Extrair o número da tupla retornada
            numero_sala = numeros_sala[0][1] if isinstance(numeros_sala[0], tuple) else numeros_sala[0]
        else:
            # Tentar sem espaço (ex: "sala315")
            numeros_sala = re.findall(r'sala(\d{3})', mensagem.lower())
            if numeros_sala:
                numero_sala = numeros_sala[0]
        
        if numero_sala:
            horarios_sala = buscar_horario_sala(numero_sala)
            if horarios_sala:
                horarios_formatados = formatar_horario_sala_para_resposta(numero_sala, horarios_sala)
                resposta = (
                    f"{horarios_formatados}\n"
                    "Para consultar horarios atualizados e substituicoes, acesse:\n"
                    '<a href="https://senaisaocarlos.edupage.org/timetable/" style="color: red; text-decoration: underline;" target="_blank" rel="noopener noreferrer">https://senaisaocarlos.edupage.org/timetable/</a>\n\n'
                    f"Telefone: {telefone}\n"
                    f"Email: {email}"
                )
                return resposta
        
        # 2) Tentar extrair nome do professor da pergunta
        mensagem_lower = mensagem.lower()
        mensagem_normalizada = _remover_acentos(mensagem_lower)
        # Padrões comuns: "onde está o professor X", "professor X", "horário do professor X"
        professores_disponiveis = list(carregar_horarios_professores().keys())
        
        # Primeiro, tentar busca exata
        for prof_nome in professores_disponiveis:
            prof_lower = prof_nome.lower()
            prof_normalizado = _remover_acentos(prof_lower)
            # Verificar se o nome do professor está na mensagem (case-insensitive e sem acentos)
            if (prof_lower in mensagem_lower or 
                prof_normalizado in mensagem_normalizada or
                any(palavra in mensagem_lower for palavra in [
                    f'professor {prof_lower}', f'prof {prof_lower}', f'prof. {prof_lower}'
                ])):
                horarios_prof = buscar_horario_professor(prof_nome)
                if horarios_prof:
                    horarios_formatados = formatar_horario_professor_para_resposta(prof_nome, horarios_prof)
                    resposta = (
                        f"{horarios_formatados}\n"
                        "Para consultar horarios atualizados e substituicoes, acesse:\n"
                        '<a href="https://senaisaocarlos.edupage.org/timetable/" style="color: red; text-decoration: underline;" target="_blank" rel="noopener noreferrer">https://senaisaocarlos.edupage.org/timetable/</a>\n\n'
                        f"Telefone: {telefone}\n"
                        f"Email: {email}"
                    )
                    return resposta
        
        # Se não encontrou com busca exata, tentar fuzzy matching
        try:
            from fuzzywuzzy import fuzz
            melhor_match = None
            melhor_score = 0
            for prof_nome in professores_disponiveis:
                prof_lower = prof_nome.lower()
                # Verificar similaridade com o nome do professor na mensagem
                score = fuzz.partial_ratio(prof_lower, mensagem_lower)
                if score > melhor_score and score >= 70:  # Threshold de 70%
                    melhor_score = score
                    melhor_match = prof_nome
            
            if melhor_match:
                horarios_prof = buscar_horario_professor(melhor_match)
                if horarios_prof:
                    horarios_formatados = formatar_horario_professor_para_resposta(melhor_match, horarios_prof)
                    resposta = (
                        f"{horarios_formatados}\n"
                        "Para consultar horarios atualizados e substituicoes, acesse:\n"
                        '<a href="https://senaisaocarlos.edupage.org/timetable/" style="color: red; text-decoration: underline;" target="_blank" rel="noopener noreferrer">https://senaisaocarlos.edupage.org/timetable/</a>\n\n'
                        f"Telefone: {telefone}\n"
                        f"Email: {email}"
                    )
                    return resposta
        except ImportError:
            pass  # Se fuzzywuzzy não estiver disponível, continuar sem fuzzy matching
        
        # 3) Tentar extrair nome da turma da pergunta
        turmas_disponiveis = list(carregar_horarios_turmas().keys())
        for turma_nome in turmas_disponiveis:
            # Normalizar nome da turma para busca (remover caracteres especiais)
            turma_normalizada = turma_nome.lower().replace('_', ' ').replace('-', ' ')
            turma_sem_espacos = turma_normalizada.replace(' ', '').replace('-', '').replace('_', '')
            # Normalizar mensagem também (remover espaços, hífens, underscores)
            mensagem_sem_espacos = mensagem_lower.replace(' ', '').replace('-', '').replace('_', '')
            mensagem_normalizada_turma = _remover_acentos(mensagem_sem_espacos)
            turma_normalizada_sem_espacos = _remover_acentos(turma_sem_espacos)
            
            # Verificar se o nome da turma está na mensagem (com ou sem espaços/hífens/underscores)
            if (turma_normalizada in mensagem_lower or 
                turma_sem_espacos in mensagem_sem_espacos or
                turma_normalizada_sem_espacos in mensagem_normalizada_turma or
                any(palavra in mensagem_lower for palavra in [
                    f'turma {turma_normalizada}', f'classe {turma_normalizada}',
                    f'turma {turma_nome.lower()}', f'classe {turma_nome.lower()}'
                ])):
                horarios_turma = buscar_horario_turma(turma_nome)
                if horarios_turma:
                    # Formatar nome da turma para exibição
                    turma_display = turma_nome.replace('_', '-').upper()
                    horarios_formatados = formatar_horario_turma_para_resposta(turma_display, horarios_turma)
                    resposta = (
                        f"{horarios_formatados}\n"
                        "Para consultar horarios atualizados e substituicoes, acesse:\n"
                        '<a href="https://senaisaocarlos.edupage.org/timetable/" style="color: red; text-decoration: underline;" target="_blank" rel="noopener noreferrer">https://senaisaocarlos.edupage.org/timetable/</a>\n\n'
                        f"Telefone: {telefone}\n"
                        f"Email: {email}"
                    )
                    return resposta
        
        # Se não encontrou sala, professor ou turma específica, resposta genérica
        return (
            "Horarios Escolares do SENAI Sao Carlos\n\n"
            "Para consultar os horarios completos e atualizados de salas, professores e turmas, "
            "acesse o sistema de horarios escolar:\n\n"
            '<a href="https://senaisaocarlos.edupage.org/timetable/" style="color: red; text-decoration: underline;" target="_blank" rel="noopener noreferrer">https://senaisaocarlos.edupage.org/timetable/</a>\n\n'
            "No sistema voce pode:\n"
            "- Ver horarios por sala\n"
            "- Ver horarios por professor\n"
            "- Ver horarios por turma\n"
            "- Consultar substituicoes\n"
            "- Ver informacoes atualizadas em tempo real\n\n"
            "Os horarios sao atualizados regularmente. "
            "Para informacoes especificas sobre uma sala, professor ou turma, "
            "consulte diretamente no link acima.\n\n"
            "Se precisar de ajuda para acessar o sistema ou tiver outras duvidas, "
            "entre em contato:\n"
            f"Telefone: {telefone}\n"
            f"Email: {email}"
        )

    # Respostas específicas para perguntas comuns
    if any(palavra in mensagem_lower for palavra in ['quem é vc', 'quem é você', 'quem voce', 'quem vc']):
        return RESPOSTAS_PADRAO["saudacao"]

    elif any(palavra in mensagem_lower for palavra in ['onde', 'fica', 'localização', 'localizacao', 'endereço', 'endereco']):
        return RESPOSTAS_PADRAO["endereco"]

    elif any(palavra in mensagem_lower for palavra in ['telefone', 'fone', 'contato', 'ligar']):
        return f"""Para entrar em contato com o SENAI São Carlos:

📞 Telefone/WhatsApp: {telefone}
📧 Email: {email}

Horário de atendimento: {horario}

Posso te ajudar com mais alguma informação? 😊"""

    # REMOVIDO: Resposta pré-definida para cursos - agora vai para LM Studio
    # Perguntas sobre cursos devem passar pelo LM Studio para respostas mais detalhadas e personalizadas

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
        # NÃO retornar se for pergunta sobre horários de aulas/professores/turmas
        # (essas perguntas já foram tratadas acima na seção de horários)
        if _eh_pergunta_sobre_horarios(mensagem):
            # Já foi tratado acima, não fazer nada aqui
            pass
        else:
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
        return f"""Olá! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos.

Posso te ajudar com informações sobre:
🎓 Cursos técnicos e de qualificação
📍 Localização e horários
📞 Contatos e inscrições
🏭 O que é o SENAI

É só perguntar! 😊

Para informações específicas, entre em contato:
📞 {telefone}
📧 {email}"""

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

def _eh_mensagem_sem_sentido(mensagem: str) -> bool:
    """
    Detecta se a mensagem não faz sentido (gibberish, caracteres aleatórios, etc.)
    Retorna True se a mensagem parece ser sem sentido
    """
    if not mensagem or len(mensagem.strip()) < 2:
        return False
    
    mensagem_limpa = mensagem.strip().lower()
    
    # Remover espaços e pontuação para análise
    mensagem_sem_espacos = re.sub(r'[^\w]', '', mensagem_limpa)
    
    if len(mensagem_sem_espacos) < 2:
        return False
    
    # Verificar se contém apenas caracteres repetidos (ex: "aaaa", "1111")
    if len(set(mensagem_sem_espacos)) <= 2 and len(mensagem_sem_espacos) > 3:
        return True
    
    # Verificar padrões de caracteres aleatórios sem vogais suficientes
    vogais = sum(1 for c in mensagem_sem_espacos if c in 'aeiouáéíóúâêîôûàèìòùãõ')
    total_caracteres = len(mensagem_sem_espacos)
    
    # Se tem menos de 20% de vogais e mais de 4 caracteres, provavelmente é sem sentido
    if total_caracteres > 4 and vogais / total_caracteres < 0.2:
        return True
    
    # Verificar se não contém palavras comuns do português ou relacionadas ao SENAI
    palavras_comuns = [
        'senai', 'curso', 'aula', 'professor', 'sala', 'biblioteca', 'secretaria',
        'o', 'a', 'de', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'na',
        'qual', 'onde', 'como', 'quando', 'quem', 'porque', 'sobre', 'sobre',
        'informacao', 'informação', 'preciso', 'quero', 'gostaria', 'pode',
        'me', 'você', 'voce', 'eu', 'ele', 'ela', 'nos', 'eles', 'elas'
    ]
    
    # Verificar se contém alguma palavra comum
    tem_palavra_comum = any(palavra in mensagem_limpa for palavra in palavras_comuns)
    
    # Se não tem palavras comuns e tem mais de 3 caracteres, pode ser sem sentido
    if not tem_palavra_comum and len(mensagem_sem_espacos) > 3:
        # Verificar se tem muitas consoantes consecutivas (padrão de gibberish)
        consoantes_consecutivas = re.findall(r'[bcdfghjklmnpqrstvwxyz]{4,}', mensagem_sem_espacos)
        if consoantes_consecutivas:
            return True
    
    # Verificar padrões de teclado (ex: "asdf", "qwerty", "zxcv")
    padroes_teclado = ['asdf', 'qwerty', 'zxcv', 'hjkl', 'fghj', 'dfgh']
    if any(padrao in mensagem_sem_espacos for padrao in padroes_teclado):
        return True
    
    return False

def processar_mensagem(mensagem: str, historico_chat: List[Dict]) -> str:
    """Processa a mensagem e retorna uma resposta com arquitetura inteligente"""
    try:
        mensagem_lower = (mensagem or '').lower()
        nome_usuario_ctx = _extrair_nome_do_historico(historico_chat)
        
        # 0.5) Verificar se a mensagem não faz sentido ANTES de qualquer processamento
        if _eh_mensagem_sem_sentido(mensagem):
            resposta_especifica = (
                "Olá! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxílio para o SENAI São Carlos. "
                "Posso ajudar apenas com informações sobre o SENAI São Carlos, como:\n\n"
                "• Cursos oferecidos\n"
                "• Localização de salas e instalações\n"
                "• Horários de funcionamento\n"
                "• Processos de inscrição\n"
                "• Informações sobre professores e turmas\n"
                "• E outras informações relacionadas à unidade\n\n"
                "Se você tiver alguma dúvida sobre o SENAI São Carlos, fique à vontade para perguntar!"
            )
            return tratar_nome_usuario(resposta_especifica, nome_usuario_ctx)

        # 0) Verificar cache primeiro (antes de qualquer processamento)
        from utils.response_cache import get_cached_response, cache_response
        from info.horarios import carregar_horarios_professores
        
        # NÃO usar cache para perguntas sobre professores/horários (sempre buscar informações atualizadas)
        area_dois_keywords = ['área dois', 'area dois', 'área 2', 'area 2', 'área ii', 'area ii']
        professores_disponiveis = [p.lower() for p in carregar_horarios_professores().keys()]
        tem_professor_na_mensagem = any(prof.lower() in mensagem_lower for prof in professores_disponiveis)
        eh_pergunta_horario = _eh_pergunta_sobre_horarios(mensagem)
        
        # Pular cache se for pergunta sobre área dois, professores ou horários
        if any(k in mensagem_lower for k in area_dois_keywords) or (tem_professor_na_mensagem and eh_pergunta_horario):
            cached_response = None
        else:
            cached_response = get_cached_response(mensagem)
        if cached_response:
            # Sempre tratar o nome do usuário ao recuperar do cache
            # (o cache não deve conter nomes de usuários)
            return tratar_nome_usuario(cached_response, nome_usuario_ctx)

        # 1) Small-talk: tratar imediatamente com fallback (cumprimentos, despedidas, agradecimentos)
        if _e_small_talk(mensagem_lower):
            # Cumprimentos
            if any(p in mensagem_lower for p in ['olá', 'ola', 'oi', 'bom dia', 'boa tarde', 'boa noite']):
                resposta_base = RESPOSTAS_PADRAO["saudacao"]
                cache_response(mensagem, resposta_base)  # Salvar sem nome do usuário
                resposta = tratar_nome_usuario(resposta_base, nome_usuario_ctx)
                return resposta
            # Agradecimentos
            if any(p in mensagem_lower for p in ['obrigado', 'obrigada', 'valeu', 'agradeco', 'agradeço', 'perfeito', 'show', 'ok']):
                resposta_base = RESPOSTAS_PADRAO["agradecimento"]
                cache_response(mensagem, resposta_base)  # Salvar sem nome do usuário
                resposta = tratar_nome_usuario(resposta_base, nome_usuario_ctx)
                return resposta
            # Despedidas
            if any(p in mensagem_lower for p in ['tchau', 'até', 'ate', 'flw', 'falou', 'até logo', 'ate logo']):
                resposta_base = RESPOSTAS_PADRAO["despedida"]
                cache_response(mensagem, resposta_base)  # Salvar sem nome do usuário
                resposta = tratar_nome_usuario(resposta_base, nome_usuario_ctx)
                return resposta
            # Nome do bot
            if any(p in mensagem_lower for p in ['qual seu nome', 'como você se chama', 'quem é você', 'quem é vc', 'quem e voce', 'quem e vc']):
                resposta_base = RESPOSTAS_PADRAO["nome"]
                cache_response(mensagem, resposta_base)  # Salvar sem nome do usuário
                resposta = tratar_nome_usuario(resposta_base, nome_usuario_ctx)
                return resposta
            # Confirmações simples
            if any(p in mensagem_lower for p in ['beleza', 'blz', 'tá bom', 'ta bom']):
                resposta_base = RESPOSTAS_PADRAO["confirmacao"]
                cache_response(mensagem, resposta_base)  # Salvar sem nome do usuário
                resposta = tratar_nome_usuario(resposta_base, nome_usuario_ctx)
                return resposta
            # Default fallback para outros casos de small talk
            resposta_base = obter_resposta_fallback(mensagem)
            cache_response(mensagem, resposta_base)  # Salvar sem nome do usuário
            resposta = tratar_nome_usuario(resposta_base, nome_usuario_ctx)
            return resposta

        # 2) Perguntas sobre horários: usar fallback (para não pesar no LM Studio)
        # Verificar primeiro se é pergunta específica sobre horários da biblioteca
        if any(p in mensagem_lower for p in ['horário', 'horario', 'horários', 'horarios']) and any(p in mensagem_lower for p in ['biblioteca', 'bibliote']):
            informacao_especifica = obter_informacao_especifica(mensagem)
            if informacao_especifica:
                resposta_final = _adicionar_informacoes_contato(_substituir_placeholders(informacao_especifica))
                cache_response(mensagem, resposta_final)  # Salvar sem nome do usuário
                resposta_tratada = tratar_nome_usuario(resposta_final, nome_usuario_ctx)
                return resposta_tratada
        
        if _eh_pergunta_sobre_horarios(mensagem):
            resposta_base = obter_resposta_fallback(mensagem)
            cache_response(mensagem, resposta_base)  # Salvar sem nome do usuário
            resposta = tratar_nome_usuario(resposta_base, nome_usuario_ctx)
            return resposta

        # 2.5) Perguntas sobre contato (email, telefone): verificar informações específicas primeiro
        if any(palavra in mensagem_lower for palavra in ['email', 'e-mail', 'correio eletronico', 'correio eletrônico', 
                                                          'telefone', 'fone', 'whatsapp', 'contato']):
            informacao_especifica = obter_informacao_especifica(mensagem)
            if informacao_especifica:
                resposta_final = _adicionar_informacoes_contato(_substituir_placeholders(informacao_especifica))
                cache_response(mensagem, resposta_final)  # Salvar sem nome do usuário
                resposta_tratada = tratar_nome_usuario(resposta_final, nome_usuario_ctx)
                return resposta_tratada

        # 3) Perguntas de localização: usar fallback (onde fica, como chegar, etc.)
        if _eh_pergunta_localizacao(mensagem):
            informacao_especifica = obter_informacao_especifica(mensagem)
            if informacao_especifica:
                resposta_final = _adicionar_informacoes_contato(_substituir_placeholders(informacao_especifica))
                cache_response(mensagem, resposta_final)  # Salvar sem nome do usuário
                resposta_tratada = tratar_nome_usuario(resposta_final, nome_usuario_ctx)
                return resposta_tratada
            # Caso nenhuma informação específica seja encontrada, usa fallback padrão
            resposta_base = RESPOSTAS_PADRAO.get("local_nao_encontrado", obter_resposta_fallback(mensagem))
            cache_response(mensagem, resposta_base)  # Salvar sem nome do usuário
            resposta = tratar_nome_usuario(resposta_base, nome_usuario_ctx)
            return resposta

        # 3) TODO O RESTO: usar LM Studio para responder
        if _deve_usar_lm_studio(mensagem, historico_chat):
            try:
                historico_formatado = formatar_historico_chat_para_prompt(historico_chat)
                # Usar informações completas para respostas mais inteligentes
                base_completa = format_senai_info_for_prompt(mensagem, include_all=True)
                prompt_inteligente = (
                    "Você é o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. "
                    "IMPORTANTE: Use EXCLUSIVAMENTE as informações estruturadas do módulo info/ fornecidas abaixo. "
                    "Responda de forma cordial, objetiva e profissional. "
                    "Seja detalhado e informativo, mas mantenha o tom amigável. "
                    "Mantenha continuidade com a conversa anterior. "
                    "Baseie suas respostas nas informações oficiais do SENAI São Carlos.\n\n"
                    "INSTRUÇÕES ESPECIAIS:\n"
                    "- Se a pergunta for sobre o CONTEÚDO de uma sala/banheiro/instalação (ex: 'o que tem no banheiro', 'o que tem na biblioteca'), "
                    "use as informações de INFRAESTRUTURA E INSTALAÇÕES fornecidas abaixo para descrever o que existe naquele local.\n"
                    "- Se a pergunta for sobre LOCALIZAÇÃO (ex: 'onde fica o banheiro'), use as informações de localização fornecidas.\n"
                    "- Se a pergunta for sobre HORÁRIOS (ex: 'qual professor está na sala 315?', 'qual turma está na sala 322?', 'onde está o professor Fabiana?', 'que dia a turma 2IDS-SC_A tem aula?'), "
                    "use as informações de HORÁRIOS DE SALAS, PROFESSORES E TURMAS fornecidas abaixo. Responda de forma clara e organizada, indicando o dia da semana, período (manhã/tarde/noite), disciplina, professor e sala quando disponível.\n"
                    "- Se as informações sobre conteúdo não estiverem disponíveis, seja honesto e informe que não tem essa informação específica.\n\n"
                    f"{base_completa}\n\n"
                    f"Histórico da conversa:\n{historico_formatado}\n\n"
                    f"Usuário: {mensagem}\n\n"
                    f"Assistente SENAI:"
                )
                texto = _chamar_lm_studio(prompt_inteligente, stop=["Usuário:", "Sistema:", "Assistente SENAI:"])
                if texto:
                    resposta_limpa = limpar_resposta(texto)
                    if resposta_limpa.strip() and len(resposta_limpa.strip()) > 20:
                        resposta_final = _adicionar_informacoes_contato(_substituir_placeholders(resposta_limpa))
                        resposta_final = _corrigir_informacoes_banheiro(resposta_final)
                        cache_response(mensagem, resposta_final)  # Salvar sem nome do usuário
                        resposta_tratada = tratar_nome_usuario(resposta_final, nome_usuario_ctx)
                        return resposta_tratada
                # LM Studio não retornou algo útil: usar resposta rica baseada em info_manager
                resposta_rica = _gerar_resposta_rica_sobre_senai(mensagem)
                if resposta_rica:
                    resposta_rica = _adicionar_informacoes_contato(_substituir_placeholders(resposta_rica))
                    resposta_rica = _corrigir_informacoes_banheiro(resposta_rica)
                    cache_response(mensagem, resposta_rica)  # Salvar sem nome do usuário
                    resposta_tratada = tratar_nome_usuario(resposta_rica, nome_usuario_ctx)
                    return resposta_tratada
            except Exception as e:
                # Se LM Studio falhar, usar fallback genérico
                print(f"Erro ao chamar LM Studio: {e}")
                pass
        
        # FALLBACK FINAL: Se LM Studio não funcionou, usar resposta genérica
        resposta_fallback_base = obter_resposta_fallback(mensagem)
        cache_response(mensagem, resposta_fallback_base)  # Salvar sem nome do usuário
        resposta_fallback = tratar_nome_usuario(resposta_fallback_base, nome_usuario_ctx)
        return resposta_fallback

    except Exception as e:
        # Fallback final para qualquer erro não tratado
        nome_usuario_fallback = _extrair_nome_do_historico(historico_chat)
        resposta_fallback_base = obter_resposta_fallback(mensagem)
        cache_response(mensagem, resposta_fallback_base)  # Salvar sem nome do usuário
        resposta_fallback = tratar_nome_usuario(resposta_fallback_base, nome_usuario_fallback)
        return resposta_fallback

def _extrair_nome_do_historico(historico_chat: List[Dict]) -> str:
    """Tenta extrair o nome do usuário do histórico (campo nome_usuario)."""
    try:
        if not historico_chat:
            return ''
        for msg in reversed(historico_chat):
            # Suporta ambos formatos: ('remetente'/'usuario') e ('sender'/'user')
            if ((msg.get('remetente') == 'usuario') or (msg.get('sender') == 'user')) and msg.get('nome_usuario'):
                return str(msg.get('nome_usuario'))
        return ''
    except Exception:
        return ''

# Alias para compatibilidade com app.py
process_message = processar_mensagem


