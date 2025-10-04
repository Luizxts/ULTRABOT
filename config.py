import os
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÃO BYBIT REAL
BYBIT_CONFIG = {
    'api_key': os.getenv('BYBIT_API_KEY_REAL'),
    'api_secret': os.getenv('BYBIT_API_SECRET_REAL'),
    'testnet': os.getenv('BYBIT_TESTNET', 'false').lower() == 'true'
}

# TELEGRAM CONFIG
TELEGRAM_CONFIG = {
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID')
}

# TRADING CONFIG
TRADING_CONFIG = {
    'ativo_principal': 'BTCUSDT',
    'pares_monitorados': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
    'intervalo_analise': 30,
    'risk_per_trade': 0.02,
    'max_positions': 3,
    'modo_real': True,
    'valor_por_trade': 50
}

# WEB DASHBOARD CONFIG
WEB_CONFIG = {
    'port': int(os.getenv('PORT', 5000)),
    'host': '0.0.0.0',
    'debug': False
}

# LOGGING CONFIG
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
