import os
from dotenv import load_dotenv

load_dotenv()

class TavaresConfig:
    def __init__(self):
        # 🤖 CONFIGURAÇÕES TELEGRAM
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8444269740:AAE2dlSXozV4cIGNMMs72APIDcrYBvIq31M')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-4977542145')
        
        # 💰 BYBIT REAL - SUAS CREDENCIAIS
        self.BYBIT_API_KEY = os.getenv('BYBIT_API_KEY_REAL')
        self.BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET_REAL')
        self.BYBIT_TESTNET = False  # 🔥 MODO REAL!
        
        # 📊 PARES MONITORADOS (BYBIT)
        self.PARES_MONITORADOS = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT',
            'DOT/USDT', 'LINK/USDT', 'AVAX/USDT', 'MATIC/USDT'
        ]
        
        # ⚡ CONFIGURAÇÕES DE TRADING REAL
        self.INTERVALO_ANALISE = 60  # segundos
        self.RISK_PER_TRADE = 0.01   # 1% por trade
        self.VALOR_POR_TRADE = 50    # $50 por operação
        self.STOP_LOSS = 0.015       # 1.5%
        self.TAKE_PROFIT = 0.03      # 3%
        self.LEVERAGE = 3            # Alavancagem conservadora
        self.CONFIANCA_MINIMA = 65   # 65% confiança mínima

config = TavaresConfig()
