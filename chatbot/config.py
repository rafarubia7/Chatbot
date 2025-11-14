"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

#Banco de dados MySQL
# Configurações do MySQL
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'aluno')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'senAI')

# URI de conexão MySQL
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'

# Configurações do Flask
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'sua-chave-secreta-aqui')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

#NOME DO MODELO PARA BAIXAR NO LMSTUDIO E USAR AQUI
#COPIE E COLE ISSO: "Llama-3.2-3B-Instruct-GGUF"

# Configurações do LM Studio
LM_STUDIO_URL = os.getenv('LM_STUDIO_URL', 'http://localhost:1234/v1/completions')
MODEL_NAME = os.getenv('MODEL_NAME', 'llama-3.2-3b-instruct')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 60))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 1))

# Alias para compatibilidade com o código existente
URL_LM_STUDIO = LM_STUDIO_URL
NOME_MODELO = MODEL_NAME
TIMEOUT_REQUISICAO = REQUEST_TIMEOUT
MAX_TENTATIVAS = MAX_RETRIES
DELAY_TENTATIVA = RETRY_DELAY

# Configurações de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')

# Configurações de sessão
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = 1800  # 30 minutos

# Configurações de cache
CACHE_TIMEOUT = 300  # 5 minutos

# Configurações de logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'