# bybit_integration.py - CONEXÃO BYBIT COMPLETA E CORRIGIDA
import ccxt
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from config import BYBIT_CONFIG, LOG_CONFIG

class BybitAdvancedIntegration:
    """
    Classe avançada para integração com Bybit API - MULTI-ENDPOINT
    """
    
    def __init__(self):
        self.config = BYBIT_CONFIG
        self.logger = self.setup_logger()
        self.exchange = None
        self.session_initialized = False
        self.fallback_mode = True
        self.current_price = 50000
        self.last_price_update = None
        
        # Múltiplos endpoints para tentar
        self.endpoints = [
            "https://api.bybit.com",
            "https://api.bytick.com", 
            "https://api.bybit.org"
        ]
        
        self.setup_exchange_advanced()
        
    def setup_logger(self):
        """Configura logger"""
        logger = logging.getLogger('BybitAdvanced')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
        return logger

    def setup_exchange_advanced(self):
        """Tenta múltiplos endpoints e configurações"""
        for endpoint in self.endpoints:
            try:
                self.logger.info(f"🔄 Tentando conectar com: {endpoint}")
                
                self.exchange = ccxt.bybit({
                    'apiKey': self.config['api_key'],
                    'secret': self.config['api_secret'],
                    'sandbox': self.config['testnet'],
                    'enableRateLimit': True,
                    'rateLimit': 300,
                    'options': {
                        'defaultType': 'linear',
                        'adjustForTimeDifference': True,
                        'recvWindow': 20000,
                    },
                })
                
                # Sobrescrever URL base
                self.exchange.urls['api'] = endpoint
                
                # Testar conexão
                markets = self.exchange.load_markets()
                self.session_initialized = True
                self.fallback_mode = False
                self.logger.info(f"✅ CONECTADO COM SUCESSO: {endpoint}")
                self.logger.info(f"📊 {len(markets)} mercados disponíveis")
                break
                
            except Exception as e:
                self.logger.warning(f"❌ Falha com {endpoint}: {str(e)[:100]}...")
                continue
        
        if not self.session_initialized:
            self.logger.warning("🚫 Todos os endpoints falharam, ativando modo fallback")
            self.fallback_mode = True

    def get_account_balance_detailed(self):
        """Obtém saldo REAL da conta"""
        try:
            if not self.session_initialized or self.fallback_mode:
                # Fallback para saldo simulado
                base_balance = self.config['initial_balance']
                variation = np.random.uniform(-0.1, 0.1)
                current_balance = base_balance * (1 + variation)
                
                simulated_balance = {
                    'total': {'USDT': round(current_balance, 2), 'BTC': 0.001},
                    'free': {'USDT': round(current_balance * 0.95, 2), 'BTC': 0.001},
                    'used': {'USDT': round(current_balance * 0.05, 2), 'BTC': 0.000},
                    'timestamp': datetime.now()
                }
                self.logger.info(f"💰 SALDO SIMULADO: USDT ${simulated_balance['total']['USDT']:.2f}")
                return simulated_balance
                
            # MODO REAL - Obter saldo real
            try:
                balance = self.exchange.fetch_balance()
                usdt_balance = balance.get('total', {}).get('USDT', 0)
                btc_balance = balance.get('total', {}).get('BTC', 0)
                
                real_balance = {
                    'total': {
                        'USDT': usdt_balance,
                        'BTC': btc_balance,
                    },
                    'free': {
                        'USDT': balance.get('free', {}).get('USDT', usdt_balance),
                        'BTC': balance.get('free', {}).get('BTC', btc_balance),
                    },
                    'used': {
                        'USDT': balance.get('used', {}).get('USDT', 0),
                        'BTC': balance.get('used', {}).get('BTC', 0),
                    },
                    'timestamp': datetime.now()
                }
                
                self.logger.info(f"💰 SALDO REAL: USDT ${usdt_balance:.2f} | BTC: {btc_balance:.6f}")
                return real_balance
                
            except Exception as e:
                self.logger.error(f"❌ ERRO AO OBTER SALDO REAL: {e}")
                # Fallback para não travar o bot
                return {
                    'total': {'USDT': self.config['initial_balance'], 'BTC': 0.001},
                    'free': {'USDT': self.config['initial_balance'], 'BTC': 0.001},
                    'timestamp': datetime.now()
                }
            
        except Exception as e:
            self.logger.error(f"❌ ERRO GERAL NO BALANÇO: {e}")
            return {
                'total': {'USDT': self.config['initial_balance'], 'BTC': 0.001},
                'timestamp': datetime.now()
            }

    def update_simulated_price(self):
        """Atualiza preço simulado com movimentos realistas"""
        if self.last_price_update is None or (datetime.now() - self.last_price_update).seconds > 60:
            # Movimento de preço realista
            price_change = np.random.normal(0, 0.002)
            self.current_price *= (1 + price_change)
            self.current_price = max(10000, min(100000, self.current_price))
            self.last_price_update = datetime.now()

    def get_advanced_ticker(self, symbol=None):
        """Obtém dados do ticker"""
        try:
            if not symbol:
                symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            
            if not self.session_initialized or self.fallback_mode:
                # Modo simulação
                self.update_simulated_price()
                
                spread = np.random.uniform(0.01, 0.05)
                base_volume = 1000000
                volume_variation = np.random.uniform(0.5, 2.0)
                
                simulated_ticker = {
                    'symbol': symbol,
                    'last': round(self.current_price, 2),
                    'bid': round(self.current_price * (1 - spread/200), 2),
                    'ask': round(self.current_price * (1 + spread/200), 2),
                    'high': round(self.current_price * (1 + np.random.uniform(0.01, 0.03)), 2),
                    'low': round(self.current_price * (1 - np.random.uniform(0.01, 0.03)), 2),
                    'volume': round(base_volume * volume_variation),
                    'spread': spread,
                    'timestamp': datetime.now()
                }
                
                return simulated_ticker
            
            # Modo real
            ticker = self.exchange.fetch_ticker(symbol)
            orderbook = self.exchange.fetch_order_book(symbol, limit=5)
            
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
                'spread': spread,
                'timestamp': ticker['timestamp']
            }
            
            return ticker_info
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER TICKER: {e}")
            self.update_simulated_price()
            return {
                'symbol': symbol or 'BTC/USDT:USDT',
                'last': round(self.current_price, 2),
                'bid': round(self.current_price * 0.999, 2),
                'ask': round(self.current_price * 1.001, 2),
                'volume': 1500000,
                'spread': 0.02,
                'timestamp': datetime.now()
            }

    def get_ohlcv_data(self, symbol=None, timeframe='5m', limit=100):
        """Obtém dados OHLCV para análise técnica"""
        try:
            if not symbol:
                symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            
            if not self.session_initialized or self.fallback_mode:
                return self.generate_realistic_ohlcv(limit)
            
            # Modo real
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            self.logger.info(f"📊 OHLCV REAL: {len(df)} candles | TF: {timeframe}")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER OHLCV: {e}")
            return self.generate_realistic_ohlcv(limit)

    def generate_realistic_ohlcv(self, limit=100):
        """Gera dados OHLCV realistas para simulação"""
        base_price = 50000
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=limit, freq='5min')
        
        prices = [base_price]
        for i in range(1, limit):
            trend = np.random.normal(0, 0.0005)
            noise = np.random.normal(0, 0.002)
            new_price = prices[-1] * (1 + trend + noise)
            prices.append(max(1000, new_price))
        
        df = pd.DataFrame(index=dates)
        df['close'] = prices
        df['open'] = df['close'].shift(1).fillna(base_price)
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.005, len(df)))
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.005, len(df)))
        df['volume'] = np.random.lognormal(14, 1, len(df))
        
        self.logger.info("📊 DADOS OHLCV SIMULADOS - Padrões realistas de mercado")
        return df

    def get_multiple_timeframes_data(self, symbol=None, timeframes=None):
        """Obtém dados de múltiplos timeframes"""
        if timeframes is None:
            timeframes = ['5m', '15m', '1h']
        
        multi_tf_data = {}
        
        for tf in timeframes:
            data = self.get_ohlcv_data(symbol, tf)
            if data is not None:
                multi_tf_data[tf] = data
        
        self.logger.info(f"✅ DADOS MULTI-TIMEFRAME: {len(multi_tf_data)} timeframes")
        return multi_tf_data

    def calculate_position_size(self, balance=None, risk_per_trade=None, stop_loss_pct=0.02):
        """Calcula tamanho da posição"""
        try:
            if balance is None:
                balance_info = self.get_account_balance_detailed()
                balance = balance_info['total']['USDT']
            
            if risk_per_trade is None:
                risk_per_trade = self.config['risk_per_trade']
            
            ticker = self.get_advanced_ticker()
            current_price = ticker['last']
            
            risk_amount = balance * risk_per_trade
            risk_per_unit = current_price * stop_loss_pct
            position_size = risk_amount / risk_per_unit
            
            max_size = self.config.get('max_position_size', 0.1)
            position_size = min(position_size, max_size)
            
            min_size = 0.001
            position_size = max(position_size, min_size)
            
            self.logger.info(f"📏 POSIÇÃO CALCULADA: {position_size:.6f} | Risco: ${risk_amount:.2f}")
            return position_size
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CÁLCULO DA POSIÇÃO: {e}")
            return 0.001

    def create_advanced_order(self, symbol, side, amount, order_type='market', 
                            price=None, stop_loss=None, take_profit=None):
        """Cria ordem REAL na exchange"""
        try:
            if not self.session_initialized or self.fallback_mode:
                # SIMULAÇÃO
                order_id = f"simulated_{int(time.time())}"
                ticker = self.get_advanced_ticker(symbol)
                executed_price = ticker['last']
                
                log_msg = f"""
🎯 ORDEM SIMULAÇÃO:
   Symbol: {symbol}
   Side: {side.upper()}
   Amount: {amount:.6f}
   Price: ${executed_price:.2f}
   Value: ${amount * executed_price:.2f}
   ID: {order_id}
   Status: filled
                """
                self.logger.info(log_msg)
                
                return {
                    'id': order_id, 
                    'status': 'closed', 
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'price': executed_price
                }
            
            # MODO REAL - Executar na exchange
            self.logger.info(f"🚀 EXECUTANDO ORDEM REAL: {side.upper()} {amount:.6f} {symbol}")
            
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
                
            if stop_loss:
                order_params['params']['stopLoss'] = str(stop_loss)
            if take_profit:
                order_params['params']['takeProfit'] = str(take_profit)
                
            order = self.exchange.create_order(**order_params)
            
            # Log detalhado da ordem real
            log_msg = f"""
✅ ORDEM REAL EXECUTADA:
   Symbol: {symbol}
   Side: {side.upper()} 
   Amount: {amount:.6f}
   Order ID: {order['id']}
   Status: {order['status']}
   Stop Loss: {stop_loss if stop_loss else 'Não'}
   Take Profit: {take_profit if take_profit else 'Não'}
            """
            self.logger.info(log_msg)
            
            return order
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ORDEM REAL: {e}")
            return None

    def get_open_positions(self, symbol=None):
        """Obtém posições abertas"""
        try:
            if not self.session_initialized or self.fallback_mode:
                return []
            
            positions = self.exchange.fetch_positions(symbols=[symbol] if symbol else None)
            open_positions = [p for p in positions if p['contracts'] > 0]
            
            self.logger.info(f"📋 POSIÇÕES ABERTAS: {len(open_positions)}")
            return open_positions
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER POSIÇÕES: {e}")
            return []

    def cancel_all_orders(self, symbol=None):
        """Cancela todas as ordens"""
        try:
            if not self.session_initialized or self.fallback_mode:
                self.logger.info("🗑️ SIMULAÇÃO: Todas as ordens canceladas")
                return True
            
            if symbol:
                result = self.exchange.cancel_all_orders(symbol=symbol)
            else:
                result = self.exchange.cancel_all_orders()
            
            self.logger.info("🗑️ TODAS AS ORDENS CANCELADAS")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO CANCELAR ORDENS: {e}")
            return None

    def get_market_health(self, symbol=None):
        """Analisa a saúde do mercado"""
        try:
            ticker = self.get_advanced_ticker(symbol)
            spread = ticker['spread']
            volume = ticker['volume']
            
            if spread > 0.15:
                return "HIGH_SPREAD"
            elif volume < 500000:
                return "LOW_VOLUME"
            elif spread > 0.1 and volume < 1000000:
                return "POOR_CONDITIONS"
            else:
                return "HEALTHY"
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE DE SAÚDE: {e}")
            return "UNKNOWN"

    def get_connection_status(self):
        """Status detalhado da conexão"""
        return {
            'connected': self.session_initialized,
            'fallback_mode': self.fallback_mode,
            'testnet': self.config['testnet'],
            'endpoint': self.exchange.urls['api'] if self.exchange else 'N/A'
        }

# Instância global
bybit_advanced = BybitAdvancedIntegration()
