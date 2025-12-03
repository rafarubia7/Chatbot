#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para gerenciar informações de horários de salas, professores e turmas
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

# Caminho base para os arquivos de horários
HORARIOS_BASE_PATH = Path(__file__).parent / "horarios"

# Cache para os dados carregados
_horarios_cache = {
    'professores': {},
    'salas': {},
    'turmas': {}
}


def _carregar_json(caminho: Path) -> Optional[Dict]:
    """Carrega um arquivo JSON"""
    try:
        if caminho.exists():
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None


def carregar_horarios_professores() -> Dict[str, Dict]:
    """Carrega todos os horários de professores"""
    if _horarios_cache['professores']:
        return _horarios_cache['professores']
    
    professores_path = HORARIOS_BASE_PATH / "horarios_professores"
    if not professores_path.exists():
        return {}
    
    horarios = {}
    for arquivo in professores_path.glob("*.json"):
        nome_professor = arquivo.stem.replace('_', ' ').title()
        dados = _carregar_json(arquivo)
        if dados:
            horarios[nome_professor] = dados
    
    _horarios_cache['professores'] = horarios
    return horarios


def carregar_horarios_salas() -> Dict[str, Dict]:
    """Carrega todos os horários de salas"""
    if _horarios_cache['salas']:
        return _horarios_cache['salas']
    
    salas_path = HORARIOS_BASE_PATH / "horarios_salas"
    if not salas_path.exists():
        return {}
    
    horarios = {}
    for arquivo in salas_path.glob("*.json"):
        numero_sala = arquivo.stem
        dados = _carregar_json(arquivo)
        if dados:
            horarios[numero_sala] = dados
    
    _horarios_cache['salas'] = horarios
    return horarios


def carregar_horarios_turmas() -> Dict[str, Dict]:
    """Carrega todos os horários de turmas"""
    if _horarios_cache['turmas']:
        return _horarios_cache['turmas']
    
    turmas_path = HORARIOS_BASE_PATH / "horarios_turmas"
    if not turmas_path.exists():
        return {}
    
    horarios = {}
    for arquivo in turmas_path.glob("*.json"):
        nome_turma = arquivo.stem.replace('_', ' ').upper()
        dados = _carregar_json(arquivo)
        if dados:
            horarios[nome_turma] = dados
    
    _horarios_cache['turmas'] = horarios
    return horarios


def formatar_horarios_para_prompt() -> str:
    """Formata todos os horários em um texto estruturado para o prompt do LM Studio"""
    texto = "\n=== HORÁRIOS DE SALAS, PROFESSORES E TURMAS ===\n"
    texto += "⚠️ IMPORTANTE: Estes horários são válidos para a semana de 1 a 5 de dezembro de 2025.\n\n"
    
    # Horários por sala
    horarios_salas = carregar_horarios_salas()
    if horarios_salas:
        texto += "HORÁRIOS POR SALA:\n"
        for sala_num, horarios in sorted(horarios_salas.items()):
            texto += f"\nSala {sala_num}:\n"
            for periodo in ['manhã', 'tarde', 'noite']:
                if periodo in horarios and horarios[periodo]:
                    texto += f"  {periodo.title()}:\n"
                    for dia_semana in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                        if dia_semana in horarios[periodo] and horarios[periodo][dia_semana]:
                            texto += f"    {dia_semana.title()}:\n"
                            for aula in horarios[periodo][dia_semana]:
                                disciplina = aula.get('disciplina', '')
                                professor = aula.get('professor', '')
                                if disciplina or professor:
                                    texto += f"      - Disciplina: {disciplina}"
                                    if professor:
                                        texto += f" | Professor: {professor}"
                                    texto += "\n"
        texto += "\n"
    
    # Horários por professor
    horarios_professores = carregar_horarios_professores()
    if horarios_professores:
        texto += "HORÁRIOS POR PROFESSOR:\n"
        for professor_nome, horarios in sorted(horarios_professores.items()):
            texto += f"\nProfessor(a) {professor_nome}:\n"
            for periodo in ['manhã', 'tarde', 'noite']:
                if periodo in horarios and horarios[periodo]:
                    texto += f"  {periodo.title()}:\n"
                    for dia_semana in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                        if dia_semana in horarios[periodo] and horarios[periodo][dia_semana]:
                            texto += f"    {dia_semana.title()}:\n"
                            for aula in horarios[periodo][dia_semana]:
                                disciplina = aula.get('disciplina', '')
                                turma = aula.get('turma', '')
                                sala = aula.get('sala', '')
                                if disciplina or turma or sala:
                                    texto += f"      - Disciplina: {disciplina}"
                                    if turma:
                                        texto += f" | Turma: {turma}"
                                    if sala:
                                        texto += f" | Sala: {sala}"
                                    texto += "\n"
        texto += "\n"
    
    # Horários por turma
    horarios_turmas = carregar_horarios_turmas()
    if horarios_turmas:
        texto += "HORÁRIOS POR TURMA:\n"
        for turma_nome, horarios in sorted(horarios_turmas.items()):
            texto += f"\nTurma {turma_nome}:\n"
            for periodo in ['manhã', 'tarde', 'noite']:
                if periodo in horarios and horarios[periodo]:
                    texto += f"  {periodo.title()}:\n"
                    for dia_semana in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                        if dia_semana in horarios[periodo] and horarios[periodo][dia_semana]:
                            texto += f"    {dia_semana.title()}:\n"
                            for aula in horarios[periodo][dia_semana]:
                                disciplina = aula.get('disciplina', '')
                                professor = aula.get('professor', '')
                                sala = aula.get('sala', '')
                                if disciplina or professor or sala:
                                    texto += f"      - Disciplina: {disciplina}"
                                    if professor:
                                        texto += f" | Professor: {professor}"
                                    if sala:
                                        texto += f" | Sala: {sala}"
                                    texto += "\n"
        texto += "\n"
    
    return texto


def buscar_horario_sala(numero_sala: str) -> Optional[Dict]:
    """Busca horário de uma sala específica"""
    horarios = carregar_horarios_salas()
    return horarios.get(numero_sala)


def buscar_horario_professor(nome_professor: str) -> Optional[Dict]:
    """Busca horário de um professor específico"""
    horarios = carregar_horarios_professores()
    # Tentar busca exata primeiro
    if nome_professor in horarios:
        prof_horarios = horarios[nome_professor]
        # Remover campos de metadata
        horarios_limpos = {}
        for periodo in ['manhã', 'tarde', 'noite']:
            if periodo in prof_horarios:
                horarios_limpos[periodo] = prof_horarios[periodo]
        return horarios_limpos if horarios_limpos else prof_horarios
    
    # Busca por similaridade (case-insensitive)
    nome_lower = nome_professor.lower()
    for prof_nome, prof_horarios in horarios.items():
        if prof_nome.lower() == nome_lower or nome_lower in prof_nome.lower():
            # Remover campos de metadata
            horarios_limpos = {}
            for periodo in ['manhã', 'tarde', 'noite']:
                if periodo in prof_horarios:
                    horarios_limpos[periodo] = prof_horarios[periodo]
            return horarios_limpos if horarios_limpos else prof_horarios
    
    # Busca por fuzzy matching (para erros de digitação)
    try:
        from fuzzywuzzy import fuzz
        melhor_match = None
        melhor_score = 0
        for prof_nome, prof_horarios in horarios.items():
            score = fuzz.ratio(nome_lower, prof_nome.lower())
            if score > melhor_score and score >= 75:  # Threshold de 75% de similaridade
                melhor_score = score
                melhor_match = prof_nome
        
        if melhor_match:
            prof_horarios = horarios[melhor_match]
            # Remover campos de metadata
            horarios_limpos = {}
            for periodo in ['manhã', 'tarde', 'noite']:
                if periodo in prof_horarios:
                    horarios_limpos[periodo] = prof_horarios[periodo]
            return horarios_limpos if horarios_limpos else prof_horarios
    except ImportError:
        pass  # Se fuzzywuzzy não estiver disponível, continuar sem fuzzy matching
    
    return None


def buscar_horario_turma(nome_turma: str) -> Optional[Dict]:
    """Busca horário de uma turma específica"""
    horarios = carregar_horarios_turmas()
    # Tentar busca exata primeiro
    if nome_turma in horarios:
        turma_horarios = horarios[nome_turma]
        # Remover campos de metadata
        horarios_limpos = {}
        for periodo in ['manhã', 'tarde', 'noite']:
            if periodo in turma_horarios:
                horarios_limpos[periodo] = turma_horarios[periodo]
        return horarios_limpos if horarios_limpos else turma_horarios
    
    # Busca por similaridade (case-insensitive)
    turma_lower = nome_turma.lower().replace('_', ' ')
    for turma_nome, turma_horarios in horarios.items():
        if turma_nome.lower() == turma_lower or turma_lower in turma_nome.lower():
            # Remover campos de metadata
            horarios_limpos = {}
            for periodo in ['manhã', 'tarde', 'noite']:
                if periodo in turma_horarios:
                    horarios_limpos[periodo] = turma_horarios[periodo]
            return horarios_limpos if horarios_limpos else turma_horarios
    
    return None


def formatar_horario_sala_para_resposta(numero_sala: str, horarios: Dict) -> str:
    """Formata os horários de uma sala específica para resposta ao usuário"""
    if not horarios:
        return ""
    
    texto = ""
    
    # Mapear dias da semana para português
    dias_semana_pt = {
        'segunda': 'Segunda-feira',
        'terça': 'Terça-feira',
        'quarta': 'Quarta-feira',
        'quinta': 'Quinta-feira',
        'sexta': 'Sexta-feira',
        'sábado': 'Sábado'
    }
    
    # Mapear períodos
    periodos_pt = {
        'manhã': 'Manhã',
        'tarde': 'Tarde',
        'noite': 'Noite'
    }
    
    tem_horarios = False
    for periodo in ['manhã', 'tarde', 'noite']:
        if periodo in horarios and horarios[periodo]:
            # Verificar se há aulas neste período
            tem_aulas_periodo = False
            for dia in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                if dia in horarios[periodo] and horarios[periodo][dia]:
                    tem_aulas_periodo = True
                    break
            
            if tem_aulas_periodo:
                if not tem_horarios:
                    texto += f"Horarios da Sala {numero_sala}:\n"
                    texto += "⚠️ Estes horários são válidos para a semana de 1 a 5 de dezembro de 2025.\n\n"
                    tem_horarios = True
                
                texto += f"{periodos_pt.get(periodo, periodo)}:\n"
                for dia in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                    # Ignorar campos de metadata do período
                    if dia == '_descricao' or dia == '_info':
                        continue
                    if dia in horarios[periodo] and horarios[periodo][dia]:
                        texto += f"  {dias_semana_pt.get(dia, dia)}:\n"
                        for aula in horarios[periodo][dia]:
                            # Processar apenas dicionários (aulas)
                            if isinstance(aula, dict):
                                disciplina = aula.get('disciplina', '')
                                professor = aula.get('professor', '')
                                turma = aula.get('turma', '')
                                
                                # Exibir apenas se tiver disciplina ou professor
                                if disciplina or professor:
                                    linha = f"    - {disciplina}" if disciplina else "    - Aula"
                                    if professor:
                                        linha += f" | Professor: {professor}"
                                    if turma:
                                        linha += f" | Turma: {turma}"
                                    texto += linha + "\n"
                texto += "\n"
    
    return texto

def formatar_horario_professor_para_resposta(nome_professor: str, horarios: Dict) -> str:
    """Formata os horários de um professor específico para resposta ao usuário"""
    if not horarios:
        return ""
    
    texto = ""
    
    # Mapear dias da semana para português
    dias_semana_pt = {
        'segunda': 'Segunda-feira',
        'terça': 'Terça-feira',
        'quarta': 'Quarta-feira',
        'quinta': 'Quinta-feira',
        'sexta': 'Sexta-feira',
        'sábado': 'Sábado'
    }
    
    # Mapear períodos
    periodos_pt = {
        'manhã': 'Manhã',
        'tarde': 'Tarde',
        'noite': 'Noite'
    }
    
    tem_horarios = False
    for periodo in ['manhã', 'tarde', 'noite']:
        if periodo in horarios and horarios[periodo]:
            # Verificar se há aulas neste período
            tem_aulas_periodo = False
            for dia in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                if dia in horarios[periodo] and horarios[periodo][dia]:
                    tem_aulas_periodo = True
                    break
            
            if tem_aulas_periodo:
                if not tem_horarios:
                    texto += f"Horarios do Professor {nome_professor}:\n"
                    texto += "⚠️ Estes horários são válidos para a semana de 1 a 5 de dezembro de 2025.\n\n"
                    tem_horarios = True
                
                texto += f"{periodos_pt.get(periodo, periodo)}:\n"
                for dia in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                    # Ignorar campos de metadata do período
                    if dia == '_descricao' or dia == '_info':
                        continue
                    if dia in horarios[periodo] and horarios[periodo][dia]:
                        texto += f"  {dias_semana_pt.get(dia, dia)}:\n"
                        for aula in horarios[periodo][dia]:
                            # Processar apenas dicionários (aulas)
                            if isinstance(aula, dict):
                                disciplina = aula.get('disciplina', '')
                                turma = aula.get('turma', '')
                                sala = aula.get('sala', '')
                                
                                # Exibir apenas se tiver disciplina ou turma
                                if disciplina or turma:
                                    linha = f"    - {disciplina}" if disciplina else "    - Aula"
                                    if turma:
                                        linha += f" | Turma: {turma}"
                                    if sala:
                                        linha += f" | Sala: {sala}"
                                    texto += linha + "\n"
                texto += "\n"
    
    return texto

def formatar_horario_turma_para_resposta(nome_turma: str, horarios: Dict) -> str:
    """Formata os horários de uma turma específica para resposta ao usuário"""
    if not horarios:
        return ""
    
    texto = ""
    
    # Mapear dias da semana para português
    dias_semana_pt = {
        'segunda': 'Segunda-feira',
        'terça': 'Terça-feira',
        'quarta': 'Quarta-feira',
        'quinta': 'Quinta-feira',
        'sexta': 'Sexta-feira',
        'sábado': 'Sábado'
    }
    
    # Mapear períodos
    periodos_pt = {
        'manhã': 'Manhã',
        'tarde': 'Tarde',
        'noite': 'Noite'
    }
    
    tem_horarios = False
    for periodo in ['manhã', 'tarde', 'noite']:
        if periodo in horarios and horarios[periodo]:
            # Verificar se há aulas neste período
            tem_aulas_periodo = False
            for dia in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                if dia in horarios[periodo] and horarios[periodo][dia]:
                    tem_aulas_periodo = True
                    break
            
            if tem_aulas_periodo:
                if not tem_horarios:
                    texto += f"Horarios da Turma {nome_turma}:\n"
                    texto += "⚠️ Estes horários são válidos para a semana de 1 a 5 de dezembro de 2025.\n\n"
                    tem_horarios = True
                
                texto += f"{periodos_pt.get(periodo, periodo)}:\n"
                for dia in ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']:
                    if dia in horarios[periodo] and horarios[periodo][dia]:
                        texto += f"  {dias_semana_pt.get(dia, dia)}:\n"
                        for aula in horarios[periodo][dia]:
                            # Processar apenas dicionários (aulas)
                            if isinstance(aula, dict):
                                disciplina = aula.get('disciplina', '')
                                professor = aula.get('professor', '')
                                sala = aula.get('sala', '')
                                
                                # Exibir apenas se tiver disciplina ou professor
                                if disciplina or professor:
                                    linha = f"    - {disciplina}" if disciplina else "    - Aula"
                                    if professor:
                                        linha += f" | Professor: {professor}"
                                    if sala:
                                        linha += f" | Sala: {sala}"
                                    texto += linha + "\n"
                texto += "\n"
    
    return texto

def limpar_cache():
    """Limpa o cache de horários"""
    global _horarios_cache
    _horarios_cache = {
        'professores': {},
        'salas': {},
        'turmas': {}
    }

