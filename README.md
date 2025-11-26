# Chatbot SENAI São Carlos - Cadu

Chatbot inteligente desenvolvido para o SENAI São Carlos, utilizando processamento de linguagem natural para fornecer informações sobre cursos, horários, funcionários, salas e outros assuntos relacionados à instituição.

## Sobre o Projeto

O Cadu é um assistente virtual desenvolvido para auxiliar alunos, funcionários e visitantes do SENAI São Carlos com informações institucionais. O sistema utiliza integração com LM Studio para processamento de linguagem natural e oferece uma interface web moderna e intuitiva.

## Funcionalidades

- Chat Inteligente: Conversação natural com processamento de linguagem natural via LM Studio
- Sistema de Autenticação: Login e registro de usuários
- Gerenciamento de Conversas: Histórico de chats, salvar e deletar conversas
- Perfil de Usuário: Edição de perfil com upload de avatar
- Busca de Informações: Acesso a informações sobre:
  - Cursos oferecidos
  - Horários de professores, salas e turmas
  - Funcionários
  - Processos administrativos
  - Informações institucionais
- Cache Inteligente: Sistema de cache para otimizar respostas
- Sessões Seguras: Gerenciamento de sessões por usuário

## Tecnologias Utilizadas

### Backend
- Flask 3.0.2: Framework web Python
- SQLAlchemy: ORM para banco de dados
- PyMySQL: Driver MySQL para Python
- Flask-CORS: Suporte a CORS
- python-dotenv: Gerenciamento de variáveis de ambiente

### Banco de Dados
- MySQL: Banco de dados relacional

### Processamento de Linguagem Natural
- LM Studio: Integração com modelos de linguagem local
- FuzzyWuzzy: Busca fuzzy para correspondência de texto

### Frontend
- HTML5, CSS3, JavaScript
- Interface responsiva e moderna

## Pré-requisitos

Antes de começar, você precisará ter instalado:

- Python 3.8 ou superior
- MySQL 5.7 ou superior
- LM Studio (para processamento de linguagem natural)
- Git (opcional)

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd chatbot
```


### 2. Instale as dependências

```bash
pip install -r requirements.txt
```


### 3. Configure o banco de dados

Execute o script SQL para criar o banco de dados:

```bash
mysql -u root -p < create_database.sql
```

Ou execute manualmente no MySQL:

```sql
mysql -u root -p
source create_database.sql
```


### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Banco de Dados MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=senAI

# Flask
FLASK_SECRET_KEY=sua-chave-secreta-aqui
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# LM Studio
LM_STUDIO_URL=http://localhost:1234/v1/completions
MODEL_NAME=llama-3.2-3b-instruct
REQUEST_TIMEOUT=60
MAX_RETRIES=3
RETRY_DELAY=1

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```


### 5. Configure o LM Studio

1. Baixe e instale o [LM Studio](https://lmstudio.ai/)
2. Baixe o modelo recomendado: Llama-3.2-3B-Instruct-GGUF
3. Inicie o servidor local no LM Studio na porta 1234
4. Certifique-se de que o modelo está carregado e pronto para uso


## Como Executar

### 1. Inicie o LM Studio

Certifique-se de que o LM Studio está rodando com o modelo carregado na porta 1234.


### 2. Execute a aplicação

```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:5000`


### 3. Acesse no navegador

Abra seu navegador e acesse:
- Página inicial: http://localhost:5000
- Login: http://localhost:5000/login
- Chat: http://localhost:5000/chat (requer login)


## Estrutura do Projeto

```
chatbot/
├── app.py                      # Aplicação principal Flask
├── config.py                   # Configurações da aplicação
├── requirements.txt            # Dependências Python
├── create_database.sql         # Script de criação do banco
├── limpar_cache.py             # Script para limpar cache
├── sistema_de_cache.json       # Arquivo de cache
│
├── info/                       # Módulo de informações
│   ├── base_info.py           # Informações base do SENAI
│   ├── cursos.py              # Informações sobre cursos
│   ├── funcionarios.py        # Informações sobre funcionários
│   ├── horarios.py            # Gerenciamento de horários
│   ├── horarios/              # Arquivos JSON de horários
│   │   ├── horarios_professores/
│   │   ├── horarios_salas/
│   │   └── horarios_turmas/
│   ├── info_manager.py        # Gerenciador de informações
│   ├── informacoes_adicionais.py
│   ├── institucional.py       # Informações institucionais
│   ├── processos.py           # Processos administrativos
│   ├── respostas.py           # Respostas padrão
│   ├── salas.py               # Informações sobre salas
│   └── search.py              # Sistema de busca
│
├── models/                     # Modelos de dados
│   └── sqlalchemy_models.py   # Modelos SQLAlchemy
│
├── utils/                      # Utilitários
│   ├── chat_manager.py        # Gerenciador de chat
│   ├── gerenciador_chat.py    # Gerenciador de conversas
│   ├── gerenciador_sessao.py  # Gerenciador de sessões
│   ├── response_cache.py      # Sistema de cache
│   └── session_manager.py     # Gerenciador de sessões
│
├── static/                     # Arquivos estáticos
│   ├── uploads/               # Uploads de usuários
│   │   └── avatars/           # Avatares dos usuários
│   ├── default-avatar.svg     # Avatar padrão
│   └── favicon.png            # Favicon
│
└── templates/                  # Templates HTML
    ├── chat.html              # Página do chat
    ├── index.html             # Página inicial
    ├── info.html              # Página de informações
    ├── login.html             # Página de login
    ├── profile.html           # Página de perfil
    ├── register.html          # Página de registro
    └── tela.html              # Tela inicial
```


### Banco de Dados

O sistema usa MySQL por padrão.


### Cache

O sistema utiliza cache para otimizar respostas. Para limpar o cache:

```bash
python limpar_cache.py
```


## Usuários Padrão

O sistema cria automaticamente os seguintes usuários padrão para testes:

- Email: usuario@gmail.com | Senha: senha123
- Email: usuario@icloud.com | Senha: senha123
- Email: usuario@facebook.com | Senha: senha123

Importante: Altere essas credenciais em produção!


### Autenticação
- `GET /login` - Página de login
- `POST /login` - Processar login
- `GET /register` - Página de registro
- `POST /register` - Processar registro
- `GET /logout` - Fazer logout


### Chat
- `POST /api/chat` - Enviar mensagem e receber resposta
- `GET /api/chat/history` - Obter histórico do chat
- `POST /api/chat/save` - Salvar chat
- `GET /api/chat/list` - Listar todos os chats
- `POST /api/chat/delete` - Deletar chat
- `POST /api/chat/update_title` - Atualizar título do chat


### Perfil
- `GET /api/profile` - Obter dados do perfil
- `POST /api/update-profile` - Atualizar perfil
- `POST /api/upload-avatar` - Upload de avatar
- `GET /api/check-updates` - Verificar atualizações


## Licença

Este projeto é desenvolvido para o SENAI São Carlos.


## Contribuidores

Desenvolvido para o SENAI São Carlos.


## Suporte

Para mais informações sobre o SENAI São Carlos:
- Site: https://sp.senai.br/unidade/saocarlos/
- Email: Verifique as informações no arquivo `info/base_info.py`

---

## Deselvolvedores 
- Lívia Maria Monteiro;
- Julia Vitória Ferreira Stapavicci;
- Kelvin Brito Negrini Alves;
- Rafael Rubiá Oliveria Cardoso.

## LinkedIn
[rafa_rubia7](https://www.linkedin.com/in/rafa_rubia7)

---

Desenvolvido para o SENAI São Carlos

