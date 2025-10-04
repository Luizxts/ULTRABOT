import ccxt
import pandas as pd
import time
import logging
from config import BYBIT_CONFIG

logger = logging.getLogger('BybitConnector')

class BybitConnector:
    def __init__(self):
        self.exchange = None
        self.conectado = False
        self.inicializar_conexao()
    
    def inicializar_conexao(self):
        """Inicializar conexão com Bybit"""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': BYBIT_CONFIG['api_key'],
                'secret': BYBIT_CONFIG['api_secret'],
                'sandbox': BYBIT_CONFIG['testnet'],
                'enableRateLimit': True,
            })
            
            # Testar conexão
            self.exchange.fetch_balance()
            self.conectado = True
            logger.info("✅ CONEXÃO BYBIT ESTABELECIDA")
            
        except Exception as e:
            logger.error(f"❌ ERRO NA CONEXÃO BYBIT: {e}")
            self.conectado = False
    
    def verificar_conexao(self):
        """Verificar se a conexão está ativa"""
        try:
            if self.exchange:
                self.exchange.fetch_balance()
                self.conectado = True
                return True
        except Exception as e:
            logger.error(f"❌ CONEXÃO BYBIT PERDIDA: {e}")
            self.conectado = False
            # Tentar reconectar
            self.inicializar_conexao()
        
        return self.conectado
    
    def obter_dados_multitimeframe(self, pares, timeframes=['5m', '15m', '1h']):
        """Obter dados OHLCV multi-timeframe"""
        dados = {}
        
        for par in pares:
            try:
                dados_par = {}
                for tf in timeframes:
                    ohlcv = self.exchange.fetch_ohlcv(par, tf, limit=100)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    dados_par[tf] = df
                
                dados[par] = dados_par
                logger.info(f"✅ Dados {par} obtidos - {len(dados_par)} timeframes")
                
            except Exception as e:
                logger.error(f"❌ Erro ao obter dados {par}: {e}")
                dados[par] = None
        
        return dados
    
    def executar_ordem(self, simbolo, lado, quantidade, tipo_ordem='market'):
        """Executar ordem na exchange"""
        try:
            if not self.verificar_conexao():
                logger.error("❌ Sem conexão para executar ordem")
                return None
            
            # Calcular quantidade baseada no preço atual
            ticker = self.exchange.fetch_ticker(simbolo)
            preco_atual = ticker['last']
            qty = quantidade / preco_atual
            
            ordem = self.exchange.create_order(
                symbol=simbolo,
                type=tipo_ordem,
                side=lado,
                amount=qty,
                price=None if tipo_ordem == 'market' else preco_atual
            )
            
            logger.info(f"✅ ORDEM EXECUTADA: {simbolo} {lado} {qty:.6f}")
            return ordem
            
        except Exception as e:
            logger.error(f"❌ ERRO AO EXECUTAR ORDEM: {e}")
            return None
    
    def obter_saldo_conta(self):
        """Obter saldo da conta em USDT"""
        try:
            if self.verificar_conexao():
                balance = self.exchange.fetch_balance()
                if 'USDT' in balance['total']:
                    return float(balance['total']['USDT'])
            return 0.0
        except Exception as e:
            logger.error(f"❌ ERRO AO OBTER SALDO: {e}")
            return 0.0
    
    def obter_posicoes_abertas(self):
        """Obter posições abertas"""
        try:
            if self.verificar_conexao():
                positions = self.exchange.fetch_positions()
                return [p for p in positions if p['contracts'] > 0]
            return []
        except Exception as e:
            logger.error(f"❌ ERRO AO OBTER POSIÇÕES: {e}")
            return []
