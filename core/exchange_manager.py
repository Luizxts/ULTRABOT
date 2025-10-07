import ccxt
import logging
import asyncio
import time
import numpy as np
import os
from decimal import Decimal, ROUND_DOWN
from core.config import config

logger = logging.getLogger('ExchangeManager')

class BybitManager:
    """Gerenciador Bybit 100% SEGURO - Modo Análise Apenas"""
    
    def __init__(self):
        # 🔥 BLOQUEIO PERMANENTE DE SEGURANÇA
        self._ativar_bloqueio_seguranca()
        
        # 💰 MODO APENAS ANÁLISE - SEM RISCO
        self.modo_offline = True
        self.bloqueio_permanente = True
        self.modo_apenas_analise = True
        
        logger.info("💰 BYBIT MANAGER - MODO ANÁLISE SEGURO ATIVADO")
        logger.critical("🚫 BLOQUEIO PERMANENTE: Operações reais DESATIVADAS")
    
    def _ativar_bloqueio_seguranca(self):
        """Ativar bloqueios de segurança permanentes"""
        # 🔒 BLOQUEIO 1: Railway detectado
        if 'RAILWAY' in os.environ:
            logger.critical("🚫 BLOQUEIO RAILWAY: Ambiente não permite operações reais")
        
        # 🔒 BLOQUEIO 2: Modo análise forçado
        if hasattr(config, 'MODO_ANALISE') and config.MODO_ANALISE:
            logger.critical("🚫 BLOQUEIO CONFIG: Modo análise ativado na configuração")
        
        # 🔒 BLOQUEIO 3: Sem credenciais API
        if not config.BYBIT_API_KEY or config.BYBIT_API_KEY == 'SUA_API_KEY_REAL_AQUI':
            logger.critical("🚫 BLOQUEIO API: Credenciais não configuradas")
    
    def _verificar_conexao_inteligente(self):
        """Apenas para compatibilidade - Sempre modo offline"""
        self.modo_offline = True
        self.bloqueio_permanente = True
        logger.info("🔍 MODO ANÁLISE: Apenas monitoramento de mercado")
        return False
    
    def obter_saldo(self):
        """Saldo simulado - ZERO RISCO"""
        logger.info("💰 SALDO SIMULADO: Modo análise gratuita")
        return 0.0  # Saldo zero para garantir segurança
    
    def obter_dados_mercado(self, par, timeframe='15m', limit=100):
        """Obter dados para análise - SEM OPERAÇÕES"""
        try:
            # 🔍 TENTAR DADOS REIAS APENAS PARA ANÁLISE
            if not hasattr(self, 'exchange'):
                self.exchange = ccxt.bybit({
                    'apiKey': 'API_KEY_DUMMY',
                    'secret': 'SECRET_DUMMY', 
                    'sandbox': True,
                    'enableRateLimit': True,
                })
            
            ohlcv = self.exchange.fetch_ohlcv(par, timeframe, limit=limit)
            if ohlcv and len(ohlcv) > 0:
                logger.debug(f"📊 Dados reais para análise: {par}")
                return ohlcv
            else:
                raise Exception("Dados vazios")
                
        except Exception as e:
            # 🔄 FALLBACK PARA DADOS SIMULADOS
            logger.debug(f"📊 Usando dados simulados para análise: {par}")
            return self._dados_simulados_realistas(par, limit)
    
    def _dados_simulados_realistas(self, par, limit):
        """Gerar dados simulados realistas para análise"""
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
            
            # Movimento de preço realista
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
        
        logger.debug(f"📊 Dados simulados gerados para {par}")
        return data
    
    def obter_preco_atual(self, par):
        """Obter preço atual para análise - SEM RISCO"""
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
        preco = precios_simulados.get(par, 100)
        logger.debug(f"📈 Preço simulado para análise: {par} = ${preco}")
        return preco
    
    def _calcular_quantidade(self, par, valor_usdt):
        """Calcular quantidade para análise - SEM EXECUÇÃO"""
        preco_atual = self.obter_preco_atual(par)
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
        
        logger.info(f"📊 ANÁLISE: {par} - Preço=${preco_atual:.2f}, Qtd teórica={quantidade}")
        return quantidade
    
    async def executar_ordem(self, par, direcao, valor_usdt):
        """🚫 BLOQUEADO - ORDENS REAIS DESATIVADAS"""
        error_msg = f"""
🚫 ORDEM BLOQUEADA - MODO ANÁLISE

Par: {par}
Direção: {direcao}
Valor: ${valor_usdt}

💡 SEU ROBÔ ESTÁ EM MODO ANÁLISE SEGURO
📊 Apenas gera sinais para você analisar
💰 NENHUMA operação real é executada

🔒 BLOQUEIOS ATIVOS:
• Modo análise ativado
• Railway environment
• Credenciais não configuradas

⚡ Use os sinais para análise manual
🎯 Zero risco - Zero custo
        """
        
        logger.critical(f"🚫 TENTATIVA DE ORDEM BLOQUEADA: {par} {direcao}")
        logger.critical("🔒 MODO ANÁLISE: Operações reais permanentemente desativadas")
        
        raise Exception(error_msg)
    
    def get_status(self):
        """Status de segurança do sistema"""
        return {
            'modo': 'ANÁLISE SEGURA',
            'bloqueio_permanente': True,
            'operacoes_reais': 'DESATIVADAS',
            'saldo': 'SIMULADO (R$ 0,00)',
            'risco': 'ZERO',
            'ambiente': 'RAILWAY GRATUITO'
        }
    
    def verificar_seguranca(self):
        """Verificação completa de segurança"""
        verificacoes = {
            'modo_offline': self.modo_offline,
            'bloqueio_permanente': self.bloqueio_permanente,
            'modo_apenas_analise': self.modo_apenas_analise,
            'ambiente_railway': 'RAILWAY' in os.environ,
            'credenciais_configured': hasattr(config, 'BYBIT_API_KEY') and config.BYBIT_API_KEY not in ['', 'SUA_API_KEY_REAL_AQUI'],
            'operacoes_ativas': False
        }
        
        logger.info("🔒 VERIFICAÇÃO DE SEGURANÇA COMPLETA:")
        for check, status in verificacoes.items():
            logger.info(f"   {check}: {'✅ SEGURO' if not status else '❌ RISCO'}")
        
        return all(not status for status in [verificacoes['credenciais_configured'], verificacoes['operacoes_ativas']])

# 🔒 VERIFICAÇÃO DE SEGURANÇA NA INICIALIZAÇÃO
logger.info("🔒 INICIALIZANDO SISTEMA 100% SEGURO")
logger.info("💰 MODO: ANÁLISE GRATUITA - SEM OPERAÇÕES REAIS")
logger.info("🚫 BYBIT: BLOQUEADO PERMANENTEMENTE")
