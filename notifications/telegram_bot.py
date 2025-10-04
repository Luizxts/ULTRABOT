import telegram
import logging
from datetime import datetime
from core.config_manager import config

logger = logging.getLogger('TelegramBot')

class TelegramNotifier:
    def __init__(self):
        self.bot = None
        self.chat_id = config.TELEGRAM_CONFIG['chat_id']
        self.inicializar_bot()
    
    def inicializar_bot(self):
        """Inicializar bot do Telegram"""
        try:
            self.bot = telegram.Bot(token=config.TELEGRAM_CONFIG['bot_token'])
            logger.info("✅ BOT TELEGRAM INICIALIZADO")
        except Exception as e:
            logger.error(f"❌ ERRO AO INICIALIZAR BOT TELEGRAM: {e}")
            self.bot = None
    
    def enviar_mensagem(self, mensagem):
        """Enviar mensagem para o Telegram"""
        try:
            if self.bot and self.chat_id:
                self.bot.send_message(
                    chat_id=self.chat_id, 
                    text=mensagem,
                    parse_mode='Markdown'
                )
                logger.info("✅ MENSAGEM TELEGRAM ENVIADA")
                return True
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
🎪 **Ordem ID:** `{ordem.get('id', 'N/A')}`

⏰ **Horário:** `{datetime.now().strftime('%H:%M:%S')}`
        """
        self.enviar_mensagem(mensagem)
    
    def enviar_status_sistema(self, status, metricas, conexao):
        """Enviar status completo do sistema"""
        mensagem = f"""
🤖 **ULTRABOT PRO MAX - STATUS**

🟢 **Status:** `{status}`
🌐 **Conexão:** `{'✅ CONECTADO' if conexao else '❌ OFFLINE'}`
📈 **Trades:** `{metricas.get('trades', 0)}`
💰 **Lucro:** `${metricas.get('lucro', 0):.2f}`

⏰ **Atualizado:** `{datetime.now().strftime('%H:%M:%S')}`
        """
        self.enviar_mensagem(mensagem)
