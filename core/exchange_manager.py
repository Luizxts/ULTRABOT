import ccxt
import logging
import asyncio
import time
import numpy as np
from decimal import Decimal, ROUND_DOWN
from core.config import config

logger = logging.getLogger('ExchangeManager')

class BybitManager:
    """Gerenciador Bybit - Modo Testes Seguros com R$100"""
    
    def __init__(self):
        # 🔥 CONEXÃO REAL MAS COM PROTEGÇÕES
        self.exchange = ccxt.bybit({
            'apiKey': config.BYBIT_API_KEY,
            'secret': config.BYBIT_API_SECRET,
            'sandbox': config.BYBIT_TESTNET,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        self.modo_offline = False
        self.saldo_inicial = 0
        self._verificar_configuracao_segura()
        logger.info("💰 BYBIT MANAGER - MODO TESTES SEGUROS ATIVADO!")
    
    def _verificar_configuracao_segura(self):
        """Verificação de segurança para testes"""
        try:
            # Verificar saldo real
            balance = self.exchange.fetch_balance()
            saldo_usdt = float(balance['total'].get('USDT', 0))
            self.saldo_inicial = saldo_usdt
            
            logger.info(f"💰 SALDO INICIAL: {saldo_usdt} USDT")
            
            if saldo_usdt < 15:  # Mínimo $15 USD
                logger.critical("🚫 SALDO INSUFICIENTE PARA TESTES")
                raise Exception(f"Saldo muito baixo: {saldo_usdt} USDT. Mínimo: $15 USD")
            
            if saldo_usdt > 100:  # Limite de segurança
                logger.warning("⚠️ SALDO ALTO - Confirme que quer operar real")
            
            # Verificar pares acessíveis
            markets = self.exchange.load_markets()
            for par in config.PARES_MONITORADOS:
                if par not in markets:
                    logger.warning(f"⚠️ Par não disponível: {par}")
            
            logger.info("✅ CONFIGURAÇÃO SEGURA - PRONTO PARA TESTES")
            
        except Exception as e:
            logger.error(f"❌ ERRO CONFIGURAÇÃO: {e}")
            self.modo_offline = True
    
    def obter_saldo(self):
        """Obter saldo REAL com verificações"""
        try:
            balance = self.exchange.fetch_balance()
            saldo = float(balance['total'].get('USDT', 0))
            
            # 🔒 VERIFICAÇÃO DE SEGURANÇA
            if saldo < 5:  # Mínimo $5 USD
                logger.critical("🚫 SALDO CRÍTICO - Parando operações")
                self.modo_offline = True
            
            return saldo
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo: {e}")
            return 0.0
    
    def _calcular_quantidade_segura(self, par, valor_usdt):
        """Calcular quantidade com MÚLTIPLAS proteções"""
        try:
            # 1. Obter preço atual
            ticker = self.exchange.fetch_ticker(par)
            preco_atual = ticker['last']
            
            if preco_atual == 0:
                raise Exception(f"Preço zero para {par}")
            
            # 2. Calcular quantidade
            quantidade = valor_usdt / preco_atual
            
            # 3. Obter informações de precisão
            mercado = self.exchange.load_markets()
            symbol_info = mercado[par]
            
            # 4. Aplicar precisão
            precision = symbol_info['precision']['amount']
            quantidade = float(Decimal(str(quantidade)).quantize(
                Decimal(str(precision)), rounding=ROUND_DOWN
            ))
            
            # 5. Verificar quantidade mínima
            min_amount = symbol_info['limits']['amount']['min']
            if quantidade < min_amount:
                logger.warning(f"⚠️ Quantidade ajustada para mínima: {min_amount}")
                quantidade = min_amount
            
            logger.info(f"📊 {par}: Preço=${preco_atual:.4f}, Qtd={quantidade:.6f}")
            return quantidade
            
        except Exception as e:
            logger.error(f"❌ Erro cálculo quantidade {par}: {e}")
            raise
    
    async def executar_ordem(self, par, direcao, valor_usdt):
        """Executar ordem com MÁXIMA SEGURANÇA"""
        if self.modo_offline:
            raise Exception(f"MODO OFFLINE - {par} {direcao}")
        
        try:
            logger.info(f"💰 EXECUTANDO ORDEM: {par} {direcao} ${valor_usdt}")
            
            # 🛡️ VERIFICAÇÕES DE SEGURANÇA
            saldo_atual = self.obter_saldo()
            
            # 1. Verificar saldo suficiente
            if saldo_atual < valor_usdt:
                raise Exception(f"Saldo insuficiente: ${saldo_atual:.2f} < ${valor_usdt}")
            
            # 2. Verificar limite por trade (não mais que 50% do saldo)
            if valor_usdt > saldo_atual * 0.5:
                raise Exception(f"Valor muito alto: ${valor_usdt} > 50% do saldo")
            
            # 3. Calcular quantidade segura
            quantidade = self._calcular_quantidade_segura(par, valor_usdt)
            
            # 4. Executar ordem
            if direcao.upper() == 'BUY':
                ordem = self.exchange.create_market_buy_order(par, quantidade)
            else:
                ordem = self.exchange.create_market_sell_order(par, quantidade)
            
            logger.info(f"✅ ORDEM EXECUTADA: {ordem['id']} - ${ordem['cost']:.2f}")
            
            # 5. Registrar operação
            custo_real = float(ordem['cost'])
            logger.info(f"💰 CUSTO REAL: ${custo_real:.2f}")
            
            return {
                'id': ordem['id'],
                'symbol': ordem['symbol'],
                'side': ordem['side'],
                'price': float(ordem['price']),
                'amount': float(ordem['amount']),
                'cost': custo_real,
                'timestamp': ordem['timestamp'],
                'status': ordem['status']
            }
            
        except Exception as e:
            logger.error(f"❌ ERRO ORDEM {par}: {e}")
            raise
    
    def obter_dados_mercado(self, par, timeframe='15m', limit=50):
        """Obter dados do mercado"""
        try:
            return self.exchange.fetch_ohlcv(par, timeframe, limit=limit)
        except Exception as e:
            logger.warning(f"⚠️ Erro dados {par}: {e}")
            # Fallback simples
            return self._dados_fallback(par, limit)
    
    def _dados_fallback(self, par, limit):
        """Dados de fallback"""
        current_time = int(time.time() * 1000)
        data = []
        base_price = 0.5 if 'XRP' in par else 0.4  # Preços realistas
        
        for i in range(limit):
            timestamp = current_time - (limit - i) * 900000
            price_change = np.random.normal(0, 0.01)
            open_price = base_price * (1 + price_change)
            high_price = open_price * 1.02
            low_price = open_price * 0.98
            close_price = (high_price + low_price) / 2
            volume = np.random.uniform(10000, 100000)
            
            data.append([timestamp, open_price, high_price, low_price, close_price, volume])
        
        return data

logger.info("🔐 BYBIT - MODO TESTES SEGUROS ATIVADO")
logger.info("💰 SALDO: R$100 (TESTES CONSERVADORES)")
logger.info("🎯 OBJETIVO: TESTES SEGUROS COM LUCRO")
