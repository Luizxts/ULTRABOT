import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import time

logger = logging.getLogger('TavaresTelegram')

class TavaresTelegramBot:
    """TAVARES A EVOLUÇÃO - Versão BYBIT REAL RESILIENTE"""
    
    def __init__(self):
        # 🧠 Sistema Neural
        from cerebro.rede_neural_simples import CerebroNeuralSimples
        from cerebro.analise_sentimentos import AnalisadorSentimentos
        
        self.cerebro = CerebroNeuralSimples()
        self.analisador_sentimentos = AnalisadorSentimentos()
        
        # 💰 Bybit Real - COM TRATAMENTO DE ERRO
        try:
            from core.exchange_manager import BybitManager
            self.bybit = BybitManager()
            self.exchange_ok = True
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Bybit: {e}")
            self.exchange_ok = False
            # Criar manager dummy para continuar
            self.bybit = type('DummyManager', (), {
                'obter_saldo': lambda: 100.0,
                'obter_dados_mercado': lambda *args: None,
                'executar_ordem': lambda *args: None
            })()
        
        # 🤖 Telegram
        from core.config import config
        self.config = config
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.chat_id = config.TELEGRAM_CHAT_ID
        
        # 📊 Estado do Bot
        self.estado = {
            'status': '🟢 INICIANDO',
            'modo': 'BYBIT REAL 💰',
            'ciclo_atual': 0,
            'ultima_atualizacao': datetime.now().isoformat(),
            'performance': {
                'total_ciclos': 0,
                'operacoes_executadas': 0,
                'operacoes_lucrativas': 0,
                'lucro_total': 0.0,
                'saldo_atual': self.bybit.obter_saldo() if self.exchange_ok else 100.0,
                'win_rate': 0.0
            },
            'sentimento_mercado': {},
            'historico_operacoes': [],
            'exchange_status': '✅ CONECTADO' if self.exchange_ok else '⚠️ MODO SIMULAÇÃO'
        }
        
        logger.info("🤖 TAVARES TELEGRAM BYBIT REAL - INICIALIZADO!")
        
    async def enviar_mensagem(self, texto):
        """Enviar mensagem para o Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=texto,
                parse_mode='HTML'
            )
            logger.info(f"📤 Mensagem enviada: {texto[:50]}...")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem Telegram: {e}")
    
    async def executar_ciclo_trading_real(self):
        """Executar ciclo de trading REAL com resiliência"""
        try:
            self.estado['ciclo_atual'] += 1
            self.estado['performance']['total_ciclos'] += 1
            
            logger.info(f"🔮 CICLO {self.estado['ciclo_atual']} - TAVARES ANALISANDO...")
            
            # 1. 📰 ANÁLISE DE SENTIMENTOS
            await self._analisar_sentimentos_mercado()
            
            # 2. 📊 COLETAR DADOS (com fallback)
            dados_mercado = await self._coletar_dados_reais()
            
            # 3. 🎯 PREVISÃO NEURAL
            previsoes = await self._gerar_previsoes_neurais(dados_mercado)
            
            # 4. ⚡ EXECUTAR OPERAÇÕES REAIS (apenas se exchange estiver OK)
            if self.exchange_ok:
                await self._executar_operacoes_reais(previsoes)
            else:
                logger.warning("⚠️ Exchange não disponível - modo simulação")
            
            self.estado['status'] = '🟢 OPERANDO' if self.exchange_ok else '🟡 SIMULAÇÃO'
            self.estado['ultima_atualizacao'] = datetime.now().isoformat()
            
            # 5. 📊 RELATÓRIO PERIÓDICO
            if self.estado['ciclo_atual'] % 10 == 0:
                await self.enviar_relatorio_diario()
            
        except Exception as e:
            logger.error(f"❌ ERRO NO CICLO: {e}")
            self.estado['status'] = '🔴 ERRO TEMPORÁRIO'
    
    async def _coletar_dados_reais(self):
        """Coletar dados com resiliência"""
        try:
            dados = {}
            
            for par in self.config.PARES_MONITORADOS:
                try:
                    ohlcv = self.bybit.obter_dados_mercado(par, '15m', 50)  # Menos dados para ser mais rápido
                    
                    if ohlcv:
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        dados[par] = {'15m': df}
                    else:
                        # Dados simulados se API falhar
                        logger.warning(f"⚠️ Usando dados simulados para {par}")
                        dados[par] = self._gerar_dados_simulados()
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro dados {par}: {e}")
                    dados[par] = self._gerar_dados_simulados()
                    continue
            
            return dados
            
        except Exception as e:
            logger.error(f"❌ Erro geral coleta dados: {e}")
            return self._gerar_dados_simulados_geral()
    
    def _gerar_dados_simulados(self):
        """Gerar dados simulados para um par"""
        import numpy as np
        dates = pd.date_range(end=datetime.now(), periods=50, freq='15min')
        base_price = np.random.uniform(100, 50000)
        
        prices = [base_price]
        for i in range(1, 50):
            change = np.random.normal(0, 0.02)  # 2% volatility
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': [np.random.uniform(1000, 10000) for _ in prices]
        })
        
        return {'15m': df}
    
    def _gerar_dados_simulados_geral(self):
        """Gerar dados simulados para todos os pares"""
        dados = {}
        for par in self.config.PARES_MONITORADOS:
            dados[par] = self._gerar_dados_simulados()
        return dados

    # ... (mantém todos os outros métodos do Telegram)
    
    async def comando_status(self, update, context):
        """Comando /status atualizado"""
        perf = self.estado['performance']
        
        mensagem = f"""
💰 <b>STATUS TAVARES BYBIT</b>

<b>Exchange:</b> {self.estado['exchange_status']}
<b>Status:</b> {self.estado['status']}
<b>Ciclos:</b> {perf['total_ciclos']}
<b>Operações:</b> {perf['operacoes_executadas']}
<b>Saldo:</b> <code>${perf['saldo_atual']:.2f}</code>

<b>Mercado:</b>
• {self.estado['sentimento_mercado'].get('sentimento_geral', 'N/A')}

🔄 <i>Sistema resiliente ativo</i>
        """
        
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def iniciar_telegram_bot(self):
        """Iniciar bot do Telegram com mensagem adaptada"""
        try:
            application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
            
            # Comandos
            application.add_handler(CommandHandler("start", self.comando_start))
            application.add_handler(CommandHandler("status", self.comando_status))
            application.add_handler(CommandHandler("operacoes", self.comando_operacoes))
            application.add_handler(CommandHandler("performance", self.comando_performance))
            application.add_handler(CommandHandler("sentimento", self.comando_sentimento))
            application.add_handler(CommandHandler("saldo", self.comando_saldo))
            
            # Mensagem de boas-vindas adaptada
            status_msg = "✅ BYBIT REAL" if self.exchange_ok else "⚠️ MODO SIMULAÇÃO"
            
            await self.enviar_mensagem(
                f"🤖 <b>TAVARES A EVOLUÇÃO</b> 🔥\n\n"
                f"💰 <b>Modo:</b> {status_msg}\n"
                f"🎯 <b>Estratégia:</b> Neural Resiliente\n"
                f"⚡ <b>Status:</b> {self.estado['status']}\n\n"
                f"🧠 <i>Sistema adaptativo ativado</i>\n"
                f"📊 <i>Monitoramento ativo</i>\n"
                f"🚀 <i>Pronto para operar!</i>"
            )
            
            logger.info("🤖 Bot Telegram inicializado")
            return application
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Telegram: {e}")
            return None
    
    async def executar_continuamente(self):
        """Executar sistema continuamente com resiliência"""
        logger.info("🚀 TAVARES BYBIT - INICIANDO SISTEMA RESILIENTE")
        
        # Iniciar bot Telegram
        telegram_app = await self.iniciar_telegram_bot()
        
        if telegram_app:
            await telegram_app.initialize()
            await telegram_app.start()
            await telegram_app.updater.start_polling()
        
        # Loop principal resiliente
        while True:
            try:
                await self.executar_ciclo_trading_real()
                await asyncio.sleep(self.config.INTERVALO_ANALISE)
                
            except Exception as e:
                logger.error(f"💥 ERRO CRÍTICO: {e}")
                await asyncio.sleep(30)  # Espera menor para recuperação rápida
