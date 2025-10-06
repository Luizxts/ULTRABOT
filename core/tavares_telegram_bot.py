import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import time
import ccxt

logger = logging.getLogger('TavaresTelegram')

class TavaresTelegramBot:
    """TAVARES A EVOLUÇÃO - Versão Telegram COM BYBIT REAL"""
    
    def __init__(self):
        # 🧠 Sistema Neural
        from cerebro.rede_neural_leve import CerebroNeuralLeve
        from cerebro.analise_sentimentos import AnalisadorSentimentos
        
        self.cerebro = CerebroNeuralLeve()
        self.analisador_sentimentos = AnalisadorSentimentos()
        
        # 💰 Bybit Real
        from core.exchange_manager import BybitManager
        self.bybit = BybitManager()
        
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
                'saldo_atual': self.bybit.obter_saldo(),
                'win_rate': 0.0
            },
            'sentimento_mercado': {},
            'historico_operacoes': []
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
    
    async def enviar_operacao_real(self, operacao):
        """Enviar notificação de operação REAL"""
        sinal = operacao['sinal']
        resultado = operacao.get('resultado', {})
        
        emoji = "🟢" if resultado.get('sucesso', True) else "🔴"
        seta = "📈" if sinal['direcao'] == 'BUY' else "📉"
        
        mensagem = f"""
{emoji} <b>🔥 OPERAÇÃO REAL EXECUTADA</b> {seta}

<b>Par:</b> {sinal['par']}
<b>Direção:</b> {sinal['direcao']}
<b>Confiança:</b> {sinal['confianca_neural']:.1f}%
<b>Valor:</b> ${self.config.VALOR_POR_TRADE}

<b>ID Ordem:</b> {operacao.get('id_ordem', 'N/A')}
<b>Preço Execução:</b> {operacao.get('preco_execucao', 'N/A')}

<b>Saldo Atual:</b> ${self.estado['performance']['saldo_atual']:.2f}

⏰ <i>{datetime.now().strftime('%H:%M:%S')}</i>
        """
        
        await self.enviar_mensagem(mensagem)
    
    async def executar_operacao_real(self, previsao):
        """Executar operação REAL na Bybit"""
        try:
            logger.info(f"💰 EXECUTANDO OPERAÇÃO REAL: {previsao['par']} {previsao['direcao']}")
            
            # Executar ordem na Bybit
            resultado_ordem = await self.bybit.executar_ordem(
                previsao['par'], 
                previsao['direcao'], 
                self.config.VALOR_POR_TRADE
            )
            
            if resultado_ordem:
                # Registrar operação
                operacao = {
                    'id': f"TAVR{int(time.time())}",
                    'sinal': previsao,
                    'resultado_real': resultado_ordem,
                    'timestamp': datetime.now().isoformat(),
                    'tipo': 'REAL'
                }
                
                self.estado['historico_operacoes'].append(operacao)
                self.estado['performance']['operacoes_executadas'] += 1
                
                # Atualizar saldo
                self.estado['performance']['saldo_atual'] = self.bybit.obter_saldo()
                
                # Enviar notificação
                await self.enviar_operacao_real(operacao)
                
                return operacao
            else:
                await self.enviar_mensagem(f"❌ <b>FALHA NA ORDEM REAL</b>\nPar: {previsao['par']}\nErro: Não executada")
                return None
                
        except Exception as e:
            logger.error(f"❌ ERRO OPERAÇÃO REAL: {e}")
            await self.enviar_mensagem(f"💥 <b>ERRO CRÍTICO</b>\n{e}")
            return None
    
    async def executar_ciclo_trading_real(self):
        """Executar ciclo de trading REAL"""
        try:
            self.estado['ciclo_atual'] += 1
            self.estado['performance']['total_ciclos'] += 1
            
            logger.info(f"🔮 CICLO {self.estado['ciclo_atual']} - TAVARES ANALISANDO MERCADO REAL...")
            
            # 1. 📰 ANÁLISE DE SENTIMENTOS
            await self._analisar_sentimentos_mercado()
            
            # 2. 📊 COLETAR DADOS REAIS
            dados_mercado = await self._coletar_dados_reais()
            
            # 3. 🎯 PREVISÃO NEURAL
            previsoes = await self._gerar_previsoes_neurais(dados_mercado)
            
            # 4. ⚡ EXECUTAR OPERAÇÕES REAIS
            await self._executar_operacoes_reais(previsoes)
            
            self.estado['status'] = '🟢 OPERANDO REAL'
            self.estado['ultima_atualizacao'] = datetime.now().isoformat()
            
            # 5. 📊 RELATÓRIO A CADA 10 CICLOS
            if self.estado['ciclo_atual'] % 10 == 0:
                await self.enviar_relatorio_diario()
            
        except Exception as e:
            logger.error(f"❌ ERRO NO CICLO REAL: {e}")
            self.estado['status'] = '🔴 ERRO TEMPORÁRIO'
            await self.enviar_mensagem(f"⚠️ <b>Erro no ciclo REAL:</b> {str(e)}")
    
    async def _coletar_dados_reais(self):
        """Coletar dados REAIS da Bybit"""
        try:
            dados = {}
            
            for par in self.config.PARES_MONITORADOS:
                try:
                    # Buscar dados OHLCV reais
                    ohlcv = self.bybit.exchange.fetch_ohlcv(par, '15m', limit=100)
                    
                    if ohlcv:
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        dados[par] = {'15m': df}
                        logger.info(f"✅ Dados reais coletados: {par}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao coletar dados {par}: {e}")
                    continue
            
            return dados
            
        except Exception as e:
            logger.error(f"❌ Erro coleta dados reais: {e}")
            return {}
    
    async def _executar_operacoes_reais(self, previsoes):
        """Executar operações REAIS"""
        try:
            for previsao in previsoes:
                # Critério mais conservador para operações reais
                if previsao['confianca_neural'] > 70:  # 70% de confiança mínima
                    await self.executar_operacao_real(previsao)
                    await asyncio.sleep(1)  # Delay entre operações
                    
        except Exception as e:
            logger.error(f"❌ Erro execução real: {e}")
    
    # ... (mantém todos os outros métodos de comando do Telegram)
    
    async def comando_status(self, update, context):
        """Comando /status - Atualizado para dados reais"""
        perf = self.estado['performance']
        sentimento = self.estado['sentimento_mercado']
        
        # Atualizar saldo real
        saldo_real = self.bybit.obter_saldo()
        self.estado['performance']['saldo_atual'] = saldo_real
        
        mensagem = f"""
💰 <b>STATUS TAVARES BYBIT REAL</b>

<b>Performance REAL:</b>
• Operações: {perf['operacoes_executadas']}
• Win Rate: {perf['win_rate']:.1f}%
• Saldo REAL: <b>${saldo_real:.2f}</b>
• Lucro Total: ${perf['lucro_total']:.2f}

<b>Mercado:</b>
• Sentimento: {sentimento.get('sentimento_geral', 'N/A')}
• Score: {sentimento.get('score_medio', 0):.3f}

<b>Sistema:</b>
• Status: {self.estado['status']}
• Ciclos: {self.estado['ciclo_atual']}
• Modo: <b>BYBIT REAL 💰</b>

🟢 <i>Operando com dinheiro real</i>
        """
        
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def comando_saldo(self, update, context):
        """Comando /saldo - Ver saldo real"""
        saldo = self.bybit.obter_saldo()
        
        mensagem = f"""
💰 <b>SALDO BYBIT REAL</b>

<b>Saldo Disponível:</b> <code>${saldo:.2f}</code>
<b>Valor por Trade:</b> <code>${self.config.VALOR_POR_TRADE}</code>
<b>Risco por Trade:</b> <code>{self.config.RISK_PER_TRADE*100}%</code>

💸 <i>Gestão conservadora ativa</i>
        """
        
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def iniciar_telegram_bot(self):
        """Iniciar bot do Telegram"""
        try:
            application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
            
            # Comandos
            application.add_handler(CommandHandler("start", self.comando_start))
            application.add_handler(CommandHandler("status", self.comando_status))
            application.add_handler(CommandHandler("operacoes", self.comando_operacoes))
            application.add_handler(CommandHandler("performance", self.comando_performance))
            application.add_handler(CommandHandler("sentimento", self.comando_sentimento))
            application.add_handler(CommandHandler("saldo", self.comando_saldo))
            
            # Mensagem de boas-vindas REAL
            saldo_inicial = self.bybit.obter_saldo()
            await self.enviar_mensagem(
                f"🤖 <b>TAVARES A EVOLUÇÃO - BYBIT REAL</b> 🔥\n\n"
                f"💰 <b>Saldo Inicial:</b> ${saldo_inicial:.2f}\n"
                f"🎯 <b>Modo:</b> OPERAÇÃO REAL\n"
                f"⚡ <b>Valor por Trade:</b> ${self.config.VALOR_POR_TRADE}\n"
                f"🛡️ <b>Risco:</b> {self.config.RISK_PER_TRADE*100}%\n\n"
                f"🧠 <i>Sistema neural real ativado</i>\n"
                f"📊 <i>Monitoramento 24/7</i>\n"
                f"🚀 <i>Pronto para operar!</i>"
            )
            
            logger.info("🤖 Bot Telegram REAL inicializado")
            return application
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Telegram: {e}")
            return None
    
    async def executar_continuamente(self):
        """Executar sistema continuamente"""
        logger.info("🚀 TAVARES BYBIT REAL - INICIANDO SISTEMA")
        
        # Iniciar bot Telegram
        telegram_app = await self.iniciar_telegram_bot()
        
        if telegram_app:
            await telegram_app.initialize()
            await telegram_app.start()
            await telegram_app.updater.start_polling()
        
        # Loop principal de trading REAL
        while True:
            try:
                await self.executar_ciclo_trading_real()
                await asyncio.sleep(self.config.INTERVALO_ANALISE)
                
            except Exception as e:
                logger.error(f"💥 ERRO CRÍTICO REAL: {e}")
                await asyncio.sleep(60)
