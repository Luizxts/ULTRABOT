import logging
import hmac
import hashlib
import time
import json
from typing import Dict, List, Optional
import aiohttp
import asyncio

try:
    from config import BYBIT_API_KEY, BYBIT_API_SECRET, TRADING_MODE
except ImportError:
    # Valores padrão para desenvolvimento
    BYBIT_API_KEY = "g9NOzMIa9Ye7lJ6QCI"
    BYBIT_API_SECRET = "c9TdmpaeB0mxSmJQxa00BDevU6eT3Yze48X2"
    TRADING_MODE = "SIMULATION"

logger = logging.getLogger(__name__)

class BybitAnalyser:
    def __init__(self, simulation_mode: bool = (TRADING_MODE == "SIMULATION")):
        self.simulation_mode = simulation_mode
        self.base_url = "https://api.bybit.com"
        self.session = None
        self.api_key = BYBIT_API_KEY
        self.api_secret = BYBIT_API_SECRET
        self.last_balance = 18.34
        
        if not simulation_mode:
            logger.warning("🚀 MODO REAL ATIVADO - CONEXÃO DIRETA COM BYBIT!")
            logger.warning("⚠️  OPERANDO COM DINHEIRO REAL - EXTREMO CUIDADO!")
        else:
            logger.warning("🎮 MODO SIMULADO ATIVADO")
    
    def _generate_signature(self, params: dict) -> str:
        """Gera assinatura para API Bybit"""
        param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(
            self.api_secret.encode("utf-8"),
            param_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
    
    async def get_balance(self) -> float:
        """Obtém saldo REAL da conta Bybit"""
        if self.simulation_mode:
            # Retorna saldo simulado baseado na sua imagem real
            return self.last_balance
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Timestamp para a requisição
            timestamp = int(time.time() * 1000)
            
            # Parâmetros da requisição
            params = {
                'api_key': self.api_key,
                'timestamp': timestamp
            }
            
            # Gerar assinatura
            signature = self._generate_signature(params)
            params['sign'] = signature
            
            # Fazer requisição para API Bybit
            url = f"{self.base_url}/v2/private/wallet/balance"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extrair saldo USDT
                    if data.get('result') and 'USDT' in data['result']:
                        usdt_balance = float(data['result']['USDT']['available_balance'])
                        self.last_balance = usdt_balance
                        logger.info(f"💰 Saldo Bybit real: ${usdt_balance:.2f}")
                        return usdt_balance
                    else:
                        logger.error("❌ Estrutura de resposta inesperada da Bybit")
                        return self.last_balance
                else:
                    logger.error(f"❌ Erro API Bybit: HTTP {response.status}")
                    return self.last_balance
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo Bybit: {e}")
            return self.last_balance
    
    async def get_account_info(self) -> Dict:
        """Obtém informações da conta"""
        if self.simulation_mode:
            return {
                'balance': self.last_balance,
                'currency': 'USDT',
                'mode': 'SIMULATION',
                'timestamp': time.time()
            }
        
        try:
            timestamp = int(time.time() * 1000)
            params = {
                'api_key': self.api_key,
                'timestamp': timestamp
            }
            
            signature = self._generate_signature(params)
            params['sign'] = signature
            
            url = f"{self.base_url}/v2/private/wallet/balance"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'balance': float(data['result']['USDT']['available_balance']),
                        'currency': 'USDT',
                        'mode': 'REAL',
                        'timestamp': time.time(),
                        'raw_data': data
                    }
                else:
                    logger.error(f"❌ Erro ao obter info conta: HTTP {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações da conta: {e}")
            return {}
    
    async def get_open_orders(self) -> List[Dict]:
        """Obtém ordens abertas"""
        if self.simulation_mode:
            return []
        
        try:
            timestamp = int(time.time() * 1000)
            params = {
                'api_key': self.api_key,
                'timestamp': timestamp
            }
            
            signature = self._generate_signature(params)
            params['sign'] = signature
            
            url = f"{self.base_url}/v2/private/order/list"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('result', {}).get('data', [])
                else:
                    logger.error(f"❌ Erro ao obter ordens: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"❌ Erro ao obter ordens abertas: {e}")
            return []
    
    async def get_positions(self) -> List[Dict]:
        """Obtém posições ativas"""
        if self.simulation_mode:
            return []
        
        try:
            timestamp = int(time.time() * 1000)
            params = {
                'api_key': self.api_key,
                'timestamp': timestamp
            }
            
            signature = self._generate_signature(params)
            params['sign'] = signature
            
            url = f"{self.base_url}/v2/private/position/list"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('result', [])
                else:
                    logger.error(f"❌ Erro ao obter posições: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"❌ Erro ao obter posições: {e}")
            return []
    
    async def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "Market") -> bool:
        """Coloca uma ordem"""
        if self.simulation_mode:
            logger.info(f"🎮 Ordem simulada: {side} {quantity} {symbol}")
            return True
        
        try:
            timestamp = int(time.time() * 1000)
            params = {
                'api_key': self.api_key,
                'symbol': symbol,
                'side': side,
                'order_type': order_type,
                'qty': str(quantity),
                'time_in_force': 'GoodTillCancel',
                'timestamp': timestamp
            }
            
            signature = self._generate_signature(params)
            params['sign'] = signature
            
            url = f"{self.base_url}/v2/private/order/create"
            async with self.session.post(url, data=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ret_code') == 0:
                        logger.info(f"✅ Ordem real executada: {side} {quantity} {symbol}")
                        return True
                    else:
                        logger.error(f"❌ Erro na ordem: {data.get('ret_msg', 'Unknown error')}")
                        return False
                else:
                    logger.error(f"❌ Erro HTTP na ordem: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Erro ao colocar ordem: {e}")
            return False
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancela uma ordem"""
        if self.simulation_mode:
            logger.info(f"🎮 Ordem cancelada (simulada): {order_id}")
            return True
        
        try:
            timestamp = int(time.time() * 1000)
            params = {
                'api_key': self.api_key,
                'symbol': symbol,
                'order_id': order_id,
                'timestamp': timestamp
            }
            
            signature = self._generate_signature(params)
            params['sign'] = signature
            
            url = f"{self.base_url}/v2/private/order/cancel"
            async with self.session.post(url, data=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('ret_code') == 0
                else:
                    logger.error(f"❌ Erro ao cancelar ordem: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Erro ao cancelar ordem: {e}")
            return False
    
    async def verify_connection(self) -> bool:
        """Verifica conexão com a Bybit"""
        if self.simulation_mode:
            logger.info("✅ Conexão simulada com Bybit - OK")
            return True
        
        try:
            # Testar conexão com endpoint público
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/public/time", timeout=10) as response:
                    if response.status == 200:
                        logger.info("✅ Conexão com Bybit - OK")
                        return True
                    else:
                        logger.error(f"❌ Falha na conexão com Bybit: HTTP {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Falha na conexão com Bybit: {e}")
            return False
    
    def set_real_mode(self):
        """Configura modo real"""
        self.simulation_mode = False
        logger.warning("🚀 MUDADO PARA MODO REAL - CUIDADO!")
    
    def set_simulation_mode(self):
        """Configura modo simulação"""
        self.simulation_mode = True
        logger.info("🎮 Modo simulação ativado")
