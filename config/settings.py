import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys - BYBIT
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', 'Ee4HkruMw2Oha2ohUO')
    BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', 'Fps1f8uxdCwXO8xTFX0aZBx2xZ222yTONHpY')
    BYBIT_TESTNET = os.getenv('BYBIT_TESTNET', 'false').lower() == 'true'
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8444269740:AAE2dlSXozV4cIGNMMs72APIDcrYBvIq31M')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-4977542145')
    
    # Trading Settings
    DEFAULT_LEVERAGE = 10
    MAX_LEVERAGE = 25
    RISK_PER_TRADE = 0.02
    DAILY_PROFIT_TARGET = 0.05
    MAX_DRAWDOWN = 0.10
    
    # Strategy Settings
    AGGRESSIVE_MULTIPLIER = 2.0
    CONSERVATIVE_MULTIPLIER = 0.7
    
    # Technical Analysis
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    
    # Trading Pairs
    TRADING_PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
    
    @classmethod
    def get_bybit_config(cls):
        return {
            "api_key": cls.BYBIT_API_KEY,
            "api_secret": cls.BYBIT_API_SECRET,
            "testnet": cls.BYBIT_TESTNET
        }
    
    @classmethod 
    def validate_config(cls):
        issues = []
        if cls.BYBIT_API_KEY in ["XXXXXXX", "SUA_CHAVE_REAL_AQUI", "Ee4HkruMw2Oha2ohUO"]:
            issues.append("⚠️ Chave Bybit não configurada - Modo Simulado")
        return issues
