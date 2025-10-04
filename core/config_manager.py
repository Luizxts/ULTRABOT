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
            'risk_per_trade': 0.02,  # 2% por trade
            'max_positions': 3,
            'valor_por_trade': 100,  # USD por trade
            'max_drawdown': 0.05,    # 5% máximo
            'take_profit': 0.03,     # 3% TP
            'stop_loss': 0.015,      # 1.5% SL
        }
        
        # IA CONFIG
        self.AI_CONFIG = {
            'confidence_threshold': 0.65,
            'learning_enabled': True,
            'adaptive_parameters': True,
            'pattern_recognition': True
        }
        
        # WEB CONFIG
        self.WEB_CONFIG = {
            'port': int(os.getenv('PORT', 5000)),
            'host': '0.0.0.0',
            'debug': False
        }
    
    def get(self, section, key=None):
        if hasattr(self, section):
            config_section = getattr(self, section)
            return config_section if key is None else config_section.get(key)
        return None

config = ConfigManager()
