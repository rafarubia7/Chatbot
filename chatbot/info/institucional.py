"""
Informações institucionais do SENAI São Carlos
"""
from typing import List, Dict
from pydantic import BaseModel

class EmpresaParceira(BaseModel):
    nome: str
    setor: str
    tipo_parceria: List[str]
    descricao: str

class Evento(BaseModel):
    nome: str
    periodo: str
    publico_alvo: str
    descricao: str
    local: str
    inscricao: str

EMPRESAS_PARCEIRAS = {
    "volkswagen": EmpresaParceira(
        nome="Volkswagen",
        setor="Automotivo",
        tipo_parceria=["Estágio", "Aprendizagem Industrial", "Projetos"],
        descricao="Parceria em programas de aprendizagem e desenvolvimento tecnológico"
    ),
    "electrolux": EmpresaParceira(
        nome="Electrolux",
        setor="Eletrodomésticos",
        tipo_parceria=["Estágio", "Aprendizagem Industrial"],
        descricao="Cooperação em programas de formação técnica"
    ),
    "faber_castell": EmpresaParceira(
        nome="Faber-Castell",
        setor="Material Escolar",
        tipo_parceria=["Aprendizagem Industrial", "Visitas Técnicas"],
        descricao="Parceria em programas educacionais e visitas técnicas"
    ),
    "embraer": EmpresaParceira(
        nome="Embraer",
        setor="Aeronáutico",
        tipo_parceria=["Estágio", "Projetos", "Pesquisa"],
        descricao="Cooperação em projetos de inovação e desenvolvimento"
    )
}

EVENTOS = {
    "forum_ciencia_dados": Evento(
        nome="Fórum Ciência de Dados para a Indústria Inteligente",
        periodo="02 de outubro de 2025, das 9h às 16h30",
        publico_alvo="Universidades, centros de pesquisa, indústria e agências de fomento",
        descricao="Fórum que tem como objetivo integrar universidades, centros de pesquisa, indústria e agências de fomento, debatendo temas de Inteligência Artificial (IA), ciência de dados e Indústria 4.0. Evento promovido em parceria com o Instituto de Estudos Avançados da USP.",
        local="Prédio do SENAI São Carlos",
        inscricao="Consultar site ou secretaria para informações de inscrição"
    ),
    "road_show_transformacao_digital": Evento(
        nome="Road Show da Jornada de Transformação Digital",
        periodo="02 de setembro de 2022",
        publico_alvo="Indústrias da região",
        descricao="Evento voltado para digitalização de indústrias da região, parte de um programa mais amplo de modernização industrial promovido pelo SENAI São Paulo. A unidade SENAI São Carlos sediou uma edição deste evento.",
        local="SENAI São Carlos",
        inscricao="Evento já realizado"
    )
}

# Informações sobre como acompanhar eventos
INFO_ACOMPANHAR_EVENTOS = """
Para saber sobre eventos atuais e futuros do SENAI São Carlos:

1. **Acessar periodicamente a página da unidade** - Novos eventos e notícias costumam aparecer como "destaques" ou "notícias" no site oficial: https://sp.senai.br/unidade/saocarlos/

2. **Seguir as redes sociais da unidade** - Muitos eventos são divulgados através das redes sociais oficiais do SENAI São Carlos. As informações de contato e redes sociais estão disponíveis no site.

3. **Entrar em contato direto com a secretaria** - Para saber se há eventos programados ou obter informações atualizadas:
   - Telefone/WhatsApp: (16) 2106-8700
   - Email: saocarlos@sp.senai.br
   - Presencialmente: Rua Cândido Padim, 25 – Vila Prado, São Carlos/SP

A secretaria pode fornecer informações detalhadas sobre eventos futuros, datas, horários, público-alvo e processos de inscrição.
"""

DIFERENCIAIS = {
    "infraestrutura": [
        "Laboratórios modernos e bem equipados",
        "Salas de aula climatizadas",
        "Biblioteca técnica atualizada",
        "Equipamentos de última geração"
    ],
    "academico": [
        "Professores com experiência na indústria",
        "Metodologia prática e hands-on",
        "Certificação reconhecida nacionalmente",
        "Grade curricular atualizada com o mercado"
    ],
    "mercado": [
        "Parcerias com grandes empresas da região",
        "Alta taxa de empregabilidade dos alunos",
        "Projetos integradores com empresas",
        "Network com profissionais da indústria"
    ],
    "inovacao": [
        "FabLab para prototipagem",
        "Projetos de pesquisa aplicada",
        "Participação em competições tecnológicas",
        "Incentivo ao empreendedorismo"
    ]
} 