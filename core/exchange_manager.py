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
                'defaultType': 'spot',
            }
        })
        
        # Verificar conexão
        self._verificar_conexao()
        logger.info("💰 BYBIT MANAGER INICIALIZADO - MODO REAL!")
    
    def _verificar_conexao(self):
        """Verificar conexão com Bybit"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['total'].get('USDT', 0)
            logger.info(f"✅ Conectado à Bybit - Saldo: {usdt_balance} USDT")
            
            if usdt_balance < config.VALOR_POR_TRADE:
                logger.warning(f"⚠️ Saldo insuficiente: {usdt_balance} USDT < {config.VALOR_POR_TRADE} USDT")
            
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
            
            if preco_atual == 0:
                logger.error(f"❌ Preço zero para {par}")
                return None
            
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
            
            # Verificar quantidade mínima
            min_amount = symbol_info['limits']['amount']['min']
            if quantidade < min_amount:
                logger.warning(f"⚠️ Quantidade muito pequena: {quantidade} < {min_amount}")
                quantidade = min_amount
            
            logger.info(f"📊 {par}: Preço={preco_atual}, Qtd={quantidade}")
            return quantidade
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular quantidade para {par}: {e}")
            return None
    
    async def executar_ordem(self, par, direcao, valor_usdt):
        """Executar ordem REAL na Bybit"""
        try:
            # Calcular quantidade
            quantidade = self._calcular_quantidade(par, valor_usdt)
            if not quantidade:
                logger.error(f"❌ Não foi possível calcular quantidade para {par}")
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
                'price': float(ordem['price']),
                'amount': float(ordem['amount']),
                'cost': float(ordem['cost']),
                'timestamp': ordem['timestamp'],
                'status': ordem['status']
            }
            
        except Exception as e:
            logger.error(f"❌ ERRO EXECUTANDO ORDEM REAL {par}: {e}")
            return None
    
    def obter_saldo(self):
        """Obter saldo atual"""
        try:
            balance = self.exchange.fetch_balance()
            return float(balance['total'].get('USDT', 0))
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo: {e}")
            return 0
    
    def obter_preco_atual(self, par):
        """Obter preço atual do par"""
        try:
            ticker = self.exchange.fetch_ticker(par)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"❌ Erro ao obter preço {par}: {e}")
            return None
    
    def obter_dados_mercado(self, par, timeframe='15m', limit=100):
        """Obter dados OHLCV do mercado"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(par, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados {par}: {e}")
            return None
