# bybit_integration.py - CONEXÃO AVANÇADA COM BYBIT
import ccxt
import pandas as pd
import numpy as np
import time
import logging
import hmac
import hashlib
import json
from datetime import datetime, timedelta
import requests
from config import BYBIT_CONFIG, LOG_CONFIG

class BybitAdvancedIntegration:
    """
    Classe avançada para integração com Bybit API
    Inclui gerenciamento de ordens, análise de mercado e métricas
    """
    
    def __init__(self):
        self.config = BYBIT_CONFIG
        self.logger = self.setup_logger()
        self.exchange = None
        self.setup_exchange()
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = 0.2  # 200ms entre requests
        
    def setup_logger(self):
        """Configura logger avançado"""
        logger = logging.getLogger('BybitAdvanced')
        if LOG_CONFIG['log_colors']:
            formatter = logging.Formatter('\033[94m%(asctime)s\033[0m \033[96m%(levelname)s\033[0m \033[92m%(message)s\033[0m')
        else:
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
        
        return logger

    def setup_exchange(self):
        """Configuração completa da exchange Bybit"""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': self.config['api_key'],
                'secret': self.config['api_secret'],
                'sandbox': self.config['testnet'],
                'enableRateLimit': True,
                'rateLimit': 100,
                'options': {
                    'defaultType': 'linear',
                    'adjustForTimeDifference': True,
                    'recvWindow': 10000,
                },
                'verbose': False
            })
            
            # Testar conexão
            server_time = self.exchange.fetch_time()
            self.logger.info(f"🚀 BYBIT ADVANCED CONECTADO - Server Time: {datetime.fromtimestamp(server_time/1000)}")
            
            # Carregar mercados
            self.exchange.load_markets()
            self.logger.info("✅ MERCADOS CARREGADOS COM SUCESSO")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA CONEXÃO BYBIT: {e}")
            raise

    def rate_limit(self):
        """Controla rate limiting entre requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def get_account_balance_detailed(self):
        """Obtém saldo detalhado da conta"""
        self.rate_limit()
        try:
            balance = self.exchange.fetch_balance()
            
            balance_info = {
                'total': {
                    'USDT': balance.get('total', {}).get('USDT', 0),
                    'BTC': balance.get('total', {}).get('BTC', 0),
                },
                'free': {
                    'USDT': balance.get('free', {}).get('USDT', 0),
                    'BTC': balance.get('free', {}).get('BTC', 0),
                },
                'used': {
                    'USDT': balance.get('used', {}).get('USDT', 0),
                    'BTC': balance.get('used', {}).get('BTC', 0),
                },
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"💰 BALANÇO: USDT Total: ${balance_info['total']['USDT']:.2f} | Livre: ${balance_info['free']['USDT']:.2f}")
            return balance_info
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER BALANÇO: {e}")
            return None

    def get_advanced_ticker(self, symbol=None):
        """Obtém dados avançados do ticker"""
        self.rate_limit()
        try:
            if not symbol:
                symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            
            ticker = self.exchange.fetch_ticker(symbol)
            orderbook = self.exchange.fetch_order_book(symbol, limit=10)
            
            # Calcular spread e profundidade
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else ticker['bid']
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else ticker['ask']
            spread = (best_ask - best_bid) / best_bid * 100
            
            ticker_info = {
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['baseVolume'],
                'quote_volume': ticker['quoteVolume'],
                'change_24h': ticker['percentage'],
                'spread': spread,
                'bid_depth': sum([bid[1] for bid in orderbook['bids'][:5]]),
                'ask_depth': sum([ask[1] for ask in orderbook['asks'][:5]]),
                'timestamp': ticker['timestamp']
            }
            
            return ticker_info
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER TICKER: {e}")
            return None

    def get_ohlcv_data(self, symbol=None, timeframe='5m', limit=100):
        """Obtém dados OHLCV para análise técnica"""
        self.rate_limit()
        try:
            if not symbol:
                symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Adicionar timezone info
            df.index = df.index.tz_localize('UTC')
            
            self.logger.info(f"📊 OHLCV CARREGADO: {len(df)} candles | TF: {timeframe}")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER OHLCV: {e}")
            return None

    def get_multiple_timeframes_data(self, symbol=None, timeframes=None):
        """Obtém dados de múltiplos timeframes"""
        if timeframes is None:
            timeframes = ['1m', '5m', '15m', '1h', '4h']
        
        multi_tf_data = {}
        
        for tf in timeframes:
            data = self.get_ohlcv_data(symbol, tf)
            if data is not None:
                multi_tf_data[tf] = data
            else:
                self.logger.warning(f"⚠️ NÃO FOI POSSÍVEL OBTER DADOS DO TIMEFRAME: {tf}")
        
        self.logger.info(f"✅ DADOS MULTI-TIMEFRAME CARREGADOS: {len(multi_tf_data)} timeframes")
        return multi_tf_data

    def calculate_position_size(self, balance=None, risk_per_trade=None, stop_loss_pct=0.02):
        """Calcula tamanho avançado da posição"""
        try:
            if balance is None:
                balance_info = self.get_account_balance_detailed()
                balance = balance_info['free']['USDT'] if balance_info else self.config['initial_balance']
            
            if risk_per_trade is None:
                risk_per_trade = self.config['risk_per_trade']
            
            # Obter preço atual
            ticker = self.get_advanced_ticker()
            if not ticker:
                return 0.001
            
            current_price = ticker['last']
            
            # Calcular tamanho baseado no risco
            risk_amount = balance * risk_per_trade
            risk_per_unit = current_price * stop_loss_pct
            position_size = risk_amount / risk_per_unit
            
            # Aplicar limites
            max_size = self.config.get('max_position_size', 0.1)
            position_size = min(position_size, max_size)
            
            # Tamanho mínimo
            min_size = 0.001
            position_size = max(position_size, min_size)
            
            self.logger.info(f"📏 POSIÇÃO CALCULADA: {position_size:.6f} | Risco: ${risk_amount:.2f}")
            return position_size
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CÁLCULO DA POSIÇÃO: {e}")
            return 0.001

    def create_advanced_order(self, symbol, side, amount, order_type='market', 
                            price=None, stop_loss=None, take_profit=None, reduce_only=False):
        """Cria ordem avançada com gerenciamento de risco"""
        self.rate_limit()
        try:
            order_params = {
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'amount': amount,
                'params': {
                    'timeInForce': 'GTC'
                }
            }
            
            if price and order_type == 'limit':
                order_params['price'] = price
                
            # Adicionar stop loss e take profit
            if stop_loss:
                order_params['params']['stopLoss'] = str(stop_loss)
            if take_profit:
                order_params['params']['takeProfit'] = str(take_profit)
            if reduce_only:
                order_params['params']['reduceOnly'] = True
                
            order = self.exchange.create_order(**order_params)
            
            # Log detalhado
            self.log_order_created(order, side, amount, stop_loss, take_profit)
            
            return order
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO CRIAR ORDEM: {e}")
            return None

    def log_order_created(self, order, side, amount, sl, tp):
        """Log detalhado da ordem criada"""
        log_msg = f"""
🎯 ORDEM CRIADA COM SUCESSO:
   ► Side: {side.upper()}
   ► Amount: {amount:.6f}
   ► ID: {order['id']}
   ► Status: {order['status']}
   ► Stop Loss: {sl if sl else 'Não configurado'}
   ► Take Profit: {tp if tp else 'Não configurado'}
        """
        self.logger.info(log_msg)

    def get_open_positions(self, symbol=None):
        """Obtém posições abertas"""
        self.rate_limit()
        try:
            positions = self.exchange.fetch_positions(symbols=[symbol] if symbol else None)
            open_positions = [p for p in positions if p['contracts'] > 0]
            
            self.logger.info(f"📋 POSIÇÕES ABERTAS: {len(open_positions)}")
            return open_positions
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER POSIÇÕES: {e}")
            return []

    def cancel_all_orders(self, symbol=None):
        """Cancela todas as ordens"""
        self.rate_limit()
        try:
            if symbol:
                result = self.exchange.cancel_all_orders(symbol=symbol)
            else:
                result = self.exchange.cancel_all_orders()
            
            self.logger.info("🗑️ TODAS AS ORDENS FORAM CANCELADAS")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO CANCELAR ORDENS: {e}")
            return None

    def get_market_health(self, symbol=None):
        """Analisa a saúde do mercado"""
        try:
            ticker = self.get_advanced_ticker(symbol)
            if not ticker:
                return "UNKNOWN"
                
            spread = ticker['spread']
            volume = ticker['volume']
            
            if spread > 0.15:  # Spread muito alto
                return "HIGH_SPREAD"
            elif volume < 500000:  # Volume muito baixo
                return "LOW_VOLUME"
            elif spread > 0.1 and volume < 1000000:
                return "POOR_CONDITIONS"
            else:
                return "HEALTHY"
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE DE SAÚDE: {e}")
            return "UNKNOWN"

    def get_funding_rate(self, symbol=None):
        """Obtém taxa de funding para futuros"""
        self.rate_limit()
        try:
            if not symbol:
                symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            
            markets = self.exchange.load_markets()
            market = self.exchange.market(symbol)
            
            if 'swap' in market and market['swap']:
                funding_info = self.exchange.fetch_funding_rate(symbol)
                return funding_info
                
            return None
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER FUNDING RATE: {e}")
            return None

# Instância global para uso em outros módulos
bybit_advanced = BybitAdvancedIntegration()
