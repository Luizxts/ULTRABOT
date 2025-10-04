import os
import json
from dotenv import load_dotenv

load_dotenv()

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        # BYBIT CONFIG
        self.BYBIT_CONFIG = {
            'api_key': os.getenv('BYBIT_API_KEY_REAL'),
            'api_secret': os.getenv('BYBIT_API_SECRET_REAL'),
            'testnet': os.getenv('BYBIT_TESTNET', 'false').lower() == 'true'
        }
        
        # TELEGRAM CONFIG
        self.TELEGRAM_CONFIG = {
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID')
        }
        
        # TRADING CONFIG
        self.TRADING_CONFIG = {
            'pares_monitorados': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT'],
            'intervalo_analise': 30,
            'risk_per_trade': 0.02,
            'max_positions': 3,
            'valor_por_trade': 100,
            'max_drawdown': 0.05,
            'take_profit': 0.03,
            'stop_loss': 0.015,
        }
        
        # IA CONFIG
        self.AI_CONFIG = {
            'confidence_threshold': 0.65,
            'learning_enabled': True,
            'adaptive_parameters': True
        }
        
        # WEB CONFIG
        self.WEB_CONFIG = {
            'port': int(os.getenv('PORT', 5000)),
            'host': '0.0.0.0',
            'debug': False
        }

config = ConfigManager()
