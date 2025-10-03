import logging
import random

class BybitAnalyser:
    def __init__(self, testnet=True):
        self.logger = logging.getLogger(__name__)
        self.testnet = testnet
        self.session = None
        
    def initialize_session(self, api_key, api_secret):
        """Inicializa sessão com Bybit (simulada)"""
        try:
            if self.testnet:
                self.logger.warning("🎮 MODO SIMULADO ATIVADO")
            else:
                self.logger.info("💰 MODO REAL ATIVADO - Conexão Bybit simulada")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar com Bybit: {e}")
    
    def get_balance(self):
        """Obtém saldo da conta (simulado)"""
        try:
            if self.testnet:
                return 1000.00  # Saldo simulado
            else:
                return 18.34   # Saldo real simulado
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter saldo: {e}")
            return 1000.00
    
    def get_market_data(self, symbol="BTCUSDT"):
        """Obtém dados de mercado (simulado)"""
        try:
            # Dados simulados para teste
            return {
                'last_price': str(random.randint(25000, 50000)),
                'price_24h_pcnt': str(random.uniform(-0.05, 0.05)),
                'volume_24h': str(random.randint(1000000, 50000000)),
                'high_price_24h': str(random.randint(45000, 52000)),
                'low_price_24h': str(random.randint(24000, 30000))
            }
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter dados: {e}")
            return {
                'last_price': '42000',
                'price_24h_pcnt': '0.02',
                'volume_24h': '25000000'
            }
