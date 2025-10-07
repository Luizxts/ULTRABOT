import os
from dotenv import load_dotenv

load_dotenv()

class TavaresConfig:
    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
        self.MODO_ANALISE = True
        self.PARES_MONITORADOS = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT',
            'DOT/USDT', 'LINK/USDT', 'AVAX/USDT', 'MATIC/USDT'
        ]
        self.INTERVALO_ANALISE = 60
        self.CONFIANCA_MINIMA = 65

config = TavaresConfig()
