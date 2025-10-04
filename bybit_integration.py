# bybit_integration.py - CONEXÃO BYBIT COMPLETA E OTIMIZADA
import ccxt
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from config import BYBIT_CONFIG, LOG_CONFIG

class BybitAdvancedIntegration:
    """
    Classe avançada para integração com Bybit API - CONTA REAL
    Sistema resiliente com fallback automático
    """
    
    def __init__(self):
        self.config = BYBIT_CONFIG
        self.logger = self.setup_logger()
        self.exchange = None
        self.session_initialized = False
        self.fallback_mode = True  # Começar em fallback por segurança
        self.market_data_cache = {}
        self.last_price_update = None
        self.current_price = 50000  # Preço base simulado
        
        self.setup_exchange_smart()
        
    def setup_logger(self):
        """Configura logger para Bybit"""
        logger = logging.getLogger('BybitAdvanced')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
        return logger

    def setup_exchange_smart(self):
        """Configuração inteligente - tenta conectar, mas opera em fallback se bloqueado"""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': self.config['api_key'],
                'secret': self.config['api_secret'],
                'sandbox': self.config['testnet'],
                'enableRateLimit': True,
                'rateLimit': 200,
                'options': {
                    'defaultType': 'linear',
                    'adjustForTimeDifference': True,
                    'recvWindow': 15000,
                },
            })
            
            # Tentativa rápida e segura de conexão
            try:
                markets = self.exchange.load_markets()
                self.session_initialized = True
                self.fallback_mode = False
                mode = "TESTNET" if self.config['testnet'] else "MAINNET"
                self.logger.info(f"✅ BYBIT {mode} CONECTADO - {len(markets)} mercados")
            except Exception as e:
                self.logger.warning(f"🔄 Conexão Bybit falhou, ativando modo fallback: {str(e)[:100]}...")
                self.session_initialized = False
                self.fallback_mode = True
                
        except Exception as e:
            self.logger.warning(f"🔄 MODO FALLBACK ATIVADO: {str(e)[:100]}...")
            self.session_initialized = False
            self.fallback_mode = True
            self.logger.info("🎯 OPERANDO EM MODO SIMULAÇÃO - Dados realistas para desenvolvimento")

    def get_account_balance_detailed(self):
        """Obtém saldo detalhado da conta - com fallback realista"""
        try:
            if not self.session_initialized or self.fallback_mode:
                # Simular saldo realista com variações
                base_balance = self.config['initial_balance']
                # Adicionar variação realista (±10%)
                variation = np.random.uniform(-0.1, 0.1)
                current_balance = base_balance * (1 + variation)
                
                simulated_balance = {
                    'total': {
                        'USDT': round(current_balance, 2),
                        'BTC': 0.001 + np.random.uniform(0, 0.0005),
                    },
                    'free': {
                        'USDT': round(current_balance * 0.95, 2),  # 5% em uso
                        'BTC': 0.001,
                    },
                    'used': {
                        'USDT': round(current_balance * 0.05, 2),
                        'BTC': 0.000,
                    },
                    'timestamp': datetime.now()
                }
                self.logger.info(f"💰 SALDO SIMULADO: USDT ${simulated_balance['total']['USDT']:.2f}")
                return simulated_balance
                
            # Modo real - conectar à Bybit
            balance = self.exchange.fetch_balance()
            balance_info = {
                'total': {
                    'USDT': balance.get('total', {}).get('USDT', self.config['initial_balance']),
                    'BTC': balance.get('total', {}).get('BTC', 0),
                },
                'free': {
                    'USDT': balance.get('free', {}).get('USDT', self.config['initial_balance']),
                    'BTC': balance.get('free', {}).get('BTC', 0),
                },
                'used': {
                    'USDT': balance.get('used', {}).get('USDT', 0),
                    'BTC': balance.get('used', {}).get('BTC', 0),
                },
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"💰 SALDO REAL: USDT ${balance_info['total']['USDT']:.2f}")
            return balance_info
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER BALANÇO: {e}")
            # Fallback para saldo simulado
            return {
                'total': {'USDT': self.config['initial_balance'], 'BTC': 0.001},
                'free': {'USDT': self.config['initial_balance'], 'BTC': 0.001},
                'used': {'USDT': 0, 'BTC': 0},
                'timestamp': datetime.now()
            }

    def update_simulated_price(self):
        """Atualiza preço simulado com movimentos realistas"""
        if self.last_price_update is None or (datetime.now() - self.last_price_update).seconds > 60:
            # Movimento de preço realista (variação diária típica de 2-8%)
            price_change = np.random.normal(0, 0.002)  # 0.2% de desvio padrão
            self.current_price *= (1 + price_change)
            
            # Garantir que o preço fique em range realista
            self.current_price = max(10000, min(100000, self.current_price))
            self.last_price_update = datetime.now()

    def get_advanced_ticker(self, symbol=None):
        """Obtém dados avançados do ticker - com dados simulados realistas"""
        try:
            if not symbol:
                symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            
            if not self.session_initialized or self.fallback_mode:
                # Atualizar preço simulado
                self.update_simulated_price()
                
                # Gerar dados de ticker realistas
                spread = np.random.uniform(0.01, 0.05)  # Spread típico 0.01-0.05%
                base_volume = 1000000  # Volume base
                volume_variation = np.random.uniform(0.5, 2.0)  # Variação de volume
                
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
            
            # Modo real - obter dados da Bybit
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
            # Fallback para dados simulados
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
        """Obtém dados OHLCV para análise técnica - com dados simulados realistas"""
        try:
            if not symbol:
                symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            
            if not self.session_initialized or self.fallback_mode:
                # Gerar dados OHLCV simulados realistas
                return self.generate_realistic_ohlcv(limit)
            
            # Modo real - obter dados da Bybit
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
        # Preço base começando em valor realista
        base_price = 50000
        
        # Gerar timestamps
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=limit, freq='5min')
        
        # Gerar preços com tendência e volatilidade realistas
        prices = [base_price]
        for i in range(1, limit):
            # Tendência suave + ruído + volatilidade
            trend = np.random.normal(0, 0.0005)  # Tendência muito suave
            noise = np.random.normal(0, 0.002)   # Ruído diário ~0.2%
            new_price = prices[-1] * (1 + trend + noise)
            prices.append(max(1000, new_price))  # Preço mínimo $1000
        
        # Criar DataFrame OHLCV realista
        df = pd.DataFrame(index=dates)
        df['close'] = prices
        
        # Gerar OHLC realista (Open, High, Low baseado no Close)
        df['open'] = df['close'].shift(1).fillna(base_price)
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.005, len(df)))
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.005, len(df)))
        df['volume'] = np.random.lognormal(14, 1, len(df))  # Volume log-normal realista
        
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
        """Calcula tamanho avançado da posição"""
        try:
            if balance is None:
                balance_info = self.get_account_balance_detailed()
                balance = balance_info['total']['USDT']
            
            if risk_per_trade is None:
                risk_per_trade = self.config['risk_per_trade']
            
            # Obter preço atual
            ticker = self.get_advanced_ticker()
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
                            price=None, stop_loss=None, take_profit=None):
        """Cria ordem avançada com gerenciamento de risco"""
        try:
            if not self.session_initialized or self.fallback_mode:
                # Simular ordem em modo fallback
                order_id = f"simulated_{int(time.time())}"
                self.logger.info(f"🎯 SIMULAÇÃO: {side.upper()} {amount:.6f} {symbol}")
                
                # Log detalhado da ordem simulada
                self.log_order_created({
                    'id': order_id,
                    'status': 'closed',
                    'symbol': symbol,
                    'side': side,
                    'amount': amount
                }, side, amount, stop_loss, take_profit)
                
                return {'id': order_id, 'status': 'closed', 'symbol': symbol}
            
            # Modo real - criar ordem na Bybit
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
                
            order = self.exchange.create_order(**order_params)
            
            # Log detalhado
            self.log_order_created(order, side, amount, stop_loss, take_profit)
            
            return order
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO CRIAR ORDEM: {e}")
            return None

    def log_order_created(self, order, side, amount, sl, tp):
        """Log detalhado da ordem criada"""
        mode = "SIMULAÇÃO" if not self.session_initialized or self.fallback_mode else "REAL"
        
        log_msg = f"""
🎯 ORDEM {mode} CRIADA:
   Side: {side.upper()}
   Amount: {amount:.6f}
   ID: {order['id']}
   Status: {order['status']}
   Stop Loss: {sl if sl else 'Não'}
   Take Profit: {tp if tp else 'Não'}
        """
        self.logger.info(log_msg)

    def get_open_positions(self, symbol=None):
        """Obtém posições abertas"""
        try:
            if not self.session_initialized or self.fallback_mode:
                # Simular sem posições abertas
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
            elif volume < 500000:  # Volume muito baixo
                return "LOW_VOLUME"
            elif spread > 0.1 and volume < 1000000:
                return "POOR_CONDITIONS"
            else:
                return "HEALTHY"
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE DE SAÚDE: {e}")
            return "UNKNOWN"

    def get_connection_status(self):
        """Retorna status da conexão"""
        return {
            'connected': self.session_initialized,
            'fallback_mode': self.fallback_mode,
            'testnet': self.config['testnet'],
            'symbol': self.config['symbol']
        }

# Instância global para uso em outros módulos
bybit_advanced = BybitAdvancedIntegration()
