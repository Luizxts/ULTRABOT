import telegram
import logging
from config import TELEGRAM_CONFIG

logger = logging.getLogger('TelegramBot')

class TelegramNotifier:
    def __init__(self):
        self.bot = None
        self.chat_id = TELEGRAM_CONFIG['chat_id']
        self.inicializar_bot()
    
    def inicializar_bot(self):
        """Inicializar bot do Telegram"""
        try:
            self.bot = telegram.Bot(token=TELEGRAM_CONFIG['bot_token'])
            logger.info("✅ BOT TELEGRAM INICIALIZADO")
        except Exception as e:
            logger.error(f"❌ ERRO AO INICIALIZAR BOT TELEGRAM: {e}")
            self.bot = None
    
    def enviar_mensagem(self, mensagem):
        """Enviar mensagem para o Telegram"""
        try:
            if self.bot and self.chat_id:
                self.bot.send_message(chat_id=self.chat_id, text=mensagem)
                logger.info("✅ MENSAGEM TELEGRAM ENVIADA")
                return True
            else:
                logger.warning("⚠️ BOT TELEGRAM NÃO CONFIGURADO")
                return False
        except Exception as e:
            logger.error(f"❌ ERRO AO ENVIAR MENSAGEM TELEGRAM: {e}")
            return False
    
    def enviar_sinal_trading(self, par, direcao, confianca, preco):
        """Enviar sinal de trading formatado"""
        mensagem = f"""
🎯 **SINAL DE TRADING DETECTADO**

**Par:** {par}
**Direção:** {direcao}
**Confiança:** {confianca}%
**Preço Atual:** ${preco:.2f}

⚠️ **EXECUTANDO EM CONTA REAL**
        """
        self.enviar_mensagem(mensagem)
    
    def enviar_alerta_erro(self, erro):
        """Enviar alerta de erro"""
        mensagem = f"""
🚨 **ERRO NO ULTRABOT**

**Descrição:** {erro}

⚠️ **VERIFICAR LOGS IMEDIATAMENTE**
        """
        self.enviar_mensagem(mensagem)

    def enviar_status_bot(self, status, performance, conexao):
        """Enviar status completo do bot"""
        mensagem = f"""
🤖 **ULTRABOT PRO MAX - STATUS**

**Status:** {status}
**Conexão Exchange:** {'✅ CONECTADO' if conexao else '❌ OFFLINE'}
**Ciclos Concluídos:** {performance['ciclos']}
**Trades Realizados:** {performance['trades']}
**Saldo Atual:** ${performance['saldo']:.2f}
**Lucro/Prejuízo:** ${performance['lucro']:.2f}

🕒 **Atualizado em tempo real**
        """
        self.enviar_mensagem(mensagem)
