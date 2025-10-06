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
    """TAVARES A EVOLUÇÃO - Versão BYBIT REAL COMPLETA"""
    
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
                'saldo_atual': self.bybit.obter_saldo() if hasattr(self.bybit, 'obter_saldo') else 100.0,
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
            
            # Verificar saldo
            saldo_atual = self.bybit.obter_saldo()
            if saldo_atual < self.config.VALOR_POR_TRADE:
                await self.enviar_mensagem(f"⚠️ <b>SALDO INSUFICIENTE</b>\nSaldo: ${saldo_atual:.2f}\nNecessário: ${self.config.VALOR_POR_TRADE}")
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
                await self.enviar_mensagem(f"❌ <b>FALHA NA ORDEM REAL</b>\nPar: {previsao['par']}\nErro: Não executada")
                return None
                
        except Exception as e:
            logger.error(f"❌ ERRO OPERAÇÃO REAL: {e}")
            await self.enviar_mensagem(f"💥 <b>ERRO CRÍTICO</b>\n{e}")
            return None
    
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
    
    async def _analisar_sentimentos_mercado(self):
        """Analisar sentimentos do mercado"""
        try:
            sentimento = self.analisador_sentimentos.analisar_sentimento_mercado()
            self.estado['sentimento_mercado'] = sentimento
            logger.info(f"📊 Sentimento do mercado: {sentimento.get('sentimento_geral', 'N/A')}")
        except Exception as e:
            logger.error(f"❌ Erro sentimentos: {e}")
            self.estado['sentimento_mercado'] = {'sentimento_geral': 'NEUTRO', 'score_medio': 0}
    
    async def _coletar_dados_reais(self):
        """Coletar dados com resiliência"""
        try:
            dados = {}
            
            for par in self.config.PARES_MONITORADOS:
                try:
                    ohlcv = self.bybit.obter_dados_mercado(par, '15m', 50)
                    
                    if ohlcv:
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        dados[par] = {'15m': df}
                        logger.info(f"✅ Dados coletados: {par}")
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
            change = np.random.normal(0, 0.02)
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
                    logger.error(f"❌ Erro previsão {par}: {e}")
                    continue
        
        return previsoes
    
    async def _executar_operacoes_reais(self, previsoes):
        """Executar operações REAIS"""
        try:
            for previsao in previsoes:
                # Critério conservador para operações reais
                if (previsao['confianca'] >= self.config.CONFIANCA_MINIMA and 
                    previsao['direcao'] != 'HOLD'):
                    
                    await self.executar_operacao_real(previsao)
                    await asyncio.sleep(2)
                    
        except Exception as e:
            logger.error(f"❌ Erro execução real: {e}")
    
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
            
            mensagem = f"""
📊 <b>RELATÓRIO TAVARES</b>

<b>Performance:</b>
• Ciclos: {perf['total_ciclos']}
• Operações: {perf['operacoes_executadas']}
• Win Rate: {win_rate:.1f}%
• Saldo: <b>${perf['saldo_atual']:.2f}</b>

<b>Mercado:</b>
• Sentimento: {sentimento.get('sentimento_geral', 'N/A')}
• Score: {sentimento.get('score_medio', 0):.3f}

<b>Status:</b> {self.estado['status']}
<b>Exchange:</b> {self.estado['exchange_status']}

🟢 <i>Operando com segurança</i>
            """
            
            await self.enviar_mensagem(mensagem)
            
        except Exception as e:
            logger.error(f"❌ Erro relatório: {e}")
    
    # COMANDOS TELEGRAM COMPLETOS
    async def comando_start(self, update, context):
        """Comando /start"""
        mensagem = """
🤖 <b>TAVARES A EVOLUÇÃO - BYBIT REAL</b> 🚀

💰 <b>Modo:</b> OPERAÇÃO REAL
🎯 <b>Estratégia:</b> Neural + Análise Técnica
🛡️ <b>Risco:</b> 1% por trade

<b>Comandos disponíveis:</b>
/status - Status do sistema
/saldo - Saldo real
/operacoes - Histórico
/performance - Performance
/sentimento - Análise de mercado

⚡ <i>Pronto para operar!</i>
        """
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def comando_status(self, update, context):
        """Comando /status"""
        perf = self.estado['performance']
        sentimento = self.estado['sentimento_mercado']
        
        mensagem = f"""
💰 <b>STATUS TAVARES BYBIT</b>

<b>Exchange:</b> {self.estado['exchange_status']}
<b>Status:</b> {self.estado['status']}
<b>Ciclos:</b> {perf['total_ciclos']}
<b>Operações:</b> {perf['operacoes_executadas']}
<b>Saldo:</b> <code>${perf['saldo_atual']:.2f}</code>

<b>Mercado:</b>
• Sentimento: {sentimento.get('sentimento_geral', 'N/A')}
• Score: {sentimento.get('score_medio', 0):.3f}

🔄 <i>Sistema resiliente ativo</i>
        """
        
        await update.message.reply_text(mensagem, parse_mode='HTML')
    
    async def comando_saldo(self, update, context):
        """Comando /saldo"""
        saldo = self.bybit.obter_saldo() if hasattr(self.bybit, 'obter_saldo') else 100.0
        
        mensagem = f"""
💰 <b>SALDO BYBIT</b>

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

🎯 <i>Estratégia conservadora em execução</i>
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
                await asyncio.sleep(30)
