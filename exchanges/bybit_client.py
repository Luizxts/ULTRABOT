import ccxt
import pandas as pd
import time
import logging
from typing import Dict, List, Optional
from core.config_manager import config

logger = logging.getLogger('BybitClient')

class BybitClient:
    def __init__(self):
        self.exchange = None
        self.conectado = False
        self.ultima_conexao = None
        self.inicializar_conexao()
    
    def inicializar_conexao(self):
        """Inicializar conexão com Bybit de forma robusta"""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': config.BYBIT_CONFIG['api_key'],
                'secret': config.BYBIT_CONFIG['api_secret'],
                'sandbox': config.BYBIT_CONFIG['testnet'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True,
                    'recvWindow': 60000,
                },
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            })
            
            # Configurar URLs específicas
            if config.BYBIT_CONFIG['testnet']:
                self.exchange.urls['api'] = 'https://api-testnet.bybit.com'
            else:
                self.exchange.urls['api'] = 'https://api.bybit.com'
            
            # Testar conexão
            if self._testar_conexao():
                self.conectado = True
                self.ultima_conexao = time.time()
                logger.info("✅ CONEXÃO BYBIT ESTABELECIDA")
            else:
                logger.error("❌ FALHA NA CONEXÃO BYBIT")
                
        except Exception as e:
            logger.error(f"❌ ERRO NA INICIALIZAÇÃO BYBIT: {e}")
            self.conectado = False
    
    def _testar_conexao(self):
        """Testar conexão com métodos alternativos"""
        methods = [
            lambda: self.exchange.fetch_time(),
            lambda: self.exchange.fetch_ticker('BTC/USDT'),
            lambda: self.exchange.fetch_balance()
        ]
        
        for method in methods:
            try:
                method()
                return True
            except Exception:
                continue
        return False
    
    def verificar_conexao(self):
        """Verificar e manter conexão ativa"""
        try:
            if self.exchange and self.conectado:
                # Verificação leve
                self.exchange.fetch_time()
                return True
        except Exception as e:
            logger.warning(f"⚠️ CONEXÃO PERDIDA: {e}")
            self.conectado = False
            # Tentar reconexão
            self.inicializar_conexao()
        
        return self.conectado
    
    def obter_dados_mercado(self, simbolo: str, timeframe: str = '15m', limite: int = 100):
        """Obter dados OHLCV com tratamento de erro"""
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
    
    def obter_dados_multitimeframe(self, pares: List[str], timeframes: List[str] = None):
        """Obter dados multi-timeframe de forma eficiente"""
        if timeframes is None:
            timeframes = ['5m', '15m', '1h']
        
        dados = {}
        
        for par in pares:
            try:
                dados_par = {}
                for tf in timeframes:
                    df = self.obter_dados_mercado(par, tf, 100)
                    if df is not None and len(df) > 20:
                        dados_par[tf] = df
                    else:
                        logger.warning(f"⚠️ Dados insuficientes para {par} {tf}")
                        dados_par[tf] = None
                
                dados[par] = dados_par
                logger.info(f"✅ Dados {par} obtidos - {len([x for x in dados_par.values() if x is not None])}/{len(timeframes)} timeframes")
                
            except Exception as e:
                logger.error(f"❌ ERRO EM {par}: {e}")
                dados[par] = None
        
        return dados
    
    def executar_ordem(self, simbolo: str, lado: str, quantidade: float, tipo_ordem: str = 'market'):
        """Executar ordem com gestão de risco integrada"""
        try:
            if not self.verificar_conexao():
                logger.error("❌ SEM CONEXÃO PARA EXECUTAR ORDEM")
                return None
            
            # Obter informações do mercado
            ticker = self.exchange.fetch_ticker(simbolo)
            preco_atual = ticker['last']
            
            # Calcular quantidade precisa
            if simbolo.endswith('USDT'):
                qty = quantidade / preco_atual
            else:
                qty = quantidade
            
            # Ajustar quantidade para as regras da exchange
            mercado = self.exchange.market(simbolo)
            qty = self.exchange.amount_to_precision(simbolo, qty)
            
            logger.info(f"🎯 EXECUTANDO ORDEM: {simbolo} {lado} {qty} {tipo_ordem}")
            
            # Executar ordem
            ordem = self.exchange.create_order(
                symbol=simbolo,
                type=tipo_ordem,
                side=lado,
                amount=float(qty),
                price=None if tipo_ordem == 'market' else preco_atual,
                params={}
            )
            
            logger.info(f"✅ ORDEM EXECUTADA - ID: {ordem.get('id', 'N/A')}")
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
    
    def obter_posicoes_abertas(self):
        """Obter posições abertas"""
        try:
            if self.verificar_conexao():
                positions = self.exchange.fetch_positions()
                return [p for p in positions if p['contracts'] and float(p['contracts']) > 0]
            return []
        except Exception as e:
            logger.error(f"❌ ERRO AO OBTER POSIÇÕES: {e}")
            return []
    
    def obter_ordens_abertas(self, simbolo: str = None):
        """Obter ordens em aberto"""
        try:
            if self.verificar_conexao():
                if simbolo:
                    return self.exchange.fetch_open_orders(simbolo)
                else:
                    return self.exchange.fetch_open_orders()
            return []
        except Exception as e:
            logger.error(f"❌ ERRO AO OBTER ORDENS: {e}")
            return []
    
    def cancelar_ordem(self, id_ordem: str, simbolo: str):
        """Cancelar ordem específica"""
        try:
            if self.verificar_conexao():
                return self.exchange.cancel_order(id_ordem, simbolo)
            return None
        except Exception as e:
            logger.error(f"❌ ERRO AO CANCELAR ORDEM {id_ordem}: {e}")
            return None
    
    def obter_ticker(self, simbolo: str):
        """Obter informações do ticker"""
        try:
            if self.verificar_conexao():
                return self.exchange.fetch_ticker(simbolo)
            return None
        except Exception as e:
            logger.error(f"❌ ERRO AO OBTER TICKER {simbolo}: {e}")
            return None
