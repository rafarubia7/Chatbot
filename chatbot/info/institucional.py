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
    "feira_profissoes": Evento(
        nome="Feira de Profissões",
        periodo="Setembro/2024",
        publico_alvo="Estudantes do ensino médio",
        descricao="Exposição de cursos e carreiras técnicas",
        local="Auditório Principal",
        inscricao="Entrada franca"
    ),
    "semana_tecnologia": Evento(
        nome="Semana da Tecnologia",
        periodo="Outubro/2024",
        publico_alvo="Alunos e profissionais da área",
        descricao="Palestras e workshops sobre inovação",
        local="Diversos laboratórios",
        inscricao="Inscrições pelo site"
    ),
    "hackathon": Evento(
        nome="Hackathon SENAI",
        periodo="Novembro/2024",
        publico_alvo="Estudantes de TI",
        descricao="Maratona de programação com desafios reais",
        local="Laboratório de Informática",
        inscricao="Vagas limitadas"
    )
}

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