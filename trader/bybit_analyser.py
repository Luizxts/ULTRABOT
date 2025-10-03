import logging
import random
import os

class BybitAnalyser:
    def __init__(self, testnet=True):
        self.logger = logging.getLogger(__name__)
        self.testnet = testnet
        self.session = None
        self.api_key = os.getenv('BYBIT_API_KEY', '')
        self.api_secret = os.getenv('BYBIT_API_SECRET', '')
        
    def initialize_session(self):
        """Inicializa sessão com Bybit (real ou simulada)"""
        try:
            # ✅ VERIFICA SE TEM CREDENCIAIS PARA MODO REAL
            if not self.api_key or not self.api_secret:
                self.logger.warning("🎮 MODO SIMULADO ATIVADO (sem credenciais API)")
                return False
                
            # ✅ TENTA CONEXÃO REAL COM BYBIT (versão compatível)
            try:
                from pybit import HTTP
                
                self.session = HTTP(
                    endpoint="https://api-testnet.bybit.com" if self.testnet else "https://api.bybit.com",
                    api_key=self.api_key,
                    api_secret=self.api_secret
                )
                
                # Testa a conexão
                balance = self.get_balance_real()
                self.logger.info(f"💰 MODO REAL ATIVADO - Saldo: ${balance}")
                return True
                
            except ImportError:
                self.logger.warning("📚 Biblioteca pybit não disponível - Modo Simulado")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar com Bybit: {e}")
            self.logger.warning("🔄 Modo simulado ativado devido ao erro")
            return False
    
    def get_balance_real(self):
        """Obtém saldo real da Bybit"""
        try:
            if self.session:
                wallet = self.session.get_wallet_balance(coin="USDT")
                return float(wallet['result']['USDT']['available_balance'])
            return 0.0
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter saldo real: {e}")
            return 0.0
    
    def get_balance(self):
        """Obtém saldo (real ou simulado)"""
        try:
            if self.session and self.api_key and self.api_secret:
                return self.get_balance_real()
            else:
                return 1000.00  # Saldo simulado
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter saldo: {e}")
            return 1000.00
    
    def get_market_data(self, symbol="BTCUSDT"):
        """Obtém dados de mercado (real ou simulados)"""
        try:
            if self.session and self.api_key and self.api_secret:
                # Dados reais da Bybit
                ticker = self.session.latest_information_for_symbol(symbol=symbol)
                return ticker['result'][0]
            else:
                # Dados simulados
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
