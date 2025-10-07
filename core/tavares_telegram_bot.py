import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import time
import os

logger = logging.getLogger('TavaresTelegram')

class TavaresTelegramBot:
    """TAVARES A EVOLUÇÃO - Sistema completo de trading"""
    
    def __init__(self):
        # 🔥 VERIFICAÇÃO DE INSTÂNCIA ÚNICA
        self._instance_id = f"tavares_{int(time.time())}"
        logger.info(f"🤖 Inicializando TAVARES - ID: {self._instance_id}")
        
        # 🧠 Sistema Neural
        from cerebro.rede_neural_simples import CerebroNeuralSimples
        from cerebro.analise_sentimentos import AnalisadorSentimentos
        
        self.cerebro = CerebroNeuralSimples()
        self.analisador_sentimentos = AnalisadorSentimentos()
        
        # 💰 Bybit Manager
        from core.exchange_manager import BybitManager
        self.bybit = BybitManager()
        
        # 🤖 Telegram
        from core.config import config
        self.config = config
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.chat_id = config.TELEGRAM_CHAT_ID
        
        # 📊 Estado do Sistema
        self.estado = {
            'id': self._instance_id,
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
            'historico_operacoes': [],
            'bybit_status': 'ONLINE' if not self.bybit.modo_offline else 'OFFLINE'
        }
        
        logger.info("🤖 TAVARES INICIALIZADO COM SUCESSO!")
        
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
        resultado_real = operacao.get('resultado_real', {})
        
        emoji = "🟢" if resultado_real.get('side') == 'buy' else "🔴"
        seta = "📈" if sinal['direcao'] == 'BUY' else "📉"
        
        mensagem = f"""
{emoji} <b>🔥 OPERAÇÃO REAL EXECUTADA</b> {seta}

<b>Par:</b> {sinal['par']}
<b>Direção:</b> {sinal['direcao']}
<b>Confiança:</b> {sinal['confianca']:.1f}%
<b>Valor:</b> ${self.config.VALOR_POR_TRADE}

<b>ID Ordem:</b> <code>{resultado_real.get('id', 'N/A')}</code>
<b>Preço:</b> ${resultado_real.get('price', 'N/A')}
<b>Quantidade:</b> {resultado_real.get('amount', 'N/A')}

<b>Saldo Atual:</b> ${self.estado['performance']['saldo_atual']:.2f}

⏰ <i>{datetime.now().strftime('%H:%M:%S')}</i>
        """
        
        await self.enviar_mensagem(mensagem)
    
    async def executar_operacao_real(self, previsao):
        """Executar operação REAL na Bybit"""
        try:
            logger.info(f"💰 EXECUTANDO OPERAÇÃO REAL: {previsao['par']} {previsao['direcao']}")
            
            # Verificar se Bybit está online
            if self.bybit.modo_offline:
                await self.enviar_mensagem(
                    f"🚫 <b>BYBIT OFFLINE</b>\n\n"
                    f"Operação {previsao['par']} {previsao['direcao']} cancelada.\n"
                    f"💡 <i>Configure VPS para operação real</i>"
                )
                return None
            
            # Verificar saldo
            saldo_atual = self.bybit.obter_saldo()
            if saldo_atual < self.config.VALOR_POR_TRADE:
                await self.enviar_mensagem(
                    f"⚠️ <b>SALDO INSUFICIENTE</b>\n\n"
                    f"Saldo: ${saldo_atual:.2f}\n"
                    f"Necessário: ${self.config.VALOR_POR_TRADE}\n"
                    f"Operação cancelada."
                )
                return None
            
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
                await self.enviar_mensagem(
                    f"❌ <b>FALHA NA ORDEM REAL</b>\n\n"
                    f"Par: {previsao['par']}\n"
                    f"Erro: Ordem não executada"
                )
                return None
                
        except Exception as e:
            logger.error(f"❌ ERRO OPERAÇÃO REAL: {e}")
            await self.enviar_mensagem(
                f"💥 <b>ERRO NA ORDEM</b>\n\n"
                f"Par: {previsao['par']}\n"
                f"Erro: {str(e)[:100]}..."
            )
            return None
    
    async def executar_ciclo_trading(self):
        """Executar ciclo completo de trading"""
        try:
            self.estado['ciclo_atual'] += 1
            self.estado['performance']['total_ciclos'] += 1
            
            logger.info(f"🔮 CICLO {self.estado['ciclo_atual']} - TAVARES ANALISANDO...")
            
            # 🔄 ATUALIZAR STATUS BYBIT
            self.estado['bybit_status'] = 'ONLINE' if not self.bybit.modo_offline else 'OFFLINE'
            
            # 1. 📰 ANÁLISE DE SENTIMENTOS
            await self._analisar_sentimentos_mercado()
            
            # 2. 📊 COLETAR DADOS
            dados_mercado = await self._coletar_dados_reais()
            
            # 3. 🎯 PREVISÃO NEURAL
            previsoes = await self._gerar_previsoes_neurais(dados_mercado)
            
            # 4. ⚡ EXECUTAR OPERAÇÕES
            await self._executar_operacoes(previsoes)
            
            # 5. 📊 ATUALIZAR ESTADO
            self.estado['status'] = '🟢 OPERANDO'
            self.estado['ultima_atualizacao'] = datetime.now().isoformat()
            
            # 6. 📋 RELATÓRIO PERIÓDICO
            if self.estado['ciclo_atual'] % 10 == 0:
                await self.enviar_relatorio_diario()
            
        except Exception as e:
            logger.error(f"❌ ERRO NO CICLO: {e}")
            self.estado['status'] = '🔴 ERRO TEMPORÁRIO'
    
    async def _analisar_sentimentos_mercado(self):
        """Analisar sentimentos do mercado"""
        try:
            sentimento = self.analisador_sentimentos.analisar_sentimento_mercado()
            self.estado['sentimento_mercado'] = sentimento
            logger.info(f"📊 Sentimento: {sentimento.get('sentimento_geral', 'N/A')}")
        except Exception as e:
            logger.error(f"❌ Erro sentimentos: {e}")
            self.estado['sentimento_mercado'] = {
                'sentimento_geral': 'NEUTRO', 
                'score_medio': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _coletar_dados_reais(self):
        """Coletar dados do mercado"""
        try:
            dados = {}
            
            for par in self.config.PARES_MONITORADOS:
                try:
                    ohlcv = self.bybit.obter_dados_mercado(par, '15m', 50)
                    
                    if ohlcv:
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        dados[par] = {'15m': df}
                        logger.debug(f"✅ Dados coletados: {par}")
                    else:
                        logger.warning(f"⚠️ Dados vazios para {par}")
                        continue
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao coletar dados {par}: {e}")
                    continue
            
            return dados
            
        except Exception as e:
            logger.error(f"❌ Erro geral na coleta de dados: {e}")
            return {}
    
    async def _gerar_previsoes_neurais(self, dados_mercado):
        """Gerar previsões neurais"""
        previsoes = []
        
        for par in self.config.PARES_MONITORADOS:
            if par in dados_mercado:
                try:
                    # Criar dados específicos para o par
                    dados_par = {par: dados_mercado[par]}
                    
                    # Gerar previsão
                    previsao = self.cerebro.prever(dados_par)
                    previsao['par'] = par
                    
                    previsoes.append(previsao)
                    logger.info(f"🎯 {par}: {previsao['direcao']} ({previsao['confianca']:.1f}%)")
                    
                except Exception as e:
                    logger.error(f"❌ Erro na previsão {par}: {e}")
                    continue
        
        return previsoes
    
    async def _executar_operacoes(self, previsoes):
        """Executar operações baseadas nas previsões"""
        try:
            for previsao in previsoes:
                # Critério conservador para operações
                if (previsao['confianca'] >= self.config.CONFIANCA_MINIMA and 
                    previsao['direcao'] != 'HOLD'):
                    
                    if not self.bybit.modo_offline:
                        # MODO REAL - Executar ordem
                        await self.executar_operacao_real(previsao)
                    else:
                        # MODO OFFLINE - Apenas registrar sinal
                        logger.info(f"🎯 SINAL (OFFLINE): {previsao['par']} {previsao['direcao']} ({previsao['confianca']:.1f}%)")
                    
                    await asyncio.sleep(2)  # Delay entre operações
                    
        except Exception as e:
            logger.error(f"❌ Erro na execução: {e}")
    
    async def enviar_relatorio_diario(self):
        """Enviar relatório diário"""
        try:
            perf = self.estado['performance']
            sentimento = self.estado['sentimento_mercado']
            
            # Calcular win rate
            if perf['operacoes_executadas'] > 0:
                win_rate = (perf['operacoes_lucrativas'] / perf['operacoes_executadas']) * 100
            else:
                win_rate = 0
            
            status_bybit = "🟢 ONLINE" if not self.bybit.modo_offline else "🔴 OFFLINE"
            
            mensagem = f"""
📊 <b>RELATÓRIO TAVARES</b>

<b>Status Sistema:</b> {self.estado['status']}
<b>Status Bybit:</b> {status_bybit}
<b>Ciclos Executados:</b> {perf['total_ciclos']}
<b>Operações Realizadas:</b> {perf['operacoes_executadas']}
<b>Win Rate:</b> {win_rate:.1f}%
<b>Saldo Atual:</b> <b>${perf['saldo_atual']:.2f}</b>

<b>Análise de Mercado:</b>
• Sentimento: {sentimento.get('sentimento_geral', 'N/A')}
• Score: {sentimento.get('score_medio', 0):.3f}

💪 <i>Sistema ativo e monitorando</i>
            """
            
            await self.enviar_mensagem(mensagem)
            
        except Exception as e:
            logger.error(f"❌ Erro no relatório: {e}")
    
    # COMANDOS TELEGRAM
    async def comando_start(self, update, context):
        """Comando /start"""
        status_bybit = "🟢 CONECTADO" if not self.bybit.modo_offline else "🔴 OFFLINE"
        
        mensagem = f"""
🤖 <b>TAVARES A EVOLUÇÃO</b> 🚀

<b>Status Bybit:</b> {status_bybit}
<b>Modo:</b> OPERAÇÃO REAL
<b>Estratégia:</b> Neural + Análise Técnica
<b>Risco:</b> 1% por trade

<b>Comandos Disponíveis:</b>
/status - Status completo
/saldo - Saldo atual
/operacoes - Histórico
/performance - Performance
/sentimento - Análise de mercado

⚡ <i>Sistema ativo e monitorando</i>
        """
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def comando_status(self, update, context):
        """Comando /status"""
        perf = self.estado['performance']
        sentimento = self.estado['sentimento_mercado']
        
        status_bybit = "🟢 ONLINE" if not self.bybit.modo_offline else "🔴 OFFLINE"
        
        mensagem = f"""
💰 <b>STATUS TAVARES</b>

<b>Sistema:</b> {self.estado['status']}
<b>Bybit:</b> {status_bybit}
<b>Ciclos:</b> {perf['total_ciclos']}
<b>Operações:</b> {perf['operacoes_executadas']}
<b>Saldo:</b> <code>${perf['saldo_atual']:.2f}</code>

<b>Mercado:</b>
• Sentimento: {sentimento.get('sentimento_geral', 'N/A')}
• Score: {sentimento.get('score_medio', 0):.3f}

🔄 <i>Última atualização: {self.estado['ultima_atualizacao'][11:19]}</i>
        """
        
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def comando_saldo(self, update, context):
        """Comando /saldo"""
        saldo = self.bybit.obter_saldo()
        status_bybit = "🟢 ONLINE" if not self.bybit.modo_offline else "🔴 OFFLINE"
        
        mensagem = f"""
💰 <b>SALDO BYBIT</b>

<b>Status:</b> {status_bybit}
<b>Saldo Disponível:</b> <code>${saldo:.2f}</code>
<b>Valor por Trade:</b> <code>${self.config.VALOR_POR_TRADE}</code>
<b>Risco por Trade:</b> <code>{self.config.RISK_PER_TRADE*100}%</code>

💸 <i>Gestão conservadora ativa</i>
        """
        
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def comando_operacoes(self, update, context):
        """Comando /operacoes"""
        operacoes = self.estado['historico_operacoes'][-5:]
        
        if not operacoes:
            await update.message.reply_text("📭 Nenhuma operação executada ainda")
            return
        
        mensagem = "📊 <b>ÚLTIMAS OPERAÇÕES</b>\n\n"
        
        for op in reversed(operacoes):
            sinal = op['sinal']
            resultado = op.get('resultado_real', {})
            
            emoji = "🟢" if resultado.get('side') == 'buy' else "🔴"
            mensagem += f"""{emoji} <b>{sinal['par']}</b> {sinal['direcao']}
Conf: {sinal['confianca']:.1f}% | Preço: ${resultado.get('price', 'N/A')}
ID: <code>{resultado.get('id', 'N/A')}</code>
{op['timestamp'][11:19]}\n\n"""
        
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def comando_performance(self, update, context):
        """Comando /performance"""
        perf = self.estado['performance']
        
        if perf['operacoes_executadas'] > 0:
            win_rate = (perf['operacoes_lucrativas'] / perf['operacoes_executadas']) * 100
        else:
            win_rate = 0
        
        mensagem = f"""
📈 <b>PERFORMANCE TAVARES</b>

<b>Estatísticas:</b>
• Total Ciclos: {perf['total_ciclos']}
• Operações: {perf['operacoes_executadas']}
• Lucrativas: {perf['operacoes_lucrativas']}
• Win Rate: <b>{win_rate:.1f}%</b>

<b>Financeiro:</b>
• Lucro Total: ${perf['lucro_total']:.2f}
• Saldo Atual: <b>${perf['saldo_atual']:.2f}</b>

🎯 <i>Estratégia em execução</i>
        """
        
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def comando_sentimento(self, update, context):
        """Comando /sentimento"""
        sentimento = self.estado['sentimento_mercado']
        
        emoji = {
            'MUITO_POSITIVO': '🚀',
            'POSITIVO': '📈',
            'NEUTRO': '📊',
            'NEGATIVO': '📉',
            'MUITO_NEGATIVO': '🔻'
        }.get(sentimento.get('sentimento_geral', 'NEUTRO'), '📊')
        
        mensagem = f"""
🎭 <b>ANÁLISE DE SENTIMENTOS</b>

<b>Sentimento:</b> {emoji} {sentimento.get('sentimento_geral', 'N/A')}
<b>Score Médio:</b> {sentimento.get('score_medio', 0):.3f}
<b>Intensidade:</b> {sentimento.get('intensidade', 0):.3f}
<b>Notícias:</b> {sentimento.get('total_noticias', 0)}

⏰ <i>Atualizado: {sentimento.get('timestamp', 'N/A')[11:19]}</i>
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
            
            # Mensagem de inicialização
            status_bybit = "🟢 CONECTADO" if not self.bybit.modo_offline else "🔴 OFFLINE"
            
            await self.enviar_mensagem(
                f"🤖 <b>TAVARES A EVOLUÇÃO</b> 🔥\n\n"
                f"💰 <b>Status:</b> {status_bybit}\n"
                f"🎯 <b>Modo:</b> OPERAÇÃO REAL\n"
                f"⚡ <b>Estratégia:</b> Neural Avançada\n\n"
                f"🧠 <i>Sistema inicializado com sucesso</i>\n"
                f"📊 <i>Monitoramento 24/7 ativo</i>\n"
                f"🚀 <i>Pronto para operar!</i>"
            )
            
            logger.info("🤖 Bot Telegram inicializado com sucesso")
            return application
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Telegram: {e}")
            return None
    
    async def executar_continuamente(self):
        """Executar sistema continuamente"""
        logger.info("🚀 TAVARES - INICIANDO SISTEMA PRINCIPAL")
        
        # Iniciar bot Telegram
        telegram_app = await self.iniciar_telegram_bot()
        
        if telegram_app:
            await telegram_app.initialize()
            await telegram_app.start()
            await telegram_app.updater.start_polling()
        
        # Loop principal
        while True:
            try:
                await self.executar_ciclo_trading()
                await asyncio.sleep(self.config.INTERVALO_ANALISE)
                
            except Exception as e:
                logger.error(f"💥 ERRO NO LOOP PRINCIPAL: {e}")
                await asyncio.sleep(30)  # Espera antes de retry
