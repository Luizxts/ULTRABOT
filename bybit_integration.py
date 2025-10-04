# # bybit_integration.py - CONEXÃO BYBIT COM MÚLTIPLOS ENDPOINTS
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

    # ... (mantenha os outros métodos iguais ao anterior)

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
