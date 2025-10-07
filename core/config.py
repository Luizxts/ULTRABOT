import os
from dotenv import load_dotenv

load_dotenv()

class TavaresConfig:
    def __init__(self):
        # 🤖 CONFIGURAÇÕES TELEGRAM
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
        
        # 💰 BYBIT REAL - TESTES SEGUROS
        self.BYBIT_API_KEY = os.getenv('BYBIT_API_KEY_REAL')
        self.BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET_REAL')
        self.BYBIT_TESTNET = False  # 🔥 MODO REAL MAS CONSERVADOR
        
        # 📊 PARES MONITORADOS (CRIPTOBARATAS)
        self.PARES_MONITORADOS = [
            'XRP/USDT',    # ~R$ 2.50
            'ADA/USDT',    # ~R$ 2.00  
            'MATIC/USDT',  # ~R$ 3.75
            'DOGE/USDT',   # ~R$ 0.80
            'SHIB/USDT'    # ~R$ 0.0001
        ]
        
        # ⚡ CONFIGURAÇÕES SUPER CONSERVADORAS - R$100
        self.INTERVALO_ANALISE = 120  # 2 minutos entre análises
        self.RISK_PER_TRADE = 0.005   # 0.5% por trade (R$ 0.50)
        self.VALOR_POR_TRADE = 10     # $10 USD por operação (R$ 50)
        self.STOP_LOSS = 0.02         # 2% stop loss
        self.TAKE_PROFIT = 0.05       # 5% take profit  
        self.LEVERAGE = 1             # SEM alavancagem
        self.CONFIANCA_MINIMA = 75    # 75% confiança mínima

config = TavaresConfig()
