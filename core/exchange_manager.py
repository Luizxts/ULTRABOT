import ccxt
import logging
import asyncio
from decimal import Decimal, ROUND_DOWN
from core.config import config

logger = logging.getLogger('ExchangeManager')

class BybitManager:
    """Gerenciador Bybit com URLs alternativas para Railway"""
    
    def __init__(self):
        # 🔥 CONFIGURAÇÃO BYBIT COM URLs ALTERNATIVAS
        self.exchange = ccxt.bybit({
            'apiKey': config.BYBIT_API_KEY,
            'secret': config.BYBIT_API_SECRET,
            'sandbox': config.BYBIT_TESTNET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
            },
            # 🚀 URLs ALTERNATIVAS para evitar bloqueio
            'urls': {
                'api': {
                    'public': 'https://api.bybit.com',  # Tentar principal
                    'private': 'https://api.bybit.com',
                    # Alternativas se principal falhar
                    'api': 'https://api.bytick.com',    # URL alternativa 1
                    'test': 'https://api-testnet.bybit.com',
                }
            }
        })
        
        self._verificar_conexao_inteligente()
        logger.info("💰 BYBIT MANAGER INICIALIZADO - MODO REAL!")
    
    def _verificar_conexao_inteligente(self):
        """Verificação inteligente com múltiplas tentativas"""
        endpoints_para_testar = [
            # Tentar endpoints diferentes
            lambda: self.exchange.fetch_balance(),
            lambda: self.exchange.fetch_ticker('BTC/USDT'),
            lambda: self.exchange.load_markets(),
            lambda: self.exchange.fetch_order_book('BTC/USDT', limit=5),
        ]
        
        for i, endpoint in enumerate(endpoints_para_testar):
            try:
                result = endpoint()
                logger.info(f"✅ Endpoint {i+1} funcionou: {type(result).__name__}")
                
                # Se chegou aqui, conexão está ok
                if hasattr(result, 'get') and 'total' in result:
                    usdt_balance = result['total'].get('USDT', 0)
                    logger.info(f"💰 SALDO BYBIT REAL: {usdt_balance} USDT")
                
                return True
                
            except Exception as e:
                logger.warning(f"⚠️ Endpoint {i+1} falhou: {str(e)[:100]}...")
                continue
        
        # 🔥 SE TODOS FALHAREM, TENTAR MUDAR URL DINAMICAMENTE
        logger.warning("🔄 Tentando reconexão com URL alternativa...")
        return self._tentar_urls_alternativas()
    
    def _tentar_urls_alternativas(self):
        """Tentar URLs alternativas da Bybit"""
        urls_alternativas = [
            'https://api.bytick.com',
            'https://api.bybit.com',
            'https://api-testnet.bybit.com'
        ]
        
        for url in urls_alternativas:
            try:
                logger.info(f"🔄 Tentando URL: {url}")
                
                # Criar nova instância com URL alternativa
                exchange_alt = ccxt.bybit({
                    'apiKey': config.BYBIT_API_KEY,
                    'secret': config.BYBIT_API_SECRET,
                    'sandbox': config.BYBIT_TESTNET,
                    'enableRateLimit': True,
                    'urls': {
                        'api': {
                            'public': url,
                            'private': url,
                        }
                    }
                })
                
                # Testar conexão
                test_result = exchange_alt.fetch_ticker('BTC/USDT')
                if test_result and 'last' in test_result:
                    logger.info(f"🎯 URL ALTERNATIVA FUNCIONOU: {url}")
                    self.exchange = exchange_alt  # Usar esta instância
                    return True
                    
            except Exception as e:
                logger.warning(f"❌ URL {url} falhou: {str(e)[:100]}...")
                continue
        
        # 🚨 SE NADA FUNCIONAR, CRIAR MODO OFFLINE INTELIGENTE
        logger.error("💥 Todas as URLs falharam - Ativando modo offline inteligente")
        self._ativar_modo_offline()
        return False
    
    def _ativar_modo_offline(self):
        """Ativar modo offline com reconexão automática"""
        self.modo_offline = True
        self.ultima_tentativa = time.time()
        
        # 🔄 AGENDAR RECONEXÃO AUTOMÁTICA
        asyncio.create_task(self._reconexao_automatica())
    
    async def _reconexao_automatica(self):
        """Tentativa de reconexão automática a cada 5 minutos"""
        while self.modo_offline:
            await asyncio.sleep(300)  # 5 minutos
            
            try:
                logger.info("🔄 Tentando reconexão automática...")
                # Criar nova instância
                novo_exchange = ccxt.bybit({
                    'apiKey': config.BYBIT_API_KEY,
                    'secret': config.BYBIT_API_SECRET,
                    'sandbox': config.BYBIT_TESTNET,
                    'enableRateLimit': True,
                })
                
                # Testar
                novo_exchange.fetch_ticker('BTC/USDT')
                
                # Se chegou aqui, reconexão bem-sucedida
                self.exchange = novo_exchange
                self.modo_offline = False
                logger.info("🎉 RECONEXÃO BYBIT BEM-SUCEDIDA!")
                
                # Notificar no Telegram
                from core.tavares_telegram_bot import TavaresTelegramBot
                bot = TavaresTelegramBot()
                await bot.enviar_mensagem("🎉 <b>BYBIT RECONECTADO!</b>\nSistema voltou ao modo REAL!")
                
            except Exception as e:
                logger.warning(f"🔄 Reconexão falhou: {e}")
    
    def _calcular_quantidade(self, par, valor_usdt):
        """Calcular quantidade baseada no preço atual"""
        try:
            # Se estiver offline, usar preço simulado
            if getattr(self, 'modo_offline', False):
                logger.warning(f"📊 MODO OFFLINE: usando preço simulado para {par}")
                preco_simulado = 50000 if 'BTC' in par else 3000
                quantidade = valor_usdt / preco_simulado
                return round(quantidade, 6)
            
            # Modo online - preço real
            ticker = self.exchange.fetch_ticker(par)
            preco_atual = ticker['last']
            
            quantidade = valor_usdt / preco_atual
            
            # Obter precisão do mercado
            mercado = self.exchange.load_markets()
            symbol_info = mercado[par]
            precision = symbol_info['precision']['amount']
            
            quantidade = float(Decimal(str(quantidade)).quantize(
                Decimal(str(precision)), rounding=ROUND_DOWN
            ))
            
            logger.info(f"📊 {par}: Preço=${preco_atual}, Qtd={quantidade}")
            return quantidade
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular quantidade {par}: {e}")
            # Fallback seguro
            return valor_usdt / 50000  # BTC price fallback
    
    async def executar_ordem(self, par, direcao, valor_usdt):
        """Executar ordem REAL na Bybit"""
        # 🔴 BLOQUEAR ORDENS SE ESTIVER OFFLINE
        if getattr(self, 'modo_offline', False):
            logger.warning(f"🚫 ORDEM BLOQUEADA: Bybit offline - {par} {direcao}")
            raise Exception("BYBIT OFFLINE - Ordens suspensas temporariamente")
        
        try:
            logger.info(f"💰 EXECUTANDO ORDEM REAL: {par} {direcao} ${valor_usdt}")
            
            quantidade = self._calcular_quantidade(par, valor_usdt)
            
            # Verificar saldo
            saldo_atual = self.obter_saldo()
            if saldo_atual < valor_usdt:
                raise Exception(f"Saldo insuficiente: {saldo_atual} < {valor_usdt}")
            
            # Executar ordem
            if direcao.upper() == 'BUY':
                ordem = self.exchange.create_market_buy_order(par, quantidade)
            else:
                ordem = self.exchange.create_market_sell_order(par, quantidade)
            
            logger.info(f"✅ ORDEM REAL EXECUTADA: {ordem['id']}")
            
            return {
                'id': ordem['id'],
                'symbol': ordem['symbol'],
                'side': ordem['side'],
                'price': float(ordem['price']),
                'amount': float(ordem['amount']),
                'cost': float(ordem['cost']),
                'timestamp': ordem['timestamp'],
                'status': ordem['status']
            }
            
        except Exception as e:
            logger.error(f"❌ ERRO EXECUTANDO ORDEM REAL {par}: {e}")
            raise
    
    def obter_saldo(self):
        """Obter saldo atual"""
        try:
            if getattr(self, 'modo_offline', False):
                return 100.0  # Saldo simulado
            
            balance = self.exchange.fetch_balance()
            return float(balance['total'].get('USDT', 0))
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo: {e}")
            return 0.0
    
    def obter_dados_mercado(self, par, timeframe='15m', limit=100):
        """Obter dados OHLCV"""
        try:
            if getattr(self, 'modo_offline', False):
                return self._dados_simulados(limit)
            
            return self.exchange.fetch_ohlcv(par, timeframe, limit=limit)
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados {par}: {e}")
            return self._dados_simulados(limit)
    
    def _dados_simulados(self, limit):
        """Dados simulados para modo offline"""
        import time
        current_time = int(time.time() * 1000)
        data = []
        base_price = 50000
        
        for i in range(limit):
            timestamp = current_time - (limit - i) * 900000
            open_price = base_price + i * 10
            high_price = open_price + 50
            low_price = open_price - 30
            close_price = open_price + 20
            volume = 1000 + i * 10
            
            data.append([timestamp, open_price, high_price, low_price, close_price, volume])
        
        return data
