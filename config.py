# config.py - CONFIGURAÇÕES SENSÍVEIS - NUNCA COMPARTILHE!

# =============================================
# BYBIT API - CONTA PRINCIPAL (REAL)
# =============================================
BYBIT_API_KEY = "g9NOzMIa9Ye7lJ6QCI"
BYBIT_API_SECRET = "c9TdmpaeB0mxSmJQxa00BDevU6eT3Yze48X2"

# =============================================
# TELEGRAM CONFIGURATION
# =============================================
TELEGRAM_BOT_TOKEN = "8444269740:AAE2dlSXozV4cIGNMMs72APIDcrYBvIq31M"
TELEGRAM_CHAT_ID = "-4977542145"

# =============================================
# TRADING CONFIGURATION
# =============================================
TRADING_MODE = "SIMULATION"  # MUDE PARA "REAL" QUANDO ESTIVER PRONTO
INITIAL_BALANCE = 1000.00
RISK_PERCENTAGE = 2.0  # 2% por trade

# =============================================
# TRADING STRATEGY SETTINGS
# =============================================
TRADING_INTERVAL = 300  # 5 minutos em segundos
TRADE_PROBABILITY = 0.3  # 30% chance de trade
WIN_RATE = 0.65  # 65% win rate
MAX_TRADE_AMOUNT = 50  # Máximo $50 por trade
TRADE_PERCENTAGE = 0.05  # 5% do saldo por trade

# =============================================
# WEB INTERFACE SETTINGS
# =============================================
HOST = "0.0.0.0"
PORT = 5000
FLASK_SECRET_KEY = "ultrabot_pro_secret_key_2024_v2"

# =============================================
# LOGGING AND MONITORING
# =============================================
LOG_LEVEL = "INFO"
SAVE_HISTORY = True
MAX_HISTORY_ENTRIES = 100
MAX_NOTIFICATIONS = 50

# =============================================
# SECURITY SETTINGS
# =============================================
ENABLE_TELEGRAM_COMMANDS = True
ALLOW_REMOTE_START = True
REQUIRE_AUTH_FOR_CONTROLS = False
