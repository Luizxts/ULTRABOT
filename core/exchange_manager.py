import ccxt
import logging
import asyncio
from decimal import Decimal, ROUND_DOWN
from core.config import config

logger = logging.getLogger('ExchangeManager')

class BybitManager:
    """Gerenciador de operações reais na Bybit - MODO REAL DIRETO"""
    
    def __init__(self):
        # 🔥 CONFIGURAÇÃO BYBIT REAL
        self.exchange = ccxt.bybit({
            'apiKey': config.BYBIT_API_KEY,
            'secret': config.BYBIT_API_SECRET,
            'sandbox': config.BYBIT_TESTNET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
            }
        })
        
        # 🔥 VERIFICAÇÃO FORÇADA - EXIGE CONEXÃO REAL
        self._verificar_conexao_real()
        logger.info("💰 BYBIT MANAGER INICIALIZADO - MODO REAL!")
    
    def _verificar_conexao_real(self):
        """Verificação REAL - para conexão direta"""
        try:
            # Tentar múltiplos endpoints
            endpoints = [
                self.exchange.fetch_balance,
                lambda: self.exchange.fetch_ticker('BTC/USDT'),
                self.exchange.load_markets
            ]
            
            for endpoint in endpoints:
                try:
                    result = endpoint()
                    logger.info(f"✅ Endpoint {endpoint.__name__} funcionando")
                    break
                except Exception as e:
                    continue
            else:
                raise Exception("Todos os endpoints falharam")
                
            # Verificar saldo REAL
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['total'].get('USDT', 0)
            logger.info(f"💰 SALDO BYBIT REAL: {usdt_balance} USDT")
            
            if usdt_balance < config.VALOR_POR_TRADE:
                logger.warning(f"⚠️ Saldo insuficiente para trading: {usdt_balance} USDT")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ FALHA CRÍTICA: Não foi possível conectar à Bybit Real")
            logger.error(f"❌ Erro: {e}")
            raise Exception(f"FALHA NA CONEXÃO BYBIT REAL: {e}")
    
    def _calcular_quantidade(self, par, valor_usdt):
        """Calcular quantidade baseada no preço atual"""
        try:
            # Obter preço atual
            ticker = self.exchange.fetch_ticker(par)
            preco_atual = ticker['last']
            
            if preco_atual == 0:
                raise Exception(f"Preço zero para {par}")
            
            # Calcular quantidade
            quantidade = valor_usdt / preco_atual
            
            # Obter informações do mercado
            mercado = self.exchange.load_markets()
            symbol_info = mercado[par]
            precision = symbol_info['precision']['amount']
            
            # Arredondar para precisão correta
            quantidade = float(Decimal(str(quantidade)).quantize(
                Decimal(str(precision)), rounding=ROUND_DOWN
            ))
            
            # Verificar quantidade mínima
            min_amount = symbol_info['limits']['amount']['min']
            if quantidade < min_amount:
                quantidade = min_amount
                logger.warning(f"⚠️ Ajustada quantidade mínima: {quantidade}")
            
            logger.info(f"📊 {par}: Preço=${preco_atual}, Qtd={quantidade}")
            return quantidade
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular quantidade {par}: {e}")
            raise
    
    async def executar_ordem(self, par, direcao, valor_usdt):
        """Executar ordem REAL na Bybit"""
        try:
            logger.info(f"💰 EXECUTANDO ORDEM REAL: {par} {direcao} ${valor_usdt}")
            
            # Calcular quantidade
            quantidade = self._calcular_quantidade(par, valor_usdt)
            
            # Verificar saldo antes de executar
            saldo_atual = self.obter_saldo()
            if saldo_atual < valor_usdt:
                raise Exception(f"Saldo insuficiente: {saldo_atual} < {valor_usdt}")
            
            # Executar ordem de mercado
            if direcao.upper() == 'BUY':
                ordem = self.exchange.create_market_buy_order(par, quantidade)
            else:  # SELL
                ordem = self.exchange.create_market_sell_order(par, quantidade)
            
            logger.info(f"✅ ORDEM REAL EXECUTADA: {ordem['id']} - Preço: {ordem['price']}")
            
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
            raise
    
    def obter_saldo(self):
        """Obter saldo atual REAL"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = float(balance['total'].get('USDT', 0))
            logger.info(f"💰 Saldo atual: {usdt_balance} USDT")
            return usdt_balance
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo: {e}")
            raise
    
    def obter_preco_atual(self, par):
        """Obter preço atual do par"""
        try:
            ticker = self.exchange.fetch_ticker(par)
            preco = float(ticker['last'])
            logger.info(f"📈 {par}: ${preco}")
            return preco
        except Exception as e:
            logger.error(f"❌ Erro ao obter preço {par}: {e}")
            raise
    
    def obter_dados_mercado(self, par, timeframe='15m', limit=100):
        """Obter dados OHLCV do mercado REAL"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(par, timeframe, limit=limit)
            if not ohlcv:
                raise Exception(f"Dados vazios para {par}")
            return ohlcv
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados {par}: {e}")
            raise
