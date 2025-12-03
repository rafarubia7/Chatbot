"""
Gerenciador de informações do SENAI São Carlos
Consolida e formata informações para uso no LM Studio
"""
from typing import Dict, List, Optional
from .base_info import INFO_SENAI_SAO_CARLOS, CONTATOS
from .cursos import CURSOS
from .salas import SALAS
from .processos import PROCESSO_INSCRICAO, PERGUNTAS_FREQUENTES
from .institucional import EMPRESAS_PARCEIRAS, EVENTOS, DIFERENCIAIS
from .respostas import RESPOSTAS_PADRAO
from .funcionarios import obter_info_funcionarios_para_lm
from .informacoes_adicionais import (
    AREAS_ATUACAO, CURSOS_LIVRES_ESPECIFICOS, INFORMACOES_ALUNOS,
    SERVICOS_EMPRESAS, REDES_SOCIAIS, BOLSAS_GRATUIDADE, 
    PROCESSO_SELETIVO, DURACAO_CURSOS
)
# Nota: formatar_horarios_para_prompt não é mais usado aqui - horários são tratados pelo fallback


class InfoManager:
    """Gerenciador centralizado de informações do SENAI São Carlos"""
    
    def __init__(self):
        self.info_base = INFO_SENAI_SAO_CARLOS
        self.contatos = CONTATOS
        self.cursos = CURSOS
        self.salas = SALAS
        self.processos = PROCESSO_INSCRICAO
        self.perguntas_frequentes = PERGUNTAS_FREQUENTES
        self.empresas_parceiras = EMPRESAS_PARCEIRAS
        self.eventos = EVENTOS
        self.diferenciais = DIFERENCIAIS
        self.respostas_padrao = RESPOSTAS_PADRAO
        # Novas informações adicionais
        self.areas_atuacao = AREAS_ATUACAO
        self.cursos_livres_especificos = CURSOS_LIVRES_ESPECIFICOS
        self.informacoes_alunos = INFORMACOES_ALUNOS
        self.servicos_empresas = SERVICOS_EMPRESAS
        self.redes_sociais = REDES_SOCIAIS
        self.bolsas_gratuidade = BOLSAS_GRATUIDADE
        self.processo_seletivo = PROCESSO_SELETIVO
        self.duracao_cursos = DURACAO_CURSOS
    
    def get_basic_info(self) -> str:
        """Retorna informações básicas da unidade"""
        return f"""
**ESCOLA SENAI SÃO CARLOS - "ANTONIO A. LOBBE"**

**Localização:**
- Endereço: {self.info_base['endereco']}
- Telefone/WhatsApp: {self.info_base['telefone']}
- Email: {self.info_base['email']}
- Site: {self.info_base['site']}

⏰ **Horários de Funcionamento:**
- Secretaria: {self.info_base['horario_funcionamento']}
- Biblioteca: {self.info_base['horario_biblioteca']}

📖 **Sobre a Unidade:**
{self.info_base['sobre'].strip()}
"""
    
    def get_courses_info(self) -> str:
        """Retorna informações detalhadas sobre cursos"""
        info = "\n🎓 **CURSOS OFERECIDOS:**\n"
        
        # Cursos Técnicos
        info += "\n**CURSOS TÉCNICOS:**\n"
        for curso in self.cursos['tecnico']:
            info += f"• {curso['nome']}\n"
            info += f"  - Descrição: {curso['descricao']}\n"
            info += f"  - Duração: {curso['duracao']}\n"
            info += f"  - Modalidades: {', '.join(curso['modalidades'])}\n"
            info += f"  - Horários: {', '.join(curso['horarios'])}\n"
            info += f"  - Requisitos: {curso['requisitos']}\n"
            info += f"  - Valor: {curso['valor']}\n\n"
        
        # Cursos Superiores
        info += "\n**CURSOS SUPERIORES (Reconhecidos pelo MEC):**\n"
        for curso in self.cursos['superior']:
            info += f"• {curso['nome']}\n"
            info += f"  - Descrição: {curso['descricao']}\n"
            info += f"  - Duração: {curso['duracao']}\n"
            info += f"  - Modalidades: {', '.join(curso['modalidades'])}\n"
            info += f"  - Horários: {', '.join(curso['horarios'])}\n"
            info += f"  - Requisitos: {curso['requisitos']}\n"
            info += f"  - Reconhecimento: {curso['reconhecimento']}\n"
            info += f"  - Valor: {curso['valor']}\n\n"
        
        # Pós-graduação / Especialização
        if 'pos_graduacao' in self.cursos:
            info += "\n**PÓS-GRADUAÇÃO / ESPECIALIZAÇÃO:**\n"
            for curso in self.cursos['pos_graduacao']:
                info += f"• {curso['nome']}\n"
                info += f"  - Descrição: {curso['descricao']}\n"
                info += f"  - Duração: {curso['duracao']}\n"
                info += f"  - Modalidades: {', '.join(curso['modalidades'])}\n"
                info += f"  - Horários: {', '.join(curso['horarios'])}\n"
                info += f"  - Requisitos: {curso['requisitos']}\n"
                info += f"  - Reconhecimento: {curso['reconhecimento']}\n"
                info += f"  - Valor: {curso['valor']}\n\n"
        
        # Cursos de Aprendizagem Industrial
        info += "\n**CURSOS DE APRENDIZAGEM INDUSTRIAL (GRATUITOS):**\n"
        for curso in self.cursos['aprendizagem']:
            info += f"• {curso['nome']}\n"
            info += f"  - Descrição: {curso['descricao']}\n"
            info += f"  - Duração: {curso['duracao']}\n"
            info += f"  - Modalidade: {curso['modalidade']}\n"
            info += f"  - Valor: {curso['valor']}\n\n"
        
        # Cursos de Qualificação
        info += "\n**CURSOS DE QUALIFICAÇÃO PROFISSIONAL:**\n"
        for curso in self.cursos['qualificacao']:
            info += f"• {curso['nome']}\n"
            info += f"  - Descrição: {curso['descricao']}\n"
            info += f"  - Duração: {curso['duracao']}\n"
            info += f"  - Modalidades: {', '.join(curso['modalidades'])}\n"
            info += f"  - Horários: {', '.join(curso['horarios'])}\n"
            info += f"  - Requisitos: {curso['requisitos']}\n"
            info += f"  - Valor: {curso['valor']}\n\n"
        
        # Observações importantes
        info += "\n**INFORMAÇÕES IMPORTANTES:**\n"
        for key, obs in self.cursos['observacoes'].items():
            info += f"• {obs}\n"
        
        return info
    
    def get_infrastructure_info(self) -> str:
        """Retorna informações sobre infraestrutura e instalações"""
        info = "\n**INFRAESTRUTURA E INSTALAÇÕES:**\n"
        
        # Laboratórios
        info += "\n**LABORATÓRIOS:**\n"
        laboratorios = [sala for sala in self.salas.values() if sala.tipo == "laboratorio"]
        for lab in laboratorios:
            info += f"• {lab.nome}\n"
            info += f"  - Descrição: {lab.descricao}\n"
            info += f"  - Localização: Prédio {lab.localizacao.predio}, {lab.localizacao.andar}"
            if lab.localizacao.sala:
                info += f", Sala {lab.localizacao.sala}"
            info += f"\n  - Referência: {lab.localizacao.referencia}\n"
            if lab.capacidade:
                info += f"  - Capacidade: {lab.capacidade} pessoas\n"
            if lab.horario_funcionamento:
                info += f"  - Horário: {lab.horario_funcionamento}\n"
            info += "\n"
        
        # Banheiros e Sanitários
        info += "\n**BANHEIROS E SANITÁRIOS:**\n"
        banheiros = [sala for sala in self.salas.values() 
                     if sala.tipo == "instalacao" and 
                     ('banheiro' in sala.nome.lower() or 'sanitário' in sala.nome.lower() or 'sanitario' in sala.nome.lower())]
        for banheiro in banheiros:
            info += f"• {banheiro.nome}\n"
            info += f"  - Descrição: {banheiro.descricao}\n"
            info += f"  - Localização: Prédio {banheiro.localizacao.predio}, {banheiro.localizacao.andar}"
            if banheiro.localizacao.sala:
                info += f", Sala {banheiro.localizacao.sala}"
            info += f"\n  - Referência: {banheiro.localizacao.referencia}\n"
            if banheiro.navegacao and banheiro.navegacao.instrucoes:
                info += f"  - Como chegar: {'; '.join(banheiro.navegacao.instrucoes)}\n"
            info += "\n"
        
        # Instalações comuns
        info += "\n**INSTALAÇÕES COMUNS:**\n"
        instalacoes = [sala for sala in self.salas.values() 
                      if sala.tipo == "comum" or 
                      (sala.tipo == "instalacao" and 
                       'banheiro' not in sala.nome.lower() and 
                       'sanitário' not in sala.nome.lower() and 
                       'sanitario' not in sala.nome.lower())]
        for inst in instalacoes:
            info += f"• {inst.nome}\n"
            info += f"  - Descrição: {inst.descricao}\n"
            info += f"  - Localização: Prédio {inst.localizacao.predio}, {inst.localizacao.andar}"
            if inst.localizacao.sala:
                info += f", Sala {inst.localizacao.sala}"
            info += f"\n  - Referência: {inst.localizacao.referencia}\n"
            if inst.horario_funcionamento:
                info += f"  - Horário: {inst.horario_funcionamento}\n"
            info += "\n"
        
        return info
    
    def get_partnerships_info(self) -> str:
        """Retorna informações sobre parcerias e empresas"""
        info = "\n🤝 **EMPRESAS PARCEIRAS:**\n"
        
        for key, empresa in self.empresas_parceiras.items():
            info += f"• **{empresa.nome}** ({empresa.setor})\n"
            info += f"  - Tipos de parceria: {', '.join(empresa.tipo_parceria)}\n"
            info += f"  - Descrição: {empresa.descricao}\n\n"
        
        return info
    
    def get_events_info(self) -> str:
        """Retorna informações sobre eventos"""
        from .institucional import INFO_ACOMPANHAR_EVENTOS
        
        info = "\n📅 **EVENTOS E ATIVIDADES DO SENAI SÃO CARLOS:**\n\n"
        
        # Listar eventos conhecidos
        if self.eventos:
            info += "**EVENTOS RECENTES E PROGRAMADOS:**\n"
            for key, evento in self.eventos.items():
                info += f"• **{evento.nome}**\n"
                info += f"  - Data/Horário: {evento.periodo}\n"
                info += f"  - Público-alvo: {evento.publico_alvo}\n"
                info += f"  - Descrição: {evento.descricao}\n"
                info += f"  - Local: {evento.local}\n"
                info += f"  - Inscrição: {evento.inscricao}\n\n"
        
        # Adicionar informações sobre como acompanhar eventos
        info += "\n**COMO ACOMPANHAR EVENTOS FUTUROS:**\n"
        info += INFO_ACOMPANHAR_EVENTOS
        
        return info
    
    def get_differentials_info(self) -> str:
        """Retorna informações sobre diferenciais da unidade"""
        info = "\n⭐ **DIFERENCIAIS DA UNIDADE:**\n"
        
        for categoria, itens in self.diferenciais.items():
            info += f"\n**{categoria.upper()}:**\n"
            for item in itens:
                info += f"• {item}\n"
        
        return info
    
    def get_enrollment_process(self) -> str:
        """Retorna informações sobre processos de inscrição"""
        info = "\n**PROCESSOS DE INSCRIÇÃO:**\n"
        
        for tipo, processo in self.processos.items():
            info += f"\n**{tipo.upper()}:**\n"
            info += f"{processo.strip()}\n"
        
        return info
    
    def get_faq_info(self) -> str:
        """Retorna perguntas frequentes"""
        info = "\n❓ **PERGUNTAS FREQUENTES:**\n"
        
        for pergunta, resposta in self.perguntas_frequentes.items():
            info += f"\n**P: {pergunta}**\n"
            info += f"R: {resposta.strip()}\n"
        
        return info
    
    def get_contacts_info(self) -> str:
        """Retorna informações de contato detalhadas"""
        info = "\n**CONTATOS E ATENDIMENTO:**\n"
        
        for depto, contato in self.contatos.items():
            info += f"\n**{depto.replace('_', ' ').title()}:**\n"
            if 'telefone' in contato:
                info += f"• Telefone: {contato['telefone']}\n"
            if 'whatsapp' in contato:
                info += f"• WhatsApp: {contato['whatsapp']}\n"
            if 'email' in contato:
                info += f"• Email: {contato['email']}\n"
            if 'horario' in contato:
                info += f"• Horário: {contato['horario']}\n"
        
        return info
    
    def get_staff_info(self) -> str:
        """Retorna informações sobre funcionários"""
        return obter_info_funcionarios_para_lm()
    
    def get_complete_info(self) -> str:
        """Retorna todas as informações consolidadas com priorização"""
        info = ""
        
        # PRIORIDADE 1: Informações básicas e funcionários (mais importantes)
        info += self.get_basic_info()
        info += self.get_staff_info()  # Funcionários primeiro
        
        # PRIORIDADE 2: Cursos
        info += self.get_courses_info()
        
        # NOTA: Infraestrutura e horários são tratados pelo sistema de fallback, não pelo LM Studio
        
        # PRIORIDADE 3: Contatos e FAQ
        info += self.get_contacts_info()
        info += self.get_faq_info()
        
        # PRIORIDADE 4: Outras informações (se houver espaço)
        info += self.get_partnerships_info()
        info += self.get_events_info()
        info += self.get_differentials_info()
        info += self.get_enrollment_process()
        info += self.get_additional_info()
        
        return info
    
    def get_additional_info(self) -> str:
        """Retorna informações adicionais importantes que podem estar faltando"""
        info = "\n**INFORMAÇÕES ADICIONAIS IMPORTANTES:**\n"
        
        # Áreas de atuação
        info += "\n**ÁREAS DE ATUAÇÃO PRINCIPAIS:**\n"
        for area in self.areas_atuacao['principais']:
            info += f"• {area}\n"
        
        # Estrutura adicional
        info += f"\n**ESTRUTURA ADICIONAL:**\n"
        info += f"• {self.areas_atuacao['estrutura_adicional']['faculdade']}\n"
        info += f"• {self.areas_atuacao['estrutura_adicional']['nucleo_tecnologia']}\n"
        info += "• Serviços para indústria:\n"
        for servico in self.areas_atuacao['estrutura_adicional']['servicos_industria']:
            info += f"  - {servico}\n"
        
        # Cursos livres específicos
        info += "\n**CURSOS LIVRES ESPECÍFICOS:**\n"
        for curso in self.cursos_livres_especificos:
            info += f"• {curso['nome']} ({curso['duracao']}) - {curso['area']}\n"
        
        # Informações para alunos
        info += "\n**INFORMAÇÕES PARA ALUNOS MATRICULADOS:**\n"
        info += f"• Portal do Aluno: {self.informacoes_alunos['portal_aluno']['descricao']}\n"
        info += f"• Calendário Escolar: {self.informacoes_alunos['calendario_escolar']['descricao']}\n"
        info += f"• Horário Escolar: {self.informacoes_alunos['horario_escolar']['descricao']}\n"
        info += "• Documentos Acadêmicos:\n"
        for doc in self.informacoes_alunos['documentos_academicos']:
            info += f"  - {doc}\n"
        
        # Serviços para empresas
        info += "\n**SERVIÇOS PARA EMPRESAS:**\n"
        info += f"• {self.servicos_empresas['nucleo_tecnologia']['nome']}\n"
        info += "• Serviços oferecidos:\n"
        for servico in self.servicos_empresas['nucleo_tecnologia']['servicos']:
            info += f"  - {servico}\n"
        info += "• Tipos de parcerias:\n"
        for tipo in self.servicos_empresas['parcerias']['tipos']:
            info += f"  - {tipo}\n"
        
        # Redes sociais
        info += "\n**REDES SOCIAIS E CANAIS:**\n"
        info += f"• Instagram: {self.redes_sociais['instagram']['usuario']}\n"
        info += f"• Facebook: {self.redes_sociais['facebook']['descricao']}\n"
        info += f"• Site Oficial: {self.redes_sociais['site_oficial']['url']}\n"
        
        # Bolsas e gratuidade
        info += "\n**BOLSAS E GRATUIDADE:**\n"
        info += "• Cursos gratuitos disponíveis:\n"
        for curso in self.bolsas_gratuidade['cursos_gratuitos']:
            info += f"  - {curso}\n"
        info += "• Critérios para bolsas:\n"
        for criterio in self.bolsas_gratuidade['criterios']:
            info += f"  - {criterio}\n"
        
        # Processo seletivo
        info += "\n**PROCESSO SELETIVO E INSCRIÇÕES:**\n"
        info += f"• Período de inscrições: {self.processo_seletivo['inscricoes']['periodo']}\n"
        info += "• Documentos necessários:\n"
        for doc in self.processo_seletivo['inscricoes']['documentos']:
            info += f"  - {doc}\n"
        info += "• Métodos de seleção:\n"
        for metodo in self.processo_seletivo['selecao']['metodos']:
            info += f"  - {metodo}\n"
        
        # Duração dos cursos
        info += "\n**DURAÇÃO DOS CURSOS:**\n"
        info += f"• Cursos Livres: {self.duracao_cursos['livres']['variacao']}\n"
        info += f"• Cursos Técnicos: {self.duracao_cursos['tecnicos']['duracao']} ({self.duracao_cursos['tecnicos']['periodo']})\n"
        info += f"• Cursos Superiores: {self.duracao_cursos['superiores']['duracao']} ({self.duracao_cursos['superiores']['periodo']})\n"
        info += f"• Aprendizagem Industrial: {self.duracao_cursos['aprendizagem']['duracao']} ({self.duracao_cursos['aprendizagem']['periodo']})\n"
        
        return info
    
    def get_contextual_info(self, query: str) -> str:
        """Retorna informações relevantes baseadas na consulta"""
        query_lower = query.lower()
        
        # Determinar contexto da consulta
        if any(word in query_lower for word in ['curso', 'cursos', 'técnico', 'superior', 'aprendizagem', 'qualificação']):
            return self.get_courses_info()
        
        elif any(word in query_lower for word in ['laboratório', 'laboratorio', 'sala', 'biblioteca', 'refeitório', 'refeitorio', 'banheiro', 'banheiros', 'sanitário', 'sanitario', 'infraestrutura']):
            # Verificar se é pergunta de localização específica (onde fica, como chegar) ou pergunta geral sobre infraestrutura
            palavras_localizacao = ['onde fica', 'onde está', 'onde esta', 'como chegar', 'localização', 'localizacao', 'onde encontro']
            eh_localizacao = any(palavra in query_lower for palavra in palavras_localizacao)
            
            if eh_localizacao:
                # Perguntas de localização específica são tratadas pelo sistema de fallback
                return self.get_basic_info()
            else:
                # Perguntas gerais sobre infraestrutura (ex: "quais laboratórios existem?", "que infraestrutura vocês têm?")
                # devem incluir informações de infraestrutura para o LM Studio responder
                return self.get_basic_info() + self.get_infrastructure_info()
        
        elif any(word in query_lower for word in ['parceria', 'empresa', 'estágio', 'estagio', 'oportunidade']):
            return self.get_partnerships_info()
        
        elif any(word in query_lower for word in ['evento', 'eventos', 'feira', 'feiras', 'hackathon', 'semana', 'atividade', 'atividades', 'fórum', 'forum', 'palestra', 'palestras', 'workshop', 'workshops', 'exposição', 'exposicao', 'exposições', 'exposicoes']):
            return self.get_events_info()
        
        elif any(word in query_lower for word in ['inscrição', 'inscricao', 'matrícula', 'matricula', 'processo']):
            return self.get_enrollment_process()
        
        elif any(word in query_lower for word in ['contato', 'telefone', 'email', 'atendimento']):
            return self.get_contacts_info()
        
        elif any(word in query_lower for word in ['diferencial', 'vantagem', 'benefício', 'beneficio', 'por que']):
            return self.get_differentials_info()
        
        elif any(word in query_lower for word in ['pergunta', 'dúvida', 'duvida', 'faq', 'frequente']):
            return self.get_faq_info()
        
        elif any(word in query_lower for word in ['funcionário', 'funcionario', 'funcionários', 'funcionarios', 'professor', 'coordenador', 'diretor', 'analista', 'orientador', 'fernanda', 'carla', 'marcio', 'julio', 'rainer']):
            return self.get_staff_info()
        
        elif any(word in query_lower for word in ['bolsa', 'bolsas', 'financiamento', 'desconto', 'gratuidade', 'psg', 'pagamento']):
            return self.get_basic_info() + self.get_enrollment_process() + self.get_faq_info()
        
        elif any(word in query_lower for word in ['certificado', 'certificados', 'diploma', 'reconhecimento', 'mec']):
            return self.get_courses_info() + self.get_faq_info()
        
        elif any(word in query_lower for word in ['estágio', 'estagio', 'emprego', 'trabalho', 'oportunidade', 'mural']):
            return self.get_partnerships_info() + self.get_faq_info()
        
        elif any(word in query_lower for word in ['inovação', 'inovacao', 'pesquisa', 'projeto', 'fablab', 'competição']):
            return self.get_differentials_info() + self.get_events_info()
        
        elif any(word in query_lower for word in ['senai online', 'ead', 'online', 'distância', 'distancia']):
            return self.get_basic_info() + self.get_courses_info()
        
        elif any(word in query_lower for word in ['área', 'area', 'atuacao', 'atuação', 'alimentos', 'automotiva', 'construção', 'construcao', 'eletroeletrônica', 'eletroeletronica', 'energia', 'gestão', 'gestao', 'logística', 'logistica', 'metalmecânica', 'metalmecanica', 'tecnologia informação']):
            return self.get_basic_info() + self.get_additional_info()
        
        elif any(word in query_lower for word in ['curso livre', 'cursos livres', 'qualificação', 'qualificacao', 'aperfeiçoamento', 'aperfeicoamento', 'energia solar', 'arduino', 'circuitos elétricos', 'circuitos eletricos']):
            return self.get_courses_info() + self.get_additional_info()
        
        elif any(word in query_lower for word in ['aluno', 'alunos', 'matriculado', 'matriculados', 'portal', 'calendário', 'calendario', 'horário escolar', 'horario escolar', 'manual aluno', 'regimento']):
            return self.get_additional_info() + self.get_contacts_info()
        
        elif any(word in query_lower for word in ['horário', 'horario', 'horarios', 'horários', 'qual professor', 'qual turma', 'qual sala', 'onde está o professor', 'onde esta o professor', 'professor está', 'professor esta', 'turma está', 'turma esta', 'sala está', 'sala esta', 'que dia', 'que período', 'que periodo']):
            # Perguntas sobre horários são tratadas pelo sistema de fallback, não pelo LM Studio
            return self.get_staff_info()
        
        elif any(word in query_lower for word in ['empresa', 'empresas', 'parceria', 'parcerias', 'núcleo', 'nucleo', 'tecnologia', 'automação', 'automacao', 'assistência técnica', 'assistencia tecnica', 'consultoria']):
            return self.get_additional_info() + self.get_partnerships_info()
        
        elif any(word in query_lower for word in ['instagram', 'facebook', 'rede social', 'redes sociais', 'site oficial', 'canais comunicação']):
            return self.get_additional_info()
        
        elif any(word in query_lower for word in ['duração', 'duracao', 'horas', 'período', 'periodo', 'anos', 'meses']):
            return self.get_additional_info() + self.get_courses_info()
        
        elif any(word in query_lower for word in ['inscrição', 'inscricao', 'seleção', 'selecao', 'prova', 'documentos', 'requisitos']):
            return self.get_additional_info() + self.get_enrollment_process()
        
        else:
            # Para consultas gerais, retornar informações mais completas
            return (self.get_basic_info() + 
                   self.get_courses_info() + 
                   self.get_differentials_info() + 
                   self.get_partnerships_info() +
                   self.get_additional_info())


# Instância global do gerenciador
info_manager = InfoManager()


def get_senai_context_for_lm(query: str) -> str:
    """
    Retorna contexto relevante do SENAI para uso no LM Studio
    baseado na consulta do usuário
    """
    return info_manager.get_contextual_info(query)


def get_complete_senai_info() -> str:
    """
    Retorna todas as informações do SENAI para uso no LM Studio
    """
    return info_manager.get_complete_info()


def format_senai_info_for_prompt(query: str, include_all: bool = False) -> str:
    """
    Formata informações do SENAI para inclusão no prompt do LM Studio
    
    Args:
        query: Consulta do usuário
        include_all: Se True, inclui todas as informações. Se False, apenas as relevantes
    """
    if include_all:
        info = get_complete_senai_info()
    else:
        info = get_senai_context_for_lm(query)
    
    # Limitar o tamanho das informações para evitar timeout
    max_info_length = 6000  # Reduzido para evitar timeout do LM Studio
    
    if len(info) > max_info_length:
        info = info[:max_info_length] + "..."
    
    # Verificar se a consulta é sobre eventos para adicionar instruções específicas
    query_lower = query.lower()
    e_pergunta_eventos = any(word in query_lower for word in [
        'evento', 'eventos', 'feira', 'feiras', 'hackathon', 'semana', 'atividade', 
        'atividades', 'fórum', 'forum', 'palestra', 'palestras', 'workshop', 'workshops',
        'exposição', 'exposicao', 'exposições', 'exposicoes'
    ])
    
    # Verificar tipo de pergunta para direcionamento correto
    e_pergunta_matricula_curso = any(word in query_lower for word in [
        'matrícula', 'matricula', 'inscrição', 'inscricao', 'inscrever', 'inscrever-se',
        'curso', 'cursos', 'valor', 'preço', 'preco', 'custo', 'duração', 'duracao',
        'processo seletivo', 'processo seletivo', 'vestibular', 'seleção', 'selecao',
        'documentos', 'documentação', 'documentacao', 'requisitos', 'pré-requisitos', 'pre-requisitos'
    ])
    
    e_pergunta_info_escola = any(word in query_lower for word in [
        'informação sobre a escola', 'informacao sobre a escola', 'sobre o senai', 'sobre a escola',
        'o que é o senai', 'o que e o senai', 'história', 'historia', 'fundação', 'fundacao',
        'diferenciais', 'infraestrutura', 'laboratórios', 'laboratorios', 'estrutura',
        'qualidade de vida', 'apoio ao aluno', 'setor de apoio', 'setor apoio'
    ])
    
    instrucoes_especificas = ""
    
    if e_pergunta_eventos and "EVENTOS" in info.upper():
        instrucoes_especificas = """
- ATENÇÃO: Esta pergunta é sobre EVENTOS. Procure na seção "EVENTOS E ATIVIDADES" acima.
- Liste TODOS os eventos mencionados na seção de eventos, incluindo datas, horários, descrições e informações de inscrição.
- Se houver uma seção "COMO ACOMPANHAR EVENTOS FUTUROS", mencione essas informações também.
- Seja específico e detalhado sobre cada evento listado.
"""
    elif e_pergunta_matricula_curso:
        instrucoes_especificas = """
- ATENÇÃO: Esta pergunta é sobre MATRÍCULA, INSCRIÇÃO ou CURSOS.
- DIRECIONE o usuário para a SECRETARIA do SENAI São Carlos.
- Informe que a Secretaria é responsável por:
  * Processos de matrícula e inscrição
  * Informações sobre cursos, valores, duração e requisitos
  * Documentação necessária
  * Processos seletivos
- Forneça os contatos da Secretaria:
  * Telefone/WhatsApp: (16) 2106-8700
  * Email: saocarlos@sp.senai.br
  * Horário: Segunda a Sexta-feira, das 8h às 20h; Sábados, das 8h às 13h e das 14h às 16h
  * Localização: Sala A-01, térreo (primeira sala à esquerda após a entrada)
- Se tiver informações sobre processos de inscrição nas informações acima, mencione-as, mas sempre oriente a confirmar com a Secretaria.
"""
    elif e_pergunta_info_escola:
        instrucoes_especificas = """
- ATENÇÃO: Esta pergunta é sobre INFORMAÇÕES GERAIS DA ESCOLA ou SOBRE O SENAI.
- DIRECIONE o usuário para o SETOR DE APOIO (Sala 204) quando apropriado.
- O Setor de Apoio (Análise de Qualidade de Vida) é responsável por:
  * Informações gerais sobre a escola
  * Apoio ao aluno
  * Qualidade de vida
  * Orientações gerais sobre a unidade
- Localização do Setor de Apoio: Sala 204 - no refeitório, última sala à direita
- Se a pergunta for sobre informações institucionais, diferenciais, infraestrutura ou história da escola, 
  você pode responder com as informações disponíveis acima, mas também pode orientar a entrar em contato 
  com o Setor de Apoio para mais detalhes.
- Contato geral: Telefone (16) 2106-8700 ou Email: saocarlos@sp.senai.br
"""
    
    return f"""
[INFORMAÇÕES OFICIAIS DO SENAI SÃO CARLOS - ESCOLA "ANTONIO A. LOBBE"]
{info}

[REGRAS IMPORTANTES PARA O ASSISTENTE]
- Use EXCLUSIVAMENTE as informações acima para responder
- Não invente informações que não estão listadas
- Mantenha o tom profissional mas amigável
- Sempre inclua informações de contato quando relevante
- Se não souber algo específico, oriente a entrar em contato
- Mantenha continuidade com a conversa anterior
- Seja detalhado e informativo nas respostas
- Use as informações estruturadas do módulo info/ como base principal
- Se a pergunta não estiver nas informações acima, diga que não tem essa informação específica e oriente a entrar em contato
- NUNCA invente dados como valores, datas ou informações não fornecidas

[DIRECIONAMENTO PARA SETORES - IMPORTANTE]
- Para perguntas sobre MATRÍCULA, INSCRIÇÃO, CURSOS, VALORES, PROCESSOS SELETIVOS: 
  → Direcione para a SECRETARIA (Sala A-01, térreo)
  → Telefone: (16) 2106-8700 | Email: saocarlos@sp.senai.br
  
- Para perguntas sobre INFORMAÇÕES GERAIS DA ESCOLA, SOBRE O SENAI, DIFERENCIAIS, INFRAESTRUTURA:
  → Pode responder com as informações disponíveis, mas também pode orientar ao SETOR DE APOIO (Sala 204)
  → O Setor de Apoio fica no refeitório, última sala à direita
  → Contato geral: (16) 2106-8700

{instrucoes_especificas}
"""
