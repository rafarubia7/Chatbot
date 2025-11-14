"""
Respostas padrão do chatbot
"""

RESPOSTAS_PADRAO = {
    "saudacao": "Olá! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",
    
    "agradecimento": "De nada! Fico feliz em ajudar! Estou sempre à disposição para esclarecer suas dúvidas sobre o SENAI São Carlos. Obrigado pela confiança!",
    
    "despedida": "Até logo! Foi um prazer ajudar. Se precisar de mais informações sobre o SENAI São Carlos, é só voltar! Tchau!",
    
    "nome": "Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. Como posso ajudar?",

    "confirmacao": "Beleza! Entendi perfeitamente! Estou aqui para ajudar com qualquer outra informação sobre o SENAI São Carlos. Perfeito!",
    
    "fora_escopo": (
        "Olá! Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. "
        "Posso ajudar apenas com informações da nossa unidade. "
        "Se sua pergunta for sobre o SENAI São Carlos, pode reformular incluindo o tema (ex.: curso, horário, local na escola, secretaria, biblioteca) ou o local específico (ex.: refeitório, laboratório, sala 215)?"
    ),
    
    "erro_tecnico": (
        "Desculpe, estou com dificuldades técnicas no momento. "
        "Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. "
        "Se sua dúvida for sobre nossa unidade, tente reformular incluindo o tema (curso, horário, secretaria, biblioteca, salas) para que eu possa ajudar melhor."
    ),
    
    "erro_conexao": (
        "Desculpe, estou temporariamente indisponível. "
        "Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. "
        "Se for algo sobre nossa unidade, tente novamente em instantes ou inclua mais detalhes (curso, horário, local)."
    ),
    
    "erro_geral": (
        "Desculpe, ocorreu um erro ao processar sua mensagem. "
        "Sou o Cadu, assistente virtual do SenAI, ferramenta de auxilio para o SENAI São Carlos. "
        "Se sua pergunta for sobre a unidade, por favor inclua mais contexto (curso, horário, secretaria, biblioteca, salas) e tente novamente."
    ),
    
    "local_nao_encontrado": """Por favor, me diga qual local específico você gostaria de encontrar! 

Posso te ajudar a localizar:
- Refeitório/Cantina
- Biblioteca
- Laboratórios
- Secretaria
- Entre outros locais

É só perguntar! 😊""",

    "endereco": """O SENAI São Carlos está localizado na Rua Cândido Padim, 25 - Vila Prado, São Carlos - SP.

Pontos de referência:
- Próximo ao Terminal Rodoviário de São Carlos
- Na região da Vila Prado
- A aproximadamente 3 km do centro da cidade

Posso te ajudar a encontrar algum local específico dentro da escola? Por exemplo, posso te indicar como chegar ao refeitório, biblioteca, laboratórios, etc. É só perguntar! 😊""",

    "calendario_academico": (
        "O calendário acadêmico do SENAI São Carlos pode ser consultado na secretaria da escola ou solicitado por e-mail: saocarlos@sp.senai.br. "
        "Em geral, as datas importantes também são divulgadas no site oficial. Se precisar de datas específicas, posso te orientar a entrar em contato pelo telefone (16) 2106-8700."
    ),
}