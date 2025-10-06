import ccxt
import logging
import asyncio
from decimal import Decimal, ROUND_DOWN
from core.config import config

logger = logging.getLogger('ExchangeManager')

class BybitManager:
    """Gerenciador de operações reais na Bybit"""
    
    def __init__(self):
        self.exchange = ccxt.bybit({
            'apiKey': config.BYBIT_API_KEY,
            'secret': config.BYBIT_API_SECRET,
            'sandbox': config.BYBIT_TESTNET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # Ou 'future' para futuros
            }
        })
        
        # Verificar conexão
        self._verificar_conexao()
        logger.info("💰 BYBIT MANAGER INICIALIZADO - MODO REAL!")
    
    def _verificar_conexao(self):
        """Verificar conexão com Bybit"""
        try:
            balance = self.exchange.fetch_balance()
            logger.info(f"✅ Conectado à Bybit - Saldo: {balance['total'].get('USDT', 0)} USDT")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Bybit: {e}")
            raise
    
    def _calcular_quantidade(self, par, valor_usdt):
        """Calcular quantidade baseada no preço atual e valor em USDT"""
        try:
            # Obter preço atual
            ticker = self.exchange.fetch_ticker(par)
            preco_atual = ticker['last']
            
            # Calcular quantidade
            quantidade = valor_usdt / preco_atual
            
            # Obter informações do mercado para precisão
            mercado = self.exchange.load_markets()
            symbol_info = mercado[par]
            precision = symbol_info['precision']['amount']
            
            # Arredondar para a precisão correta
            quantidade = float(Decimal(str(quantidade)).quantize(
                Decimal(str(precision)), rounding=ROUND_DOWN
            ))
            
            return quantidade
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular quantidade: {e}")
            return None
    
    async def executar_ordem(self, par, direcao, valor_usdt):
        """Executar ordem REAL na Bybit"""
        try:
            # Calcular quantidade
            quantidade = self._calcular_quantidade(par, valor_usdt)
            if not quantidade:
                return None
            
            logger.info(f"💰 EXECUTANDO ORDEM REAL: {par} {direcao} {quantidade}")
            
            # Executar ordem de mercado
            if direcao.upper() == 'BUY':
                ordem = self.exchange.create_market_buy_order(par, quantidade)
            else:  # SELL
                ordem = self.exchange.create_market_sell_order(par, quantidade)
            
            logger.info(f"✅ ORDEM EXECUTADA: {ordem['id']} - Preço: {ordem['price']}")
            
            return {
                'id': ordem['id'],
                'symbol': ordem['symbol'],
                'side': ordem['side'],
                'price': ordem['price'],
                'amount': ordem['amount'],
                'cost': ordem['cost'],
                'timestamp': ordem['timestamp'],
                'status': ordem['status']
            }
            
        except Exception as e:
            logger.error(f"❌ ERRO EXECUTANDO ORDEM REAL: {e}")
            return None
    
    def obter_saldo(self):
        """Obter saldo atual"""
        try:
            balance = self.exchange.fetch_balance()
            return balance['total'].get('USDT', 0)
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo: {e}")
            return 0
    
    def obter_preco_atual(self, par):
        """Obter preço atual do par"""
        try:
            ticker = self.exchange.fetch_ticker(par)
            return ticker['last']
        except Exception as e:
            logger.error(f"❌ Erro ao obter preço: {e}")
            return None
    
    def obter_ordens_abertas(self):
        """Obter ordens abertas"""
        try:
            ordens = self.exchange.fetch_open_orders()
            return ordens
        except Exception as e:
            logger.error(f"❌ Erro ao obter ordens abertas: {e}")
            return []
