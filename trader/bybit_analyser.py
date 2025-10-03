import logging
from pybit import usdt_perpetual

class BybitAnalyser:
    def __init__(self, testnet=True):
        self.logger = logging.getLogger(__name__)
        self.testnet = testnet
        self.session = None
        
    def initialize_session(self, api_key, api_secret):
        """Inicializa sessão com Bybit"""
        try:
            self.session = usdt_perpetual.HTTP(
                endpoint="https://api-testnet.bybit.com" if self.testnet else "https://api.bybit.com",
                api_key=api_key,
                api_secret=api_secret
            )
            
            if self.testnet:
                self.logger.warning("🎮 MODO SIMULADO ATIVADO")
            else:
                self.logger.info("💰 MODO REAL ATIVADO")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar com Bybit: {e}")
    
    def get_balance(self):
        """Obtém saldo da conta"""
        try:
            if self.session:
                wallet = self.session.get_wallet_balance(coin="USDT")
                return float(wallet['result']['USDT']['available_balance'])
            return 1000.00  # Saldo padrão para modo simulado
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter saldo: {e}")
            return 1000.00
    
    def get_market_data(self, symbol="BTCUSDT"):
        """Obtém dados de mercado"""
        try:
            if self.session:
                ticker = self.session.latest_information_for_symbol(symbol=symbol)
                return ticker['result'][0]
            return {'last_price': '50000', 'price_24h_pcnt': '0.02'}
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter dados: {e}")
            return {'last_price': '50000', 'price_24h_pcnt': '0.02'}
