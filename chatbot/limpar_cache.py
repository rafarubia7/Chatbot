#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar o cache de respostas
Execute este script para remover respostas antigas que podem conter nomes de usuários
"""

import os
import json

def limpar_cache():
    """Limpa o arquivo de cache"""
    cache_file = 'response_cache.json'
    
    if os.path.exists(cache_file):
        # Fazer backup do cache antigo
        backup_file = 'response_cache_backup.json'
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_antigo = json.load(f)
            
            # Salvar backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(cache_antigo, f, ensure_ascii=False, indent=2)
            print(f"Backup criado: {backup_file}")
            
            # Limpar cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print(f"Cache limpo com sucesso!")
            print(f"Total de entradas removidas: {len(cache_antigo)}")
        except Exception as e:
            print(f"Erro ao limpar cache: {e}")
    else:
        print("Arquivo de cache não encontrado. Nada para limpar.")

if __name__ == '__main__':
    limpar_cache()

