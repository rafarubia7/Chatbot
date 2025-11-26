"""
Módulo de informações do SENAI São Carlos
"""
from .base_info import INFO_SENAI_SAO_CARLOS, CONTATOS
from .cursos import CURSOS
from .salas import SALAS
from .processos import PROCESSO_INSCRICAO, PERGUNTAS_FREQUENTES
from .institucional import (
    EMPRESAS_PARCEIRAS,
    EVENTOS,
    DIFERENCIAIS
)
from .search import obter_informacao_especifica
from .respostas import RESPOSTAS_PADRAO
from .funcionarios import buscar_funcionario, obter_info_funcionarios_para_lm
from .info_manager import (
    InfoManager,
    info_manager,
    get_senai_context_for_lm,
    get_complete_senai_info,
    format_senai_info_for_prompt
)
from .informacoes_adicionais import (
    AREAS_ATUACAO, CURSOS_LIVRES_ESPECIFICOS, INFORMACOES_ALUNOS,
    SERVICOS_EMPRESAS, REDES_SOCIAIS, BOLSAS_GRATUIDADE, 
    PROCESSO_SELETIVO, DURACAO_CURSOS
)
from .horarios import (
    formatar_horarios_para_prompt,
    buscar_horario_sala,
    buscar_horario_professor,
    buscar_horario_turma,
    carregar_horarios_salas,
    carregar_horarios_professores,
    carregar_horarios_turmas
)

def formatar_info_sao_carlos() -> str:
    """Formata as informações do SENAI São Carlos para inclusão no prompt do sistema"""
    texto_info = f"""
[INFORMAÇÕES SOBRE O SENAI SÃO CARLOS]
Nome: {INFO_SENAI_SAO_CARLOS['nome_completo']}
Endereço: {INFO_SENAI_SAO_CARLOS['endereco']}
Telefone: {INFO_SENAI_SAO_CARLOS['telefone']}
Email: {INFO_SENAI_SAO_CARLOS['email']}
Site: {INFO_SENAI_SAO_CARLOS['site']}
Horário de funcionamento: {INFO_SENAI_SAO_CARLOS['horario_funcionamento']}
"""
    # Adicionar descrição
    texto_info += f"\nSobre a unidade: {INFO_SENAI_SAO_CARLOS['sobre'].strip()}\n"

    # Adicionar cursos técnicos
    texto_info += "\n[CURSOS TÉCNICOS OFERECIDOS]\n"
    for curso in CURSOS['tecnico']:
        texto_info += f"- {curso['nome']}: {curso['descricao']} Duração: {curso['duracao']}. Modalidades: {', '.join(curso['modalidades'])}. Horários: {', '.join(curso['horarios'])}.\n"

    # Adicionar cursos de aprendizagem industrial
    texto_info += "\n[CURSOS DE APRENDIZAGEM INDUSTRIAL]\n"
    for curso in CURSOS['aprendizagem']:
        texto_info += f"- {curso['nome']}: {curso['descricao']} Duração: {curso['duracao']}. Idade: {curso['idade']}.\n"

    # Adicionar cursos de qualificação
    texto_info += "\n[CURSOS DE QUALIFICAÇÃO PROFISSIONAL]\n"
    for curso in CURSOS['qualificacao'][:2]:  # Limitar para manter o prompt compacto
        texto_info += f"- {curso['nome']}: {curso['descricao']} Duração: {curso['duracao']}.\n"

    # Adicionar informações sobre inscrição
    texto_info += "\n[PROCESSO DE INSCRIÇÃO]\n"
    for tipo, processo in PROCESSO_INSCRICAO.items():
        linha = processo.strip().split('\n')[0]
        texto_info += f"Para cursos {tipo}: {linha}\n"

    # Adicionar informações sobre infraestrutura
    texto_info += "\n[INFRAESTRUTURA E LABORATÓRIOS]\n"
    for key, sala in SALAS.items():
        if sala.tipo == "laboratorio":
            texto_info += f"- {sala.nome}: {sala.descricao}\n"
            texto_info += f"  Localização: Prédio {sala.localizacao.predio}, {sala.localizacao.andar}, Sala {sala.localizacao.sala}\n"
    
    # Adicionar contatos específicos
    texto_info += "\n[CONTATOS]\n"
    for depto, info in CONTATOS.items():
        texto_info += f"{depto.capitalize()}: Tel: {info['telefone']}, Email: {info['email']}\n"

    # Adicionar diferenciais por categoria
    texto_info += "\n[DIFERENCIAIS DA UNIDADE]\n"
    for categoria, lista in DIFERENCIAIS.items():
        texto_info += f"\n{categoria.capitalize()}:\n"
        for item in lista[:2]:  # Limitando a 2 itens por categoria para manter o prompt compacto
            texto_info += f"- {item}\n"

    return texto_info

__all__ = [
    'INFO_SENAI_SAO_CARLOS',
    'CURSOS',
    'SALAS',
    'PROCESSO_INSCRICAO',
    'CONTATOS',
    'PERGUNTAS_FREQUENTES',
    'EMPRESAS_PARCEIRAS',
    'EVENTOS',
    'DIFERENCIAIS',
    'obter_informacao_especifica',
    'formatar_info_sao_carlos',
    'RESPOSTAS_PADRAO',
    'InfoManager',
    'info_manager',
    'get_senai_context_for_lm',
    'get_complete_senai_info',
    'format_senai_info_for_prompt',
    'buscar_funcionario',
    'obter_info_funcionarios_para_lm',
    'AREAS_ATUACAO',
    'CURSOS_LIVRES_ESPECIFICOS',
    'INFORMACOES_ALUNOS',
    'SERVICOS_EMPRESAS',
    'REDES_SOCIAIS',
    'BOLSAS_GRATUIDADE',
    'PROCESSO_SELETIVO',
    'DURACAO_CURSOS',
    'formatar_horarios_para_prompt',
    'buscar_horario_sala',
    'buscar_horario_professor',
    'buscar_horario_turma',
    'carregar_horarios_salas',
    'carregar_horarios_professores',
    'carregar_horarios_turmas'
] 