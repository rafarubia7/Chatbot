"""
Informações sobre salas, laboratórios e navegação interna do SENAI São Carlos
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

class Coordenadas(BaseModel):
    lat: float
    lon: float

class Localizacao(BaseModel):
    predio: str
    andar: str
    sala: Optional[str] = None
    referencia: str
    coordenadas: Coordenadas

class Navegacao(BaseModel):
    partida: str = "entrada_principal"
    instrucoes: List[str]
    pontos_referencia: List[str]
    dicas_adicionais: Optional[str] = None

class Sala(BaseModel):
    nome: str
    tipo: str  # "laboratorio", "instalacao", "administrativo", "comum"
    descricao: str
    localizacao: Localizacao
    navegacao: Navegacao
    capacidade: Optional[int] = None
    horario_funcionamento: Optional[str] = None

SALAS: Dict[str, Sala] = {
    "refeitorio": Sala(
        nome="Refeitório",
        tipo="comum",
        descricao="Espaço para refeições com cantina e área de convivência",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="R-01",
            referencia="Próximo à entrada principal",
            coordenadas=Coordenadas(lat=-22.123456, lon=-47.123456)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Passe pela catraca na entrada da escola",
                "Siga reto por aproximadamente 15 passos",
                "Vire à direita",
                "O refeitório estará à sua direita"
            ],
            pontos_referencia=["Catraca da entrada", "Corredor principal"],
            dicas_adicionais="Ao entrar no refeitório, você encontrará a AAPM (sala de achados e perdidos) à sua direita"
        ),
        horario_funcionamento="Segunda a Sexta, das 7h às 22h"
    ),
    
    "aapm_achados_202": Sala(
        nome="AAPM (Achados e Perdidos) (202)",
        tipo="administrativo",
        descricao="Associação de Pais e Mestres e Achados e Perdidos",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="202",
            referencia="Entrada do refeitório, primeira sala à direita",
            coordenadas=Coordenadas(lat=-22.123478, lon=-47.123478)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Passe pela catraca na entrada da escola",
                "Siga reto por aproximadamente 15 passos",
                "Vire à direita e entre no refeitório",
                "Logo na entrada, a primeira sala à direita é a AAPM (Achados e Perdidos)"
            ],
            pontos_referencia=["Catraca", "Entrada do refeitório"],
            dicas_adicionais=None
        ),
    ),
    
    "quadro_vagas_refeitorio": Sala(
        nome="Quadro de vagas de emprego/estágio",
        tipo="instalacao",
        descricao="Quadro afirmativo com vagas de emprego e estágio",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala=None,
            referencia="No refeitório, entre a sala de Análise de Qualidade de Vida e a CoordEstágio",
            coordenadas=Coordenadas(lat=-22.123479, lon=-47.123479)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no refeitório",
                "Caminhe pela parede direita passando pela AAPM e Setor de Apoio",
                "O quadro fica entre a sala de Análise de Qualidade de Vida e a CoordEstágio"
            ],
            pontos_referencia=["AAPM", "Setor de Apoio", "CoordEstágio"],
            dicas_adicionais=None
        ),
    ),
    
    "coord_estagio": Sala(
        nome="Coordenação de Estágio",
        tipo="administrativo",
        descricao="Setor responsável pela coordenação de estágios",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="A-Estágio",
            referencia="Dentro do refeitório, ao lado da AAPM (após a TV)",
            coordenadas=Coordenadas(lat=-22.123460, lon=-47.123460)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Passe pela catraca na entrada da escola",
                "Siga reto por aproximadamente 15 passos",
                "Vire à direita e entre no refeitório",
                "Siga em direção à TV no fundo",
                "Após a primeira sala (AAPM), a sala ao lado é a CoordEstágio"
            ],
            pontos_referencia=["Catraca", "TV do refeitório", "AAPM"],
            dicas_adicionais=None
        ),
        horario_funcionamento="Segunda a Sexta, horário comercial"
    ),
    
    "setor_apoio": Sala(
        nome="Setor de Apoio (Análise de Qualidade de Vida)",
        tipo="administrativo",
        descricao="Setor de apoio ao aluno - Sala 204",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="204",
            referencia="Dentro do refeitório, última sala à direita",
            coordenadas=Coordenadas(lat=-22.123461, lon=-47.123461)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Passe pela catraca na entrada da escola",
                "Siga reto por aproximadamente 15 passos",
                "Vire à direita e entre no refeitório",
                "Siga pela direita até a última sala (Sala 204)"
            ],
            pontos_referencia=["Catraca", "Refeitório", "Sala 204"],
            dicas_adicionais="Horário: 07:30–17:30 e 18:30–21:00. Funcionários: Carla Ballestero e Fernanda Moreira"
        ),
        horario_funcionamento="Segunda a Sexta: 07:30–17:30 e 18:30–21:00"
    ),
    
    "cantina": Sala(
        nome="Cantina",
        tipo="instalacao",
        descricao="Cantina do refeitório",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala=None,
            referencia="Dentro do refeitório, ao fundo à esquerda",
            coordenadas=Coordenadas(lat=-22.123462, lon=-47.123462)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Passe pela catraca",
                "Siga reto ~15 passos e vire à direita",
                "Entre no refeitório e siga à esquerda até o fundo",
                "Ao lado dos puffs, vire à direita para a cantina"
            ],
            pontos_referencia=["Catraca", "Puffs"],
            dicas_adicionais=None
        ),
    ),
    
    "puffs": Sala(
        nome="Área dos Puffs",
        tipo="comum",
        descricao="Área de descanso com puffs no refeitório",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala=None,
            referencia="Última parte do refeitório, ao fundo à esquerda",
            coordenadas=Coordenadas(lat=-22.123463, lon=-47.123463)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Passe pela catraca",
                "Siga reto ~15 passos e vire à direita",
                "Entre no refeitório e siga à esquerda até o fundo"
            ],
            pontos_referencia=["Catraca"],
            dicas_adicionais=None
        ),
    ),
    
    "hidrante_refeitorio": Sala(
        nome="Hidrante (entrada do refeitório)",
        tipo="instalacao",
        descricao="Hidrante próximo à entrada do refeitório",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala=None,
            referencia="Parede da direita antes de entrar no refeitório",
            coordenadas=Coordenadas(lat=-22.123464, lon=-47.123464)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Passe pela catraca",
                "Siga reto ~15 passos e vire à direita",
                "Antes de entrar no refeitório, veja a parede à direita (hidrante)"
            ],
            pontos_referencia=["Catraca"],
            dicas_adicionais=None
        ),
    ),
    
    "extintor_refeitorio": Sala(
        nome="Extintores do refeitório",
        tipo="instalacao",
        descricao="Extintores próximos à sala de Análise de Qualidade de Vida e aos lixos",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala=None,
            referencia="Frente da sala de Análise de Qualidade de Vida e ao lado dos lixos",
            coordenadas=Coordenadas(lat=-22.123465, lon=-47.123465)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no refeitório",
                "Em frente à sala de Análise de Qualidade de Vida há um extintor",
                "Há outro ao lado dos lixos do refeitório"
            ],
            pontos_referencia=["Sala de Análise de Qualidade de Vida", "Lixos"],
            dicas_adicionais=None
        ),
    ),
    
    "alarme_bomba_incendio": Sala(
        nome="Alarme e Bomba de Incêndio",
        tipo="instalacao",
        descricao="Alarme e bomba na parede da direita antes do refeitório",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala=None,
            referencia="Parede da direita antes do refeitório",
            coordenadas=Coordenadas(lat=-22.123466, lon=-47.123466)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Passe pela catraca",
                "Siga reto ~15 passos e vire à direita",
                "Veja a parede à direita antes de entrar no refeitório"
            ],
            pontos_referencia=["Catraca"],
            dicas_adicionais=None
        ),
    ),
    
    "escada": Sala(
        nome="Escada",
        tipo="instalacao",
        descricao="Escada próxima ao Arquivo Morto, logo após a entrada",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala=None,
            referencia="Após a entrada, do lado esquerdo, próxima ao Arquivo Morto",
            coordenadas=Coordenadas(lat=-22.123467, lon=-47.123467)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no prédio pela entrada",
                "Veja o elevador à esquerda",
                "A escada fica um pouco adiante, também do lado esquerdo"
            ],
            pontos_referencia=["Arquivo Morto", "Elevador"],
            dicas_adicionais=None
        ),
    ),
    
    "elevador": Sala(
        nome="Elevador",
        tipo="instalacao",
        descricao="Elevador próximo ao Arquivo Morto, logo à esquerda da entrada",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala=None,
            referencia="Logo ao entrar, à esquerda",
            coordenadas=Coordenadas(lat=-22.123468, lon=-47.123468)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre pela entrada principal",
                "O elevador está à esquerda",
                "A escada fica mais adiante, também à esquerda"
            ],
            pontos_referencia=["Arquivo Morto"],
            dicas_adicionais=None
        ),
    ),
    
    "sala_preparacao_215": Sala(
        nome="Sala de Preparação (215)",
        tipo="instalacao",
        descricao="Sala de Preparação no andar de baixo",
        localizacao=Localizacao(
            predio="Principal",
            andar="Inferior",
            sala="215",
            referencia="Pelo corredor do refeitório, terceira porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123469, lon=-47.123469)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no refeitório e vire à esquerda",
                "Siga em direção aos puffs",
                "Entre no corredor à esquerda",
                "A terceira porta à esquerda é a Sala de Preparação (215)"
            ],
            pontos_referencia=["Puffs", "Corredor do refeitório"],
            dicas_adicionais=None
        ),
    ),
    
    "sala_tecnologia_32": Sala(
        nome="Sala de Tecnologia (32 alunos)",
        tipo="instalacao",
        descricao="Sala de Tecnologia no andar de baixo",
        localizacao=Localizacao(
            predio="Principal",
            andar="Inferior",
            sala="-",
            referencia="Pelo corredor do refeitório, terceira porta à direita",
            coordenadas=Coordenadas(lat=-22.123470, lon=-47.123470)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no refeitório e vire à esquerda",
                "Siga em direção aos puffs",
                "Entre no corredor à esquerda",
                "A terceira porta à direita é a Sala de Tecnologia"
            ],
            pontos_referencia=["Puffs"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_analise_mecanica_216": Sala(
        nome="Lab. de Análise de Mecânica (216)",
        tipo="laboratorio",
        descricao="Laboratório no andar de baixo",
        localizacao=Localizacao(
            predio="Principal",
            andar="Inferior",
            sala="216",
            referencia="Primeira porta à direita no corredor do refeitório",
            coordenadas=Coordenadas(lat=-22.123471, lon=-47.123471)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no refeitório e vire à esquerda",
                "Siga em direção aos puffs",
                "Entre no corredor à esquerda",
                "A primeira porta à direita é o Lab. de Análise de Mecânica (216)"
            ],
            pontos_referencia=["Puffs"],
            dicas_adicionais=None
        ),
    ),
    
    "banheiro_masc_214": Sala(
        nome="Banheiro Masculino (214)",
        tipo="instalacao",
        descricao="Banheiro masculino no andar de baixo",
        localizacao=Localizacao(
            predio="Principal",
            andar="Inferior",
            sala="214",
            referencia="Primeiras portas à esquerda no corredor do refeitório",
            coordenadas=Coordenadas(lat=-22.123472, lon=-47.123472)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no refeitório e vire à esquerda",
                "Siga em direção aos puffs",
                "Entre no corredor à esquerda",
                "A segunda porta à esquerda é o banheiro masculino (214)"
            ],
            pontos_referencia=["Puffs"],
            dicas_adicionais=None
        ),
    ),
    
    "banheiro_fem_213": Sala(
        nome="Banheiro Feminino (213)",
        tipo="instalacao",
        descricao="Banheiro feminino no andar de baixo",
        localizacao=Localizacao(
            predio="Principal",
            andar="Inferior",
            sala="213",
            referencia="Primeira porta à esquerda no corredor do refeitório",
            coordenadas=Coordenadas(lat=-22.123473, lon=-47.123473)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no refeitório e vire à esquerda",
                "Siga em direção aos puffs",
                "Entre no corredor à esquerda",
                "A primeira porta à esquerda é o banheiro feminino (213)"
            ],
            pontos_referencia=["Puffs"],
            dicas_adicionais=None
        ),
    ),
    
    "mecanica_automobilistica_223": Sala(
        nome="Área de Mecânica Automobilística (223)",
        tipo="laboratorio",
        descricao="Área com veículos, alinhamento, depósito, motores etc.",
        localizacao=Localizacao(
            predio="Oficinas",
            andar="Inferior",
            sala="223",
            referencia="Ao fim do corredor do refeitório, porta no fim",
            coordenadas=Coordenadas(lat=-22.123474, lon=-47.123474)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre no refeitório e vire à esquerda",
                "Siga até os puffs e entre no corredor à esquerda",
                "Siga até o fim do corredor e passe pela porta da área"
            ],
            pontos_referencia=["Puffs", "Corredor"],
            dicas_adicionais="Uso de EPIs é obrigatório"
        ),
    ),
    
    "lab_comandos_230": Sala(
        nome="Laboratório de Comandos (230)",
        tipo="laboratorio",
        descricao="Laboratório de Comandos na área de Eletroeletrônica",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="230",
            referencia="Ao fim do corredor térreo, primeira sala à frente",
            coordenadas=Coordenadas(lat=-22.123475, lon=-47.123475)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Siga reto pelo corredor principal do térreo",
                "No final, vire à direita e entre na porta",
                "Siga em frente: a primeira sala à frente é o Lab. de Comandos (230)"
            ],
            pontos_referencia=["Corredor principal"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_eletronica_229": Sala(
        nome="Laboratório de Eletrônica (229)",
        tipo="laboratorio",
        descricao="Laboratório de Eletrônica na área de Eletroeletrônica",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="229",
            referencia="Após o fim do corredor térreo, sequência de viradas direitas",
            coordenadas=Coordenadas(lat=-22.123476, lon=-47.123476)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Siga reto pelo corredor principal do térreo",
                "No final, vire à direita e entre na porta",
                "Siga em frente e vire novamente à direita",
                "A segunda porta à esquerda é o Laboratório de Eletrônica (229)"
            ],
            pontos_referencia=["Corredor principal"],
            dicas_adicionais=None
        ),
    ),
    
    "sala_aula_eletro_228": Sala(
        nome="Sala de Aula (Eletroeletrônica) (228)",
        tipo="instalacao",
        descricao="Sala de aula da área de Eletroeletrônica",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="228",
            referencia="Após o fim do corredor térreo, rota com duas direitas",
            coordenadas=Coordenadas(lat=-22.123477, lon=-47.123477)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Siga reto pelo corredor principal do térreo",
                "No final, vire à direita e entre na porta",
                "Siga em frente e vire novamente à direita",
                "A terceira porta à esquerda é a sala de aula (228)"
            ],
            pontos_referencia=["Corredor principal"],
            dicas_adicionais=None
        ),
    ),
    
    "biblioteca": Sala(
        nome="Biblioteca",
        tipo="comum",
        descricao="Biblioteca técnica com acervo especializado e área de estudos",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="103",
            referencia="Acesso pela rampa à esquerda da entrada; primeira porta à esquerda ao final da rampa",
            coordenadas=Coordenadas(lat=-22.123457, lon=-47.123457)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Desça a rampa",
                "A primeira porta à esquerda é a Biblioteca"
            ],
            pontos_referencia=["Escada principal", "Corredor do 1º andar"],
            dicas_adicionais="Há uma placa indicativa grande na porta"
        ),
        horario_funcionamento="Segunda a Quinta, das 8h30 às 13h30 e das 15h às 22h; Sextas, das 8h30 às 13h30 e das 15h às 21h; Sábados, das 8h às 12h15 e das 12h30 às 14h15"
    ),
    
    "lab_mecanica": Sala(
        nome="Laboratório de Mecânica",
        tipo="laboratorio",
        descricao="Laboratório equipado com tornos, fresas e equipamentos CNC",
        localizacao=Localizacao(
            predio="Oficinas",
            andar="Térreo",
            sala="O-01",
            referencia="Próximo ao estacionamento dos fundos",
            coordenadas=Coordenadas(lat=-22.123458, lon=-47.123458)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Da entrada principal, siga pelo corredor à direita",
                "Passe pelo pátio coberto",
                "Entre no prédio das oficinas",
                "O laboratório é a primeira porta à esquerda"
            ],
            pontos_referencia=["Pátio coberto", "Prédio das oficinas"],
            dicas_adicionais="Você pode identificar o laboratório pelo som das máquinas"
        ),
        capacidade=30
    ),

    "secretaria": Sala(
        nome="Secretaria",
        tipo="administrativo",
        descricao="Setor de atendimento e processos administrativos",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="A-01",
            referencia="Ao lado da entrada principal",
            coordenadas=Coordenadas(lat=-22.123459, lon=-47.123459)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre pela porta principal",
                "A secretaria é a primeira sala à esquerda",
                "Procure o balcão de atendimento"
            ],
            pontos_referencia=["Entrada principal", "Hall de entrada"],
            dicas_adicionais="Há uma TV com senhas de atendimento no local"
        ),
        horario_funcionamento="Segunda a Sexta, das 7h às 21h"
    ),

    # ANDAR SUPERIOR - CORREDOR ESQUERDO
    
    "lab_comandos_acionamentos_334": Sala(
        nome="Lab. Comandos e Acionamentos (334)",
        tipo="laboratorio",
        descricao="Laboratório de Comandos e Acionamentos no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="334",
            referencia="Após subir pela escada principal, corredor esquerdo, próximo ao relógio",
            coordenadas=Coordenadas(lat=-22.123480, lon=-47.123480)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda e siga reto",
                "Você verá um relógio - caminhe em direção a ele",
                "O laboratório é a sala logo à frente à esquerda"
            ],
            pontos_referencia=["Escada principal", "Relógio do corredor"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_eletronica_geral_332": Sala(
        nome="Lab. Eletrônica Geral (332)",
        tipo="laboratorio",
        descricao="Laboratório de Eletrônica Geral no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="332",
            referencia="Corredor esquerdo, última sala à direita no final",
            coordenadas=Coordenadas(lat=-22.123481, lon=-47.123481)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "Siga até o final do corredor",
                "A última sala à direita é o Lab. de Eletrônica Geral"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_pneumatica_331": Sala(
        nome="Lab. Pneumática (331)",
        tipo="laboratorio",
        descricao="Laboratório de Pneumática no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="331",
            referencia="Corredor esquerdo, penúltima sala do lado direito",
            coordenadas=Coordenadas(lat=-22.123482, lon=-47.123482)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda e continue andando",
                "O Lab. de Pneumática é a penúltima sala do lado direito"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_hidraulica_328": Sala(
        nome="Lab. Hidráulica (328)",
        tipo="laboratorio",
        descricao="Laboratório de Hidráulica no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="328",
            referencia="Corredor esquerdo, ao lado da Coordenação no lado direito",
            coordenadas=Coordenadas(lat=-22.123483, lon=-47.123483)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "Siga em frente até encontrar o Lab. de Hidráulica",
                "Fica ao lado da Coordenação no lado direito"
            ],
            pontos_referencia=["Escada principal", "Sala de Coordenação"],
            dicas_adicionais=None
        ),
    ),
    
    "coordenacao_326": Sala(
        nome="Sala de Coordenação (326)",
        tipo="administrativo",
        descricao="Sala de coordenação pedagógica - Sala 326",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="326",
            referencia="Corredor esquerdo, próximo ao final, ao lado do banheiro masculino",
            coordenadas=Coordenadas(lat=-22.123484, lon=-47.123484)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "Vá andando até quase o final do corredor",
                "A Coordenação (Sala 326) fica ao lado do banheiro masculino, do lado direito"
            ],
            pontos_referencia=["Escada principal", "Banheiro masculino", "Sala 326"],
            dicas_adicionais="Funcionário: Julio Cesar Melli (Coordenador de Atividades Pedagógicas)"
        ),
        horario_funcionamento="Segunda a Sexta: 07:30–17:30"
    ),
    
    "banheiro_masc_1_andar": Sala(
        nome="Banheiro Masculino (1º Andar)",
        tipo="instalacao",
        descricao="Banheiro masculino no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="-",
            referencia="Corredor esquerdo, à direita próximo da Coordenação",
            coordenadas=Coordenadas(lat=-22.123485, lon=-47.123485)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba a escada principal",
                "Vire à esquerda no corredor",
                "Siga reto, o banheiro masculino estará à direita",
                "Próximo da Sala de Coordenação"
            ],
            pontos_referencia=["Escada principal", "Sala de Coordenação"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_informatica_ii_315": Sala(
        nome="Lab. Informática II (40 lugares) (315)",
        tipo="laboratorio",
        descricao="Laboratório de informática com 40 lugares",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="315",
            referencia="Corredor esquerdo, primeira porta à direita antes do banheiro masculino",
            coordenadas=Coordenadas(lat=-22.123486, lon=-47.123486)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba a escada principal",
                "Vire à esquerda no corredor",
                "A primeira porta à direita é o Lab. Informática II (40 lugares)"
            ],
            pontos_referencia=["Escada principal", "Banheiro masculino"],
            dicas_adicionais=None
        ),
        capacidade=40
    ),
    
    "lab_informatica_vii_321": Sala(
        nome="Lab. Informática VII (20 lugares) (321)",
        tipo="laboratorio",
        descricao="Laboratório de informática com 20 lugares - sala de vidro",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="321",
            referencia="Corredor esquerdo, segunda porta à direita - salas de vidro",
            coordenadas=Coordenadas(lat=-22.123487, lon=-47.123487)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "A segunda porta à direita são as salas de vidro",
                "A sala 321 é uma delas"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais="Salas de vidro são facilmente identificáveis"
        ),
        capacidade=20
    ),
    
    "lab_informatica_vi_319": Sala(
        nome="Lab. Informática VI (20 lugares) (319)",
        tipo="laboratorio",
        descricao="Laboratório de informática com 20 lugares - sala de vidro",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="319",
            referencia="Corredor esquerdo, primeira sala de vidro à direita, ao lado da 321",
            coordenadas=Coordenadas(lat=-22.123488, lon=-47.123488)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "A primeira porta à direita é uma das salas de vidro",
                "Esta é a sala 319, ao lado da sala 321"
            ],
            pontos_referencia=["Escada principal", "Sala 321"],
            dicas_adicionais=None
        ),
        capacidade=20
    ),
    
    "servidor_educacional_318": Sala(
        nome="Servidor Educacional (318)",
        tipo="instalacao",
        descricao="Sala do servidor educacional",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="318",
            referencia="Corredor esquerdo, à direita ao lado do banheiro feminino",
            coordenadas=Coordenadas(lat=-22.123489, lon=-47.123489)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba a escada principal",
                "Vire à esquerda no corredor",
                "O Servidor fica à direita ao lado do banheiro feminino"
            ],
            pontos_referencia=["Escada principal", "Banheiro feminino"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_informatica_iii_320": Sala(
        nome="Lab. III Informática/CAD (320)",
        tipo="laboratorio",
        descricao="Laboratório de Informática e CAD",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="320",
            referencia="Corredor esquerdo, primeira porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123490, lon=-47.123490)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "O Lab. III de Informática/CAD é a primeira porta à esquerda"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_informatica_iv_322": Sala(
        nome="Lab. IV Informática/CAD (322)",
        tipo="laboratorio",
        descricao="Laboratório de Informática e CAD",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="322",
            referencia="Corredor esquerdo, segunda porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123491, lon=-47.123491)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "O Lab. IV de Informática/CAD é a segunda porta à esquerda"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_informatica_v_324": Sala(
        nome="Lab. V Informática (324)",
        tipo="laboratorio",
        descricao="Laboratório de Informática",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="324",
            referencia="Corredor esquerdo, terceira porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123492, lon=-47.123492)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "O Lab. V de Informática é a terceira porta à esquerda"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "sala_aula_323": Sala(
        nome="Sala de Aula (323)",
        tipo="instalacao",
        descricao="Sala de aula no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="323",
            referencia="Corredor esquerdo, quarta porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123493, lon=-47.123493)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "A sala de aula 323 é a quarta porta à esquerda"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "lab_comandos_logicos_327": Sala(
        nome="Lab. Comandos Lógicos e Programáveis (327)",
        tipo="laboratorio",
        descricao="Laboratório de Comandos Lógicos e Programáveis",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="327",
            referencia="Corredor esquerdo, quinta porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123494, lon=-47.123494)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à esquerda no corredor",
                "O laboratório é a quinta porta à esquerda"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),

    # ANDAR SUPERIOR - CORREDOR DIREITO
    
    "banheiro_fem_1_andar_316": Sala(
        nome="Banheiro Feminino (316)",
        tipo="instalacao",
        descricao="Banheiro feminino no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="316",
            referencia="Logo à frente ao subir a escada principal",
            coordenadas=Coordenadas(lat=-22.123495, lon=-47.123495)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Logo à sua frente estão os banheiros femininos"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "banheiro_acessivel_314": Sala(
        nome="Banheiro Acessível (314)",
        tipo="instalacao",
        descricao="Banheiro acessível no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="314",
            referencia="Logo à frente ao subir a escada principal",
            coordenadas=Coordenadas(lat=-22.123496, lon=-47.123496)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Logo à sua frente estão os banheiros acessíveis"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "banheiro_acessivel_313": Sala(
        nome="Banheiro Acessível (313)",
        tipo="instalacao",
        descricao="Banheiro acessível no andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="313",
            referencia="Logo à frente ao subir a escada principal",
            coordenadas=Coordenadas(lat=-22.123497, lon=-47.123497)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Logo à sua frente estão os banheiros acessíveis"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "sala_preparacao_cst": Sala(
        nome="Sala de Preparação CST",
        tipo="instalacao",
        descricao="Sala de preparação para cursos superiores de tecnologia",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="-",
            referencia="Corredor direito, ao lado dos banheiros femininos à esquerda",
            coordenadas=Coordenadas(lat=-22.123498, lon=-47.123498)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba a escada principal",
                "Vire à direita no corredor e vá reto",
                "A Sala de Preparação CST fica ao lado dos banheiros femininos à sua esquerda"
            ],
            pontos_referencia=["Escada principal", "Banheiros femininos"],
            dicas_adicionais=None
        ),
    ),
    
    "sala_desenho_tecnico_308": Sala(
        nome="Sala Desenho Técnico (40 lugares) (308)",
        tipo="instalacao",
        descricao="Sala de desenho técnico com 40 lugares",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="308",
            referencia="Corredor direito, após descer a rampa, primeira sala à esquerda",
            coordenadas=Coordenadas(lat=-22.123499, lon=-47.123499)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à direita e siga reto pelo corredor",
                "Entre em um tipo de rampa e desça ela",
                "A Sala de Desenho Técnico é a primeira do lado esquerdo"
            ],
            pontos_referencia=["Escada principal", "Rampa"],
            dicas_adicionais=None
        ),
        capacidade=40
    ),
    
    "lab_projetos_307": Sala(
        nome="Lab. Projetos (20 lugares) (307)",
        tipo="laboratorio",
        descricao="Laboratório de projetos com 20 lugares",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="307",
            referencia="Corredor direito, após descer a rampa, segunda sala à esquerda",
            coordenadas=Coordenadas(lat=-22.123500, lon=-47.123500)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à direita no corredor e siga em frente",
                "Desça a rampa",
                "O Lab. de Projetos é a segunda sala à sua esquerda"
            ],
            pontos_referencia=["Escada principal", "Rampa"],
            dicas_adicionais=None
        ),
        capacidade=20
    ),
    
    "auditorio_305": Sala(
        nome="Auditório (305)",
        tipo="instalacao",
        descricao="Auditório para eventos e apresentações",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="305",
            referencia="Final do corredor direito, início do novo corredor à direita",
            coordenadas=Coordenadas(lat=-22.123501, lon=-47.123501)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à direita no corredor",
                "Vá até o final e vire à direita novamente",
                "O Auditório é no início do corredor, do lado direito"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),
    
    "sala_aula_306": Sala(
        nome="Sala de Aula (20 lugares) (306)",
        tipo="instalacao",
        descricao="Sala de aula com 20 lugares",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="306",
            referencia="Final do corredor direito, após virar à direita, primeira porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123502, lon=-47.123502)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à direita no corredor",
                "Vá até o final, virando à direita",
                "A Sala 306 é a primeira porta à sua esquerda"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
        capacidade=20
    ),
    
    "sala_aula_304": Sala(
        nome="Sala de Aula (20 lugares) (304)",
        tipo="instalacao",
        descricao="Sala de aula com 20 lugares",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="304",
            referencia="Final do corredor direito, após virar à direita, segunda porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123503, lon=-47.123503)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à direita no corredor",
                "Vá até o final, virando à direita",
                "A Sala 304 é a segunda porta à sua esquerda"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
        capacidade=20
    ),
    
    "lab_robotica_330": Sala(
        nome="Lab. de Robótica (330)",
        tipo="laboratorio",
        descricao="Laboratório de robótica",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="330",
            referencia="Final do corredor direito, após virar à direita, terceira porta à esquerda",
            coordenadas=Coordenadas(lat=-22.123504, lon=-47.123504)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à direita no corredor",
                "Vá até o final, virando à direita",
                "O Lab. de Robótica é a terceira porta à sua esquerda"
            ],
            pontos_referencia=["Escada principal"],
            dicas_adicionais=None
        ),
    ),

    # ESCADAS E ACESSOS
    
    "escada_principal": Sala(
        nome="Escada Principal",
        tipo="instalacao",
        descricao="Escada principal de acesso ao andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="-",
            referencia="Logo na entrada do prédio, de frente para o elevador",
            coordenadas=Coordenadas(lat=-22.123505, lon=-47.123505)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Entre pela entrada principal",
                "A escada principal fica logo na entrada",
                "Está de frente para o elevador"
            ],
            pontos_referencia=["Entrada principal", "Elevador"],
            dicas_adicionais="Dá acesso direto ao corredor central do andar superior"
        ),
    ),
    
    "escada_final_bloco": Sala(
        nome="Escada Final do Bloco",
        tipo="instalacao",
        descricao="Escada no final do bloco que dá acesso aos fundos do andar superior",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="-",
            referencia="Final do corredor principal do térreo, à direita",
            coordenadas=Coordenadas(lat=-22.123506, lon=-47.123506)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Siga reto pelo corredor principal do térreo",
                "Passe pelas salas e laboratórios",
                "Ao final do corredor, você verá uma escada no canto à direita",
                "Esta é a escada final do bloco"
            ],
            pontos_referencia=["Corredor principal"],
            dicas_adicionais="Dá acesso à parte dos fundos do andar superior"
        ),
    ),
    
    # Salas adicionais
    "sala_128": Sala(
        nome="Sala 128",
        tipo="instalacao",
        descricao="Sala de aula ou laboratório",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="128",
            referencia="Corredor direito do 1º andar",
            coordenadas=Coordenadas(lat=-22.123500, lon=-47.123500)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Suba pela escada principal",
                "Vire à direita no corredor do 1º andar",
                "Siga reto até encontrar a sala 128"
            ],
            pontos_referencia=["Escada principal", "Corredor direito"],
            dicas_adicionais="Verifique a numeração das salas no corredor"
        ),
    ),
    
    "sala_137": Sala(
        nome="Sala 137",
        tipo="instalacao", 
        descricao="Sala de computadores",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="137",
            referencia="Corredor direito do 1º andar",
            coordenadas=Coordenadas(lat=-22.123501, lon=-47.123501)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca de entrada, siga à esquerda",
                "Você encontrará uma rampa",
                "Desça a rampa até a escada",
                "Ao chegar ao final, vire à direita no corredor",
                "A Sala 137 estará logo à sua esquerda, sendo a primeira porta que você verá"
            ],
            pontos_referencia=["Catraca", "Rampa", "Escada"],
            dicas_adicionais="Primeira porta à esquerda no corredor"
        ),
    ),
    
    # Salas do andar inferior (1º andar - área da biblioteca)
    "biblioteca_115": Sala(
        nome="Biblioteca (115)",
        tipo="comum",
        descricao="Biblioteca técnica com acervo especializado",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="115",
            referencia="Primeira porta à esquerda após descer a rampa",
            coordenadas=Coordenadas(lat=-22.123502, lon=-47.123502)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "A Biblioteca é a primeira porta à sua esquerda"
            ],
            pontos_referencia=["Catraca", "Rampa"],
            dicas_adicionais="Há uma placa indicativa grande na porta"
        ),
        horario_funcionamento="Segunda a Quinta, das 8h30 às 13h30 e das 15h às 22h; Sextas, das 8h30 às 13h30 e das 15h às 21h; Sábados, das 8h às 12h15 e das 12h30 às 14h15"
    ),
    
    "sala_orientador_rainer": Sala(
        nome="Sala do Orientador (Rainer)",
        tipo="administrativo",
        descricao="Sala do orientador educacional",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="-",
            referencia="Segunda porta à direita após descer a rampa",
            coordenadas=Coordenadas(lat=-22.123503, lon=-47.123503)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "Vire no primeiro corredor à sua direita",
                "A sala do Orientador é a segunda porta à sua direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Primeiro corredor à direita"],
            dicas_adicionais="Sala do orientador Rainer"
        ),
    ),
    
    "sanitario_fem_usinagem": Sala(
        nome="Sanitário Feminino (Usinagem)",
        tipo="instalacao",
        descricao="Sanitário feminino da área de usinagem",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="-",
            referencia="Terceira porta à direita após descer a rampa",
            coordenadas=Coordenadas(lat=-22.123504, lon=-47.123504)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "Vire no primeiro corredor à sua direita",
                "O Sanitário Feminino é a terceira porta à sua direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Primeiro corredor à direita"],
            dicas_adicionais="Área de usinagem"
        ),
    ),
    
    "sanitario_masc_usinagem": Sala(
        nome="Sanitário Masculino (Usinagem)",
        tipo="instalacao",
        descricao="Sanitário masculino da área de usinagem",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="-",
            referencia="Quinta porta à direita após descer a rampa",
            coordenadas=Coordenadas(lat=-22.123505, lon=-47.123505)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "Vire no primeiro corredor à sua direita",
                "O Sanitário Masculino é a quinta porta à sua direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Primeiro corredor à direita"],
            dicas_adicionais="Área de usinagem"
        ),
    ),
    
    "lab_informatica_i_129": Sala(
        nome="Lab. Informática I (129)",
        tipo="laboratorio",
        descricao="Laboratório de informática I",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="129",
            referencia="Sexta porta à direita após descer a rampa",
            coordenadas=Coordenadas(lat=-22.123506, lon=-47.123506)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "Vire no primeiro corredor à sua direita",
                "O Lab. de Informática I é a sexta porta à sua direita (Sala logo após o Lavatório)"
            ],
            pontos_referencia=["Catraca", "Rampa", "Primeiro corredor à direita", "Lavatório"],
            dicas_adicionais="Logo após o lavatório"
        ),
    ),
    
    "sala_aula_16_alunos_130": Sala(
        nome="Sala de Aula (16 Alunos) (130)",
        tipo="instalacao",
        descricao="Sala de aula com capacidade para 16 alunos",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="130",
            referencia="Sétima porta à direita após descer a rampa",
            coordenadas=Coordenadas(lat=-22.123507, lon=-47.123507)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "Vire no primeiro corredor à sua direita",
                "A Sala de Aula é a sétima porta à sua direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Primeiro corredor à direita"],
            dicas_adicionais="Capacidade para 16 alunos"
        ),
        capacidade=16
    ),
    
    "lab_metrol_dimensional_131": Sala(
        nome="Lab. Metrol. Dimensional (131)",
        tipo="laboratorio",
        descricao="Laboratório de Metrologia Dimensional",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="131",
            referencia="Oitava porta à direita após descer a rampa",
            coordenadas=Coordenadas(lat=-22.123508, lon=-47.123508)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "Vire no primeiro corredor à sua direita",
                "O Lab. Metrol. Dimensional é a oitava porta à sua direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Primeiro corredor à direita"],
            dicas_adicionais="Laboratório de metrologia dimensional"
        ),
    ),
    
    "lab_metrol_tridimensional_132": Sala(
        nome="Lab. Metrol. Tridimensional (132)",
        tipo="laboratorio",
        descricao="Laboratório de Metrologia Tridimensional",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="132",
            referencia="Oitava porta à direita após descer a rampa",
            coordenadas=Coordenadas(lat=-22.123509, lon=-47.123509)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "Vire no primeiro corredor à sua direita",
                "O Lab. Metrol. Tridimensional é a oitava porta à sua direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Primeiro corredor à direita"],
            dicas_adicionais="Laboratório de metrologia tridimensional"
        ),
    ),
    
    "sala_aula_32_alunos_133": Sala(
        nome="Sala de Aula (32 Alunos) (133)",
        tipo="instalacao",
        descricao="Sala de aula com capacidade para 32 alunos",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="133",
            referencia="Última porta no fim do corredor à direita",
            coordenadas=Coordenadas(lat=-22.123510, lon=-47.123510)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca da entrada, vire à esquerda",
                "Você verá uma rampa",
                "Desça a rampa",
                "Vire no primeiro corredor à sua direita",
                "A sala de aula é a última porta no fim do corredor à sua direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Primeiro corredor à direita"],
            dicas_adicionais="Capacidade para 32 alunos"
        ),
        capacidade=32
    ),
    
    "senai_lab": Sala(
        nome="SENAI LAB",
        tipo="laboratorio",
        descricao="Laboratório SENAI",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="-",
            referencia="À direita após descer a rampa e virar no corredor",
            coordenadas=Coordenadas(lat=-22.123511, lon=-47.123511)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca de entrada, siga à esquerda",
                "Você encontrará uma rampa",
                "Desça a rampa até a escada",
                "Ao chegar ao final, vire à direita no corredor",
                "O SENAI LAB estará logo à sua direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Escada"],
            dicas_adicionais="Laboratório SENAI"
        ),
    ),
    
    "oficina": Sala(
        nome="Oficina",
        tipo="laboratorio",
        descricao="Oficina de práticas",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="-",
            referencia="À direita após a curva no corredor",
            coordenadas=Coordenadas(lat=-22.123512, lon=-47.123512)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Após passar pela catraca de entrada, siga à esquerda",
                "Você encontrará uma rampa",
                "Desça até a escada",
                "Ao chegar ao final, vire à direita no corredor",
                "A oficina estará à sua direita, logo após a curva"
            ],
            pontos_referencia=["Catraca", "Rampa", "Escada", "Curva"],
            dicas_adicionais="Oficina de práticas"
        ),
    ),
    
    "uplab": Sala(
        nome="UPLAB",
        tipo="laboratorio",
        descricao="Laboratório UPLAB",
        localizacao=Localizacao(
            predio="Principal",
            andar="1º Andar",
            sala="-",
            referencia="À esquerda após descer a rampa e virar no corredor",
            coordenadas=Coordenadas(lat=-22.123513, lon=-47.123513)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Após passar pela catraca de entrada, siga à esquerda",
                "Você encontrará uma rampa",
                "Desça até a escada",
                "Ao chegar ao final, vire à direita no corredor",
                "O UPLAB estará à sua esquerda"
            ],
            pontos_referencia=["Catraca", "Rampa", "Escada"],
            dicas_adicionais="Laboratório UPLAB"
        ),
    ),
    
    "sala_diretor_marcio": Sala(
        nome="Sala do Diretor Márcio Marinho",
        tipo="administrativo",
        descricao="Sala do Diretor de Unidade de Formação Profissional",
        localizacao=Localizacao(
            predio="Principal",
            andar="Térreo",
            sala="-",
            referencia="Primeira porta à direita após descer a rampa e virar no corredor",
            coordenadas=Coordenadas(lat=-22.123514, lon=-47.123514)
        ),
        navegacao=Navegacao(
            instrucoes=[
                "Ao passar pela catraca de entrada, siga à esquerda até encontrar uma rampa",
                "Desça a rampa até o final, onde há uma escada",
                "Ao chegar ao fim da escada, vire à esquerda no corredor e, logo em seguida, à direita",
                "A sala do diretor é a primeira porta à direita"
            ],
            pontos_referencia=["Catraca", "Rampa", "Escada"],
            dicas_adicionais="Sala do Diretor Márcio Vieira Marinho"
        ),
    )
}

def obter_navegacao(local: str, ponto_partida: str = "entrada_principal") -> str:
    """
    Retorna instruções de navegação formatadas para um local específico
    """
    if local not in SALAS:
        return "Desculpe, não tenho informações sobre como chegar a este local."
        
    sala = SALAS[local]
    nav = sala.navegacao
    
    # Monta a resposta
    resposta = f"Para chegar ao {sala.nome}:\n"
    resposta += "\n".join(f"- {instrucao}" for instrucao in nav.instrucoes)
    
    if nav.dicas_adicionais:
        resposta += f"\n\n{nav.dicas_adicionais}"
        
    return resposta

def buscar_sala_por_nome(nome: str) -> Optional[Sala]:
    """
    Busca uma sala pelo nome ou palavras-chave
    """
    nome = nome.lower()
    for key, sala in SALAS.items():
        if nome in key.lower() or nome in sala.nome.lower():
            return sala
    return None 