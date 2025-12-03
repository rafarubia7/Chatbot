"""
Gerencia o registro de sugestões de usuários em um arquivo JSON.
"""
import json
import os
from typing import Any, Dict, List

SUGGESTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'sugestoes_chat.json')
SUGGESTIONS_FILE = os.path.normpath(SUGGESTIONS_FILE)


def _load_suggestions() -> List[Dict[str, Any]]:
    """Carrega sugestões existentes do arquivo."""
    try:
        if not os.path.exists(SUGGESTIONS_FILE):
            return []
        with open(SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return data.get('suggestions', [])
    except Exception:
        return []


def _save_all(suggestions: List[Dict[str, Any]]) -> None:
    """Persiste a lista inteira no arquivo."""
    os.makedirs(os.path.dirname(SUGGESTIONS_FILE), exist_ok=True)
    with open(SUGGESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, ensure_ascii=False, indent=2)


def save_suggestion(data: Dict[str, Any]) -> Dict[str, Any]:
    """Registra uma nova sugestão e retorna o registro salvo."""
    suggestions = _load_suggestions()
    suggestion_entry = {
        "categoria": data.get("categoria") or "geral",
        "descricao": data.get("descricao"),
        "contexto": data.get("contexto")
    }
    suggestions.append(suggestion_entry)
    _save_all(suggestions)
    return suggestion_entry


