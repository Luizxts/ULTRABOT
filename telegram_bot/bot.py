import logging
import asyncio
import os
from telegram import Bot

# ✅ CONFIGURAÇÃO SEGURA
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

class TelegramBot:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.bot = None
        self.logger = logging.getLogger(__name__)
        self.initialize_bot()
    
    def initialize_bot(self):
        """Inicializa o bot do Telegram"""
        try:
            if not self.token or self.token == '8444269740:AAE2dlSXozV4cIGNMMs72APIDcrYBvIq31M':
                self.logger.warning("❌ Token do Telegram não configurado")
                return
                
            self.bot = Bot(token=self.token)
            self.logger.info("✅ Telegram bot inicializado com sucesso")
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Telegram: {e}")
    
    def send_message(self, message):
        """Envia mensagem para o Telegram (CORRIGIDO)"""
        try:
            if not self.bot or not self.chat_id:
                return
                
            # ✅ CORREÇÃO: Cria novo event loop se necessário
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # ✅ ENVIO SÍNCRONO CORRETO
            loop.run_until_complete(self._async_send_message(message))
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar mensagem Telegram: {e}")
    
    async def _async_send_message(self, message):
        """Envia mensagem assíncrona"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            self.logger.info("📱 Mensagem Telegram enviada com sucesso")
        except Exception as e:
            self.logger.error(f"❌ Erro no envio async: {e}")
