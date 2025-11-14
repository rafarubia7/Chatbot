# -*- coding: utf-8 -*-
"""
Informações dos funcionários do SENAI São Carlos
"""

# Informações dos funcionários organizadas por setor
FUNCIONARIOS_SENAI_SAO_CARLOS = {
    "setor_apoio": {
        "nome": "Setor de Apoio",
        "descricao": "Responsável pela qualidade de vida e apoio aos estudantes",
        "localizacao": "Sala 204 - Setor de Apoio (no refeitório, última sala à direita)",
        "como_chegar": "Ao passar pela catraca da entrada, siga reto por aproximadamente 15 passos e vire à direita. Você avistará o refeitório à sua direita. Ao entrar no refeitório, você avistará três salas à sua direita. Vá em direção à última sala - essa é a Sala 204, onde ficam a Fernanda e a Carla.",
        "funcionarios": [
            {
                "nome": "Fernanda Moreira",
                "email": "fernanda.moreira@sp.senai.br",
                "cargo": "Analista de Qualidade de Vida",
                "horario": "12h às 21h",
                "responsabilidades": [
                    "Análise e melhoria da qualidade de vida dos estudantes",
                    "Apoio psicossocial",
                    "Desenvolvimento de programas de bem-estar",
                    "Acompanhamento de indicadores de satisfação"
                ]
            },
            {
                "nome": "Carla Ballestero",
                "email": "carla.ballestero@sp.senai.br",
                "cargo": "Analista de Qualidade de Vida",
                "horario": "07h30min às 17h",
                "responsabilidades": [
                    "Análise e melhoria da qualidade de vida dos estudantes",
                    "Apoio psicossocial",
                    "Desenvolvimento de programas de bem-estar",
                    "Acompanhamento de indicadores de satisfação"
                ]
            }
        ]
    },
    "direcao": {
        "nome": "Direção",
        "descricao": "Direção da Unidade de Formação Profissional",
        "localizacao": "Sala de Direção",
        "funcionarios": [
            {
                "nome": "Marcio Vieira Marinho",
                "email": "mmarinho@sp.senai.br",
                "cargo": "Diretor de Unidade de Formação Profissional",
                "horario": "08h às 17h",
                "responsabilidades": [
                    "Direção geral da unidade",
                    "Gestão estratégica",
                    "Coordenação de atividades pedagógicas",
                    "Relações institucionais"
                ]
            }
        ]
    },
    "coordenacao_pedagogica": {
        "nome": "Coordenação Pedagógica",
        "descricao": "Coordenação das atividades pedagógicas e práticas profissionais",
        "localizacao": "Sala 326 - Sala de Coordenação",
        "como_chegar": "Suba pela escada principal e vire à esquerda no corredor. Vá andando até quase o final do corredor, a Sala de Coordenação fica ao lado do banheiro masculino, do lado direito.",
        "funcionarios": [
            {
                "nome": "Julio Cesar Melli",
                "email": "jmelli@sp.senai.br",
                "cargo": "Coordenador de Atividades Pedagógicas",
                "horario": "07h30min às 17h30min",
                "responsabilidades": [
                    "Coordenação das atividades pedagógicas",
                    "Supervisão de professores",
                    "Desenvolvimento de currículos",
                    "Acompanhamento do desempenho acadêmico"
                ]
            }
        ]
    },
    "orientacao": {
        "nome": "Orientação de Prática Profissional",
        "descricao": "Orientação de práticas profissionais e estágios",
        "localizacao": "Sala do Orientador (Rainer)",
        "como_chegar": "Ao passar pela catraca da entrada, vire à esquerda e você verá uma rampa. Desça a rampa. Vire no primeiro corredor à sua direita. A sala do Orientador é a segunda porta à sua direita.",
        "funcionarios": [
            {
                "nome": "Rainer Messias Bruno",
                "email": "rainer.bruno@sp.senai.br",
                "cargo": "Orientador de Prática Profissional",
                "horario": "07h30min às 17h30min",
                "responsabilidades": [
                    "Orientação de práticas profissionais",
                    "Acompanhamento de estágios",
                    "Desenvolvimento de competências práticas",
                    "Integração teoria-prática"
                ]
            }
        ]
    }
}

# Função para buscar informações de funcionários
def buscar_funcionario(consulta: str) -> str:
    """
    Busca informações de funcionários baseado na consulta
    
    Args:
        consulta: Consulta do usuário sobre funcionários
        
    Returns:
        Informações formatadas sobre o(s) funcionário(s)
    """
    consulta_lower = consulta.lower()
    
    # Buscar por nome específico (busca mais precisa)
    for setor_info in FUNCIONARIOS_SENAI_SAO_CARLOS.values():
        for funcionario in setor_info["funcionarios"]:
            nome_lower = funcionario["nome"].lower()
            # Busca por nome completo ou primeiro nome
            if (funcionario["nome"].lower() in consulta_lower or 
                any(palavra in nome_lower for palavra in consulta_lower.split() if len(palavra) > 2)):
                return _formatar_info_funcionario(funcionario, setor_info)
    
    # Buscar por variações de nomes específicos
    nomes_variacoes = {
        "marinho": "Marcio Vieira Marinho",
        "márcio": "Marcio Vieira Marinho",
        "marcio": "Marcio Vieira Marinho",
        "julio": "Julio Cesar Melli",
        "júlio": "Julio Cesar Melli",
        "melli": "Julio Cesar Melli",
        "rainer": "Rainer Messias Bruno",
        "bruno": "Rainer Messias Bruno",
        "carla": "Carla Ballestero",
        "ballestero": "Carla Ballestero",
        "fernanda": "Fernanda Moreira",
        "moreira": "Fernanda Moreira"
    }
    
    for variacao, nome_completo in nomes_variacoes.items():
        if variacao in consulta_lower:
            for setor_info in FUNCIONARIOS_SENAI_SAO_CARLOS.values():
                for funcionario in setor_info["funcionarios"]:
                    if funcionario["nome"] == nome_completo:
                        return _formatar_info_funcionario(funcionario, setor_info)
    
    # Buscar por cargo
    cargos_busca = {
        "diretor": "Diretor de Unidade de Formação Profissional",
        "diretor da unidade": "Diretor de Unidade de Formação Profissional",
        "diretor do senai": "Diretor de Unidade de Formação Profissional",
        "diretor são carlos": "Diretor de Unidade de Formação Profissional",
        "coordenador": "Coordenador de Atividades Pedagógicas",
        "coordenador pedagógico": "Coordenador de Atividades Pedagógicas",
        "coordenador pedagógica": "Coordenador de Atividades Pedagógicas",
        "orientador": "Orientador de Prática Profissional",
        "orientador de prática": "Orientador de Prática Profissional",
        "analista": "Analista de Qualidade de Vida",
        "qualidade de vida": "Analista de Qualidade de Vida"
    }
    
    for palavra_chave, cargo in cargos_busca.items():
        if palavra_chave in consulta_lower:
            for setor_info in FUNCIONARIOS_SENAI_SAO_CARLOS.values():
                for funcionario in setor_info["funcionarios"]:
                    if funcionario["cargo"] == cargo:
                        return _formatar_info_funcionario(funcionario, setor_info)
    
    # Buscar por setor
    setores_busca = {
        "apoio": "setor_apoio",
        "direção": "direcao",
        "direcao": "direcao",
        "coordenação": "coordenacao_pedagogica",
        "coordenacao": "coordenacao_pedagogica",
        "pedagógica": "coordenacao_pedagogica",
        "pedagogica": "coordenacao_pedagogica"
    }
    
    for palavra_chave, setor_key in setores_busca.items():
        if palavra_chave in consulta_lower:
            setor_info = FUNCIONARIOS_SENAI_SAO_CARLOS[setor_key]
            return _formatar_info_setor(setor_info)
    
    # Buscar por perguntas complexas sobre funcionários
    if any(palavra in consulta_lower for palavra in ['funcionários', 'funcionarios', 'funcionário', 'funcionario', 'equipe', 'pessoal', 'staff']):
        if 'setor de apoio' in consulta_lower or 'setor apoio' in consulta_lower:
            setor_info = FUNCIONARIOS_SENAI_SAO_CARLOS["setor_apoio"]
            return _formatar_info_setor(setor_info)
        elif 'coordenação' in consulta_lower or 'coordenacao' in consulta_lower:
            setor_info = FUNCIONARIOS_SENAI_SAO_CARLOS["coordenacao_pedagogica"]
            return _formatar_info_setor(setor_info)
        elif 'direção' in consulta_lower or 'direcao' in consulta_lower:
            setor_info = FUNCIONARIOS_SENAI_SAO_CARLOS["direcao"]
            return _formatar_info_setor(setor_info)
        else:
            # Retornar informações gerais sobre todos os funcionários
            return _formatar_info_geral_funcionarios()
    
    # Buscar por email
    for setor_info in FUNCIONARIOS_SENAI_SAO_CARLOS.values():
        for funcionario in setor_info["funcionarios"]:
            if funcionario["email"] in consulta_lower:
                return _formatar_info_funcionario(funcionario, setor_info)
    
    # Se não encontrou nada específico, retornar informações gerais
    return _formatar_info_geral_funcionarios()

def _formatar_info_funcionario(funcionario: dict, setor_info: dict) -> str:
    """Formata informações de um funcionário específico"""
    texto = f"""**{funcionario['nome']}**
**Email:** {funcionario['email']}
**Cargo:** {funcionario['cargo']}
**Horário:** {funcionario['horario']}
**Setor:** {setor_info['nome']}

**Responsabilidades:**
{chr(10).join(f"• {resp}" for resp in funcionario['responsabilidades'])}

**Contato:** {funcionario['email']}"""

    # Adicionar informações de localização se disponíveis
    if 'localizacao' in setor_info:
        texto += f"\n\n**Localização:** {setor_info['localizacao']}"
    
    if 'como_chegar' in setor_info:
        texto += f"\n\n**Como chegar:** {setor_info['como_chegar']}"
    
    return texto

def _formatar_info_setor(setor_info: dict) -> str:
    """Formata informações de um setor"""
    funcionarios_texto = []
    for funcionario in setor_info["funcionarios"]:
        funcionarios_texto.append(f"• **{funcionario['nome']}** - {funcionario['cargo']} ({funcionario['horario']})")
    
    return f"""**{setor_info['nome']}**
**Descrição:** {setor_info['descricao']}

**Funcionários:**
{chr(10).join(funcionarios_texto)}

**Contatos:**
{chr(10).join(f"• {func['nome']}: {func['email']}" for func in setor_info['funcionarios'])}"""

def _formatar_info_geral_funcionarios() -> str:
    """Formata informações gerais sobre todos os funcionários"""
    texto = "**Funcionários do SENAI São Carlos**\n\n"
    
    for setor_key, setor_info in FUNCIONARIOS_SENAI_SAO_CARLOS.items():
        texto += f"**{setor_info['nome']}**\n"
        texto += f"{setor_info['descricao']}\n\n"
        
        for funcionario in setor_info["funcionarios"]:
            texto += f"• **{funcionario['nome']}** - {funcionario['cargo']}\n"
            texto += f"  Email: {funcionario['email']}\n"
            texto += f"  Horário: {funcionario['horario']}\n\n"
    
    texto += "Para informações específicas sobre algum funcionário, mencione o nome, cargo ou setor."
    
    return texto

# Função para obter informações de funcionários para o LM Studio
def obter_info_funcionarios_para_lm() -> str:
    """
    Retorna informações dos funcionários formatadas para uso no LM Studio
    """
    texto = "FUNCIONÁRIOS DO SENAI SÃO CARLOS:\n\n"
    
    for setor_key, setor_info in FUNCIONARIOS_SENAI_SAO_CARLOS.items():
        texto += f"SETOR: {setor_info['nome']}\n"
        texto += f"Descrição: {setor_info['descricao']}\n"
        
        # Adicionar localização se disponível
        if 'localizacao' in setor_info:
            texto += f"Localização: {setor_info['localizacao']}\n"
        
        # Adicionar como chegar se disponível
        if 'como_chegar' in setor_info:
            texto += f"Como chegar: {setor_info['como_chegar']}\n"
        
        for funcionario in setor_info["funcionarios"]:
            texto += f"- {funcionario['nome']} ({funcionario['cargo']})\n"
            texto += f"  Email: {funcionario['email']}\n"
            texto += f"  Horário: {funcionario['horario']}\n"
            texto += f"  Responsabilidades: {', '.join(funcionario['responsabilidades'])}\n"
        
        texto += "\n"
    
    return texto

