import ccxt
import pandas as pd
import time
import logging
from core.config_manager import config

logger = logging.getLogger('BybitClient')

class BybitClient:
    def __init__(self):
        self.exchange = None
        self.conectado = False
        self.inicializar_conexao()
    
    def inicializar_conexao(self):
        """Inicializar conexão com Bybit"""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': config.BYBIT_CONFIG['api_key'],
                'secret': config.BYBIT_CONFIG['api_secret'],
                'sandbox': config.BYBIT_CONFIG['testnet'],
                'enableRateLimit': True,
            })
            
            # Testar conexão
            self.exchange.fetch_time()
            self.conectado = True
            logger.info("✅ CONEXÃO BYBIT ESTABELECIDA")
            
        except Exception as e:
            logger.error(f"❌ ERRO NA CONEXÃO BYBIT: {e}")
            self.conectado = False
    
    def verificar_conexao(self):
        """Verificar se a conexão está ativa"""
        try:
            if self.exchange:
                self.exchange.fetch_time()
                return True
        except Exception as e:
            logger.error(f"❌ CONEXÃO BYBIT PERDIDA: {e}")
            self.conectado = False
            self.inicializar_conexao()
        
        return self.conectado
    
    def obter_dados_mercado(self, simbolo: str, timeframe: str = '15m', limite: int = 100):
        """Obter dados OHLCV"""
        try:
            if not self.verificar_conexao():
                return None
            
            ohlcv = self.exchange.fetch_ohlcv(simbolo, timeframe, limit=limite)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
            
        except Exception as e:
            logger.error(f"❌ ERRO AO OBTER DADOS {simbolo}: {e}")
            return None
    
    def obter_dados_multitimeframe(self, pares: list, timeframes: list = None):
        """Obter dados multi-timeframe"""
        if timeframes is None:
            timeframes = ['5m', '15m', '1h']
        
        dados = {}
        
        for par in pares:
            try:
                dados_par = {}
                for tf in timeframes:
                    df = self.obter_dados_mercado(par, tf, 50)
                    if df is not None and len(df) > 20:
                        dados_par[tf] = df
                    else:
                        dados_par[tf] = None
                
                dados[par] = dados_par
                logger.info(f"✅ Dados {par} obtidos")
                
            except Exception as e:
                logger.error(f"❌ ERRO EM {par}: {e}")
                dados[par] = None
        
        return dados
    
    def executar_ordem(self, simbolo: str, lado: str, quantidade: float, tipo_ordem: str = 'market'):
        """Executar ordem na exchange"""
        try:
            if not self.verificar_conexao():
                logger.error("❌ SEM CONEXÃO PARA EXECUTAR ORDEM")
                return None
            
            # Calcular quantidade
            ticker = self.exchange.fetch_ticker(simbolo)
            preco_atual = ticker['last']
            qty = quantidade / preco_atual
            
            ordem = self.exchange.create_order(
                symbol=simbolo,
                type=tipo_ordem,
                side=lado,
                amount=qty,
                price=None
            )
            
            logger.info(f"✅ ORDEM EXECUTADA: {simbolo} {lado}")
            return ordem
            
        except Exception as e:
            logger.error(f"❌ ERRO NA ORDEM {simbolo} {lado}: {e}")
            return None
    
    def obter_saldo(self, moeda: str = 'USDT'):
        """Obter saldo da conta"""
        try:
            if self.verificar_conexao():
                balance = self.exchange.fetch_balance()
                if moeda in balance['total']:
                    return float(balance['total'][moeda])
            return 0.0
        except Exception as e:
            logger.error(f"❌ ERRO AO OBTER SALDO: {e}")
            return 0.0
    
    def obter_ticker(self, simbolo: str):
        """Obter informações do ticker"""
        try:
            if self.verificar_conexao():
                return self.exchange.fetch_ticker(simbolo)
            return None
        except Exception as e:
            logger.error(f"❌ ERRO AO OBTER TICKER {simbolo}: {e}")
            return None
