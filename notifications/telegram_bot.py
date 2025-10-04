import telegram
import logging
import asyncio
from datetime import datetime
from core.config_manager import config

logger = logging.getLogger('TelegramBot')

class TelegramNotifier:
    def __init__(self):
        self.bot = None
        self.chat_id = config.TELEGRAM_CONFIG['chat_id']
        self.inicializar_bot()
    
    def inicializar_bot(self):
        """Inicializar bot do Telegram de forma robusta"""
        try:
            self.bot = telegram.Bot(token=config.TELEGRAM_CONFIG['bot_token'])
            logger.info("✅ BOT TELEGRAM INICIALIZADO")
        except Exception as e:
            logger.error(f"❌ ERRO AO INICIALIZAR BOT TELEGRAM: {e}")
            self.bot = None
    
    def enviar_mensagem(self, mensagem):
        """Enviar mensagem para o Telegram de forma síncrona"""
        try:
            if self.bot and self.chat_id:
                # Criar loop assíncrono para execução síncrona
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    loop.run_until_complete(
                        self.bot.send_message(
                            chat_id=self.chat_id, 
                            text=mensagem,
                            parse_mode='Markdown'
                        )
                    )
                    logger.info("✅ MENSAGEM TELEGRAM ENVIADA")
                    return True
                finally:
                    loop.close()
                    
            else:
                logger.warning("⚠️ BOT TELEGRAM NÃO CONFIGURADO")
                return False
        except Exception as e:
            logger.error(f"❌ ERRO AO ENVIAR MENSAGEM TELEGRAM: {e}")
            return False
    
    def enviar_sinal_trading(self, sinal):
        """Enviar sinal de trading formatado"""
        emoji = "🟢" if sinal['direcao'] == 'BUY' else "🔴"
        
        mensagem = f"""
{emoji} **SINAL DE TRADING DETECTADO**

🎯 **Par:** `{sinal['par']}`
📈 **Direção:** `{sinal['direcao']}`
🎪 **Confiança:** `{sinal['confianca']:.1f}%`
💰 **Preço:** `${sinal['preco']:.4f}`
📊 **Estratégia:** `{sinal.get('estrategia', 'IA')}`
⚡ **Tamanho:** `${sinal.get('tamanho_posicao', 0):.2f}`

🛡️ **Proteções:**
├─ Stop Loss: `${sinal.get('stop_loss', 0):.4f}`
├─ Take Profit: `${sinal.get('take_profit', 0):.4f}`
└─ Risk/Reward: `{sinal.get('risk_reward_ratio', 0):.2f}`

⚠️ **EXECUTANDO EM CONTA REAL**
        """
        self.enviar_mensagem(mensagem)
    
    def enviar_execucao_trade(self, trade, ordem):
        """Enviar confirmação de execução de trade"""
        mensagem = f"""
✅ **TRADE EXECUTADO COM SUCESSO**

🎯 **Par:** `{trade['par']}`
📈 **Direção:** `{trade['direcao']}`
💰 **Preço Entrada:** `${trade['preco']:.4f}`
📊 **Quantidade:** `{ordem.get('amount', 0):.6f}`
🎪 **Ordem ID:** `{ordem.get('id', 'N/A')}`

⏰ **Horário:** `{datetime.now().strftime('%H:%M:%S')}`

🛡️ **Gerenciamento de Risco Ativo**
        """
        self.enviar_mensagem(mensagem)
    
    def enviar_fechamento_trade(self, trade, resultado):
        """Enviar notificação de fechamento de trade"""
        emoji = "💰" if resultado['lucro_percent'] > 0 else "📉"
        cor = "lucro" if resultado['lucro_percent'] > 0 else "prejuízo"
        
        mensagem = f"""
{emoji} **TRADE FECHADO - {cor.upper()}**

🎯 **Par:** `{trade['par']}`
📈 **Direção:** `{trade['direcao']}`
💰 **Resultado:** `{resultado['lucro_percent']:.2f}%`
💵 **Valor:** `${resultado['lucro_absoluto']:.2f}`
🎪 **Motivo:** `{resultado.get('motivo', 'MANUAL')}`

📊 **Performance:**
├─ Preço Entrada: `${trade['preco']:.4f}`
├─ Preço Saída: `${resultado.get('preco_saida', 0):.4f}`
└─ Duração: `{resultado.get('duracao', 'N/A')}`

⏰ **Horário:** `{datetime.now().strftime('%H:%M:%S')}`
        """
        self.enviar_mensagem(mensagem)
    
    def enviar_alerta_risco(self, tipo, detalhes):
        """Enviar alertas de risco"""
        mensagem = f"""
🚨 **ALERTA DE RISCO - {tipo}**

📊 **Detalhes:** {detalhes}

⚠️ **AÇÕES TOMADAS:**
├─ Verificar posições abertas
├─ Revisar limites de risco
└─ Monitorar mercado atentamente

⏰ **Horário:** `{datetime.now().strftime('%H:%M:%S')}`
        """
        self.enviar_mensagem(mensagem)
    
    def enviar_status_sistema(self, status, metricas, conexao):
        """Enviar status completo do sistema"""
        mensagem = f"""
🤖 **ULTRABOT PRO MAX - STATUS SISTEMA**

🟢 **Status:** `{status}`
🌐 **Conexão Exchange:** `{'✅ CONECTADO' if conexao else '❌ OFFLINE'}`
📈 **Performance:**
├─ Ciclos: `{metricas.get('ciclos', 0)}`
├─ Trades: `{metricas.get('trades', 0)}`
├─ Win Rate: `{metricas.get('win_rate', 0):.1f}%`
├─ Lucro Total: `${metricas.get('lucro_total', 0):.2f}`
└─ Profit Factor: `{metricas.get('profit_factor', 0):.2f}`

🛡️ **Proteções:**
├─ Trades Abertos: `{metricas.get('trades_abertos', 0)}`
├─ Drawdown: `{metricas.get('drawdown', 0):.2f}%`
└─ Loss Diário: `{metricas.get('loss_diario', 0):.2f}%`

⏰ **Atualizado:** `{datetime.now().strftime('%H:%M:%S')}`
        """
        self.enviar_mensagem(mensagem)
    
    def enviar_erro_critico(self, erro, contexto):
        """Enviar alerta de erro crítico"""
        mensagem = f"""
🔥 **ERRO CRÍTICO NO SISTEMA**

❌ **Erro:** `{str(erro)}`
📋 **Contexto:** `{contexto}`
🚨 **Severidade:** `ALTA`

⚠️ **AÇÕES RECOMENDADAS:**
├─ Verificar logs imediatamente
├─ Monitorar posições abertas
├─ Verificar conexões
└─ Contatar suporte se necessário

⏰ **Horário:** `{datetime.now().strftime('%H:%M:%S')}`
        """
        self.enviar_mensagem(mensagem)
