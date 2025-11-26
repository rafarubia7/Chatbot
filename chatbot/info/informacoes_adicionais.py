"""
Informações adicionais sobre o SENAI São Carlos baseadas em dados atualizados
"""
from typing import Dict, List

# Informações sobre áreas de atuação e estrutura
AREAS_ATUACAO = {
    "principais": [
        "Alimentos e Bebidas",
        "Automotiva", 
        "Construção Civil",
        "Eletroeletrônica",
        "Energia",
        "Gestão",
        "Logística",
        "Metalmecânica",
        "Tecnologia da Informação"
    ],
    "estrutura_adicional": {
        "faculdade": "Faculdade de Tecnologia SENAI Antonio Adolpho Lobbe",
        "nucleo_tecnologia": "Núcleo de Tecnologia em Automação",
        "servicos_industria": [
            "Assistência técnica",
            "Laboratórios especializados", 
            "Inovação para indústrias",
            "Consultoria tecnológica"
        ]
    }
}

# Cursos livres específicos mencionados
CURSOS_LIVRES_ESPECIFICOS = [
    {
        "nome": "Energia Solar Fotovoltaica – Tecnologias e Aplicações",
        "duracao": "24 horas",
        "modalidade": "Presencial",
        "area": "Energia"
    },
    {
        "nome": "Técnicas para Execução e Montagem de Circuitos Elétricos Prediais",
        "duracao": "80 horas", 
        "modalidade": "Presencial",
        "area": "Eletroeletrônica"
    },
    {
        "nome": "Programação e Integração da Plataforma Arduino",
        "duracao": "40 horas",
        "modalidade": "Presencial", 
        "area": "Tecnologia da Informação"
    }
]

# Informações para alunos já matriculados
INFORMACOES_ALUNOS = {
    "portal_aluno": {
        "descricao": "Portal do aluno para acesso a informações acadêmicas",
        "link": "Disponível no site oficial da unidade",
        "servicos": [
            "Consulta de notas",
            "Calendário escolar",
            "Horário de aulas",
            "Material didático"
        ]
    },
    "calendario_escolar": {
        "descricao": "Calendário com datas importantes do ano letivo",
        "link": "Disponível no site oficial da unidade",
        "conteudo": [
            "Datas de início e fim de semestre",
            "Períodos de férias",
            "Datas de provas e avaliações",
            "Eventos acadêmicos"
        ]
    },
    "horario_escolar": {
        "descricao": "Horários de aulas por turma, docente e ambiente",
        "link": "Disponível no site oficial da unidade",
        "funcionalidades": [
            "Consulta por turma",
            "Consulta por docente", 
            "Consulta por ambiente de ensino",
            "Atualização em tempo real"
        ]
    },
    "documentos_academicos": [
        "Proposta Pedagógica",
        "Manual do Aluno", 
        "Regimento Comum",
        "Regulamento do Conselho Escolar"
    ]
}

# Informações para empresas e parcerias
SERVICOS_EMPRESAS = {
    "nucleo_tecnologia": {
        "nome": "Núcleo de Tecnologia em Automação",
        "servicos": [
            "Assistência técnica especializada",
            "Laboratórios para desenvolvimento",
            "Inovação para indústrias",
            "Consultoria em automação",
            "Pesquisa e desenvolvimento"
        ],
        "contato": {
            "telefone": "(16) 2106-8700",
            "email": "saocarlos@sp.senai.br"
        }
    },
    "parcerias": {
        "tipos": [
            "Parcerias educacionais",
            "Estágios e empregos",
            "Projetos de inovação",
            "Consultoria técnica",
            "Treinamento corporativo"
        ],
        "beneficios": [
            "Acesso a mão de obra qualificada",
            "Desenvolvimento de projetos inovadores",
            "Treinamento de funcionários",
            "Consultoria especializada"
        ]
    }
}

# Redes sociais e canais de comunicação
REDES_SOCIAIS = {
    "instagram": {
        "usuario": "@senaisaocarlos601",
        "link": "https://www.instagram.com/senaisaocarlos601/",
        "descricao": "Atualizações sobre cursos, eventos e notícias da unidade"
    },
    "facebook": {
        "descricao": "Página oficial no Facebook",
        "conteudo": "Eventos, cursos e informações institucionais"
    },
    "site_oficial": {
        "url": "https://sp.senai.br/unidade/saocarlos/",
        "secoes": [
            "Sobre a Unidade",
            "Cursos Disponíveis", 
            "Horário de Atendimento",
            "Informações aos Alunos",
            "Contato"
        ]
    }
}

# Informações sobre bolsas e gratuidade
BOLSAS_GRATUIDADE = {
    "cursos_gratuitos": [
        "Todos os cursos de Aprendizagem Industrial",
        "Alguns cursos técnicos (consultar disponibilidade)",
        "Cursos de qualificação profissional (alguns)"
    ],
    "criterios": [
        "Renda familiar",
        "Situação socioeconômica", 
        "Vinculação com empresa parceira",
        "Programas governamentais"
    ],
    "informacoes": "Para informações específicas sobre bolsas e gratuidade, consulte a secretaria pelo telefone (16) 2106-8700"
}

# Informações sobre processo seletivo e inscrições
PROCESSO_SELETIVO = {
    "inscricoes": {
        "periodo": "Consultar calendário no site oficial",
        "requisitos_gerais": [
            "Documentação completa",
            "Comprovação de escolaridade",
            "Taxa de inscrição (quando aplicável)"
        ],
        "documentos": [
            "RG e CPF",
            "Comprovante de residência",
            "Histórico escolar",
            "Foto 3x4"
        ]
    },
    "selecao": {
        "metodos": [
            "Prova escrita",
            "Análise de documentos",
            "Entrevista (quando aplicável)"
        ],
        "criterios": [
            "Notas do ensino médio",
            "Desempenho na prova",
            "Disponibilidade de vagas"
        ]
    }
}

# Informações sobre duração dos cursos
DURACAO_CURSOS = {
    "livres": {
        "exemplos": [
            "24 horas - Energia Solar Fotovoltaica",
            "40 horas - Programação Arduino", 
            "80 horas - Circuitos Elétricos Prediais"
        ],
        "variacao": "De 8 a 200 horas dependendo do curso"
    },
    "tecnicos": {
        "duracao": "1.200 a 1.600 horas",
        "periodo": "1 a 2 anos"
    },
    "superiores": {
        "duracao": "2.400 a 3.200 horas",
        "periodo": "2 a 3 anos"
    },
    "aprendizagem": {
        "duracao": "400 a 1.600 horas",
        "periodo": "6 meses a 2 anos"
    }
}

