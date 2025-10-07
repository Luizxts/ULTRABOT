import ccxt
import logging
import asyncio
import time
import numpy as np
from decimal import Decimal, ROUND_DOWN
from core.config import config

logger = logging.getLogger('ExchangeManager')

class BybitManager:
    """Gerenciador Bybit completo e resiliente para Railway"""
    
    def __init__(self):
        # 🔥 CONFIGURAÇÃO BYBIT OTIMIZADA
        self.exchange = ccxt.bybit({
            'apiKey': config.BYBIT_API_KEY,
            'secret': config.BYBIT_API_SECRET,
            'sandbox': config.BYBIT_TESTNET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
                'defaultMarginMode': 'cross',
            },
            'urls': {
                'api': {
                    'public': 'https://api.bybit.com',
                    'private': 'https://api.bybit.com',
                }
            }
        })
        
        self.modo_offline = False
        self.ultima_tentativa_conexao = 0
        self.reconexao_agendada = False
        
        # Verificar conexão
        self._verificar_conexao_inteligente()
        logger.info(f"💰 BYBIT MANAGER INICIALIZADO - Modo: {'ONLINE' if not self.modo_offline else 'OFFLINE'}")
    
    def _verificar_conexao_inteligente(self):
        """Verificação inteligente com múltiplas estratégias"""
        # Evitar verificação muito frequente
        if time.time() - self.ultima_tentativa_conexao < 300:  # 5 minutos
            return
        
        self.ultima_tentativa_conexao = time.time()
        
        # 🎯 ESTRATÉGIAS DE CONEXÃO
        estrategias = [
            self._testar_endpoint_basico,
            self._testar_ticker_simples,
            self._testar_load_markets,
        ]
        
        for estrategia in estrategias:
            try:
                if estrategia():
                    logger.info("✅ BYBIT CONECTADO COM SUCESSO!")
                    self.modo_offline = False
                    
                    # Tentar obter saldo real
                    try:
                        saldo = self.obter_saldo_real()
                        logger.info(f"💰 Saldo Bybit real: {saldo} USDT")
                    except:
                        pass
                    
                    return
            except Exception as e:
                logger.debug(f"❌ Estratégia falhou: {e}")
                continue
        
        # 🔄 SE TODAS FALHAREM, MODO OFFLINE
        logger.warning("🚫 BYBIT OFFLINE - Railway está bloqueado")
        self.modo_offline = True
        
        # Agendar reconexão automática
        if not self.reconexao_agendada:
            self.reconexao_agendada = True
            asyncio.create_task(self._reconexao_automatica())
    
    def _testar_endpoint_basico(self):
        """Testar endpoint mais básico"""
        try:
            markets = self.exchange.load_markets()
            return len(markets) > 0
        except:
            return False
    
    def _testar_ticker_simples(self):
        """Testar com ticker simples"""
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker and 'last' in ticker and ticker['last'] > 0
        except:
            return False
    
    def _testar_load_markets(self):
        """Testar carregamento de mercados"""
        try:
            self.exchange.load_markets()
            return True
        except:
            return False
    
    async def _reconexao_automatica(self):
        """Reconexão automática a cada 10 minutos"""
        while self.modo_offline:
            await asyncio.sleep(600)  # 10 minutos
            
            logger.info("🔄 Tentando reconexão automática com Bybit...")
            self._verificar_conexao_inteligente()
            
            if not self.modo_offline:
                logger.info("🎉 BYBIT RECONECTADO AUTOMATICAMENTE!")
                break
    
    def obter_saldo_real(self):
        """Obter saldo real da Bybit"""
        if self.modo_offline:
            return 100.0  # Saldo simulado
        
        try:
            balance = self.exchange.fetch_balance()
            return float(balance['total'].get('USDT', 0))
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo real: {e}")
            return 0.0
    
    def obter_saldo(self):
        """Obter saldo (com fallback)"""
        try:
            return self.obter_saldo_real()
        except:
            return 100.0  # Fallback para modo offline
    
    def obter_dados_mercado(self, par, timeframe='15m', limit=100):
        """Obter dados OHLCV do mercado"""
        if self.modo_offline:
            return self._dados_simulados_realistas(par, limit)
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(par, timeframe, limit=limit)
            if ohlcv and len(ohlcv) > 0:
                logger.debug(f"✅ Dados reais obtidos: {par}")
                return ohlcv
            else:
                raise Exception("Dados vazios")
        except Exception as e:
            logger.warning(f"⚠️ Erro dados reais {par}, usando simulados: {e}")
            return self._dados_simulados_realistas(par, limit)
    
    def _dados_simulados_realistas(self, par, limit):
        """Gerar dados simulados realistas baseados no par"""
        current_time = int(time.time() * 1000)
        data = []
        
        # Preços base realistas por par
        precios_base = {
            'BTC/USDT': np.random.uniform(45000, 55000),
            'ETH/USDT': np.random.uniform(2500, 3500),
            'SOL/USDT': np.random.uniform(100, 200),
            'XRP/USDT': np.random.uniform(0.4, 0.6),
            'ADA/USDT': np.random.uniform(0.3, 0.5),
            'DOT/USDT': np.random.uniform(5, 8),
            'LINK/USDT': np.random.uniform(12, 18),
            'AVAX/USDT': np.random.uniform(25, 35),
            'MATIC/USDT': np.random.uniform(0.6, 0.9)
        }
        
        base_price = precios_base.get(par, 100)
        volatilidade = 0.01  # 1% de volatilidade
        
        for i in range(limit):
            timestamp = current_time - (limit - i) * 900000  # 15min intervals
            
            # Movimento de preço mais realista
            if i == 0:
                open_price = base_price
            else:
                price_change = np.random.normal(0, volatilidade)
                open_price = data[i-1][4] * (1 + price_change)  # Close anterior
            
            high_price = open_price * (1 + abs(np.random.normal(0, volatilidade/2)))
            low_price = open_price * (1 - abs(np.random.normal(0, volatilidade/2)))
            close_price = np.random.uniform(low_price, high_price)
            
            # Volume proporcional ao preço
            volume = np.random.uniform(1000, 50000) * (base_price / 1000)
            
            data.append([timestamp, open_price, high_price, low_price, close_price, volume])
        
        return data
    
    def obter_preco_atual(self, par):
        """Obter preço atual do par"""
        if self.modo_offline:
            # Preços simulados realistas
            precios_simulados = {
                'BTC/USDT': 50000,
                'ETH/USDT': 3000,
                'SOL/USDT': 150,
                'XRP/USDT': 0.5,
                'ADA/USDT': 0.4,
                'DOT/USDT': 6.5,
                'LINK/USDT': 15,
                'AVAX/USDT': 30,
                'MATIC/USDT': 0.75
            }
            return precios_simulados.get(par, 100)
        
        try:
            ticker = self.exchange.fetch_ticker(par)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"❌ Erro ao obter preço {par}: {e}")
            return 100.0
    
    def _calcular_quantidade(self, par, valor_usdt):
        """Calcular quantidade para ordem"""
        preco_atual = self.obter_preco_atual(par)
        
        if preco_atual == 0:
            raise Exception(f"Preço zero para {par}")
        
        quantidade = valor_usdt / preco_atual
        
        # Precisão baseada no par
        precisions = {
            'BTC/USDT': 6,
            'ETH/USDT': 5,
            'SOL/USDT': 3,
            'XRP/USDT': 1,
            'ADA/USDT': 1,
            'DOT/USDT': 3,
            'LINK/USDT': 3,
            'AVAX/USDT': 3,
            'MATIC/USDT': 1
        }
        
        precision = precisions.get(par, 6)
        quantidade = round(quantidade, precision)
        
        logger.info(f"📊 {par}: Preço=${preco_atual:.2f}, Qtd={quantidade}")
        return quantidade
    
    async def executar_ordem(self, par, direcao, valor_usdt):
        """Executar ordem na Bybit"""
        if self.modo_offline:
            error_msg = f"🚫 BYBIT OFFLINE - Ordem cancelada: {par} {direcao}"
            logger.error(error_msg)
            raise Exception(error_msg + "\n💡 Configure VPS para operação real")
        
        try:
            logger.info(f"💰 EXECUTANDO ORDEM REAL: {par} {direcao} ${valor_usdt}")
            
            # Verificar saldo primeiro
            saldo_atual = self.obter_saldo_real()
            if saldo_atual < valor_usdt:
                raise Exception(f"Saldo insuficiente: ${saldo_atual:.2f} < ${valor_usdt}")
            
            # Calcular quantidade
            quantidade = self._calcular_quantidade(par, valor_usdt)
            
            # Executar ordem
            if direcao.upper() == 'BUY':
                ordem = self.exchange.create_market_buy_order(par, quantidade)
            else:
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
    
    def get_status(self):
        """Obter status da conexão"""
        return {
            'modo': 'ONLINE' if not self.modo_offline else 'OFFLINE',
            'ultima_tentativa': self.ultima_tentativa_conexao,
            'reconexao_agendada': self.reconexao_agendada
        }
