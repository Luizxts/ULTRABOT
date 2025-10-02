import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import asyncio
import html
import json

try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    TELEGRAM_BOT_TOKEN = "8444269740:AAE2dlSXozV4cIGNMMs72APIDcrYBvIq31M"
    TELEGRAM_CHAT_ID = "-4977542145"

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.updater = None
        self.running = False
        
    async def initialize(self):
        """Inicializa o bot do Telegram"""
        try:
            if not self.token:
                logger.warning("⚠️ Token do Telegram não configurado")
                return False
            
            # Configuração CORRETA do Updater
            self.updater = Updater(self.token, use_context=True)
            
            # Configurar handlers
            self.setup_handlers()
            
            # Iniciar polling
            self.updater.start_polling()
            self.running = True
            
            logger.info("✅ Telegram bot inicializado com sucesso")
            
            # Enviar mensagem de inicialização
            await self.send_message(
                self.chat_id, 
                "🤖 *ULTRABOT PRO INICIADO* 🚀\n"
                "Modo: SIMULATION 🎮\n"
                "Pronto para operar!\n"
                "Use /status para verificar o estado atual."
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Telegram: {e}")
            self.running = False
            return False
    
    def setup_handlers(self):
        """Configura os handlers de comandos"""
        if not self.updater:
            return
            
        dispatcher = self.updater.dispatcher
        
        # Comando /start
        def start(update: Update, context: CallbackContext):
            user = update.effective_user
            update.message.reply_text(
                f"🤖 OLÁ {user.first_name}!\n"
                f"*ULTRABOT PRO ATIVO*\n"
                f"Modo: SIMULATION 🎮\n"
                f"Saldo: $1000.00\n\n"
                f"*Comandos disponíveis:*\n"
                f"/status - Status atual\n"
                f"/balance - Saldos\n"
                f"/history - Últimos trades\n"
                f"/notifications - Ver notificações\n"
                f"/stats - Estatísticas do dia",
                parse_mode='Markdown'
            )
        
        # Comando /status
        def status(update: Update, context: CallbackContext):
            try:
                from trader.core import UltraBot
                bot = UltraBot()
                status_info = bot.get_status()
                
                status_emoji = "✅" if status_info['running'] else "⏹️"
                profit_emoji = "📈" if status_info['profit_today'] >= 0 else "📉"
                
                message = (
                    f"*📊 STATUS ULTRABOT* {status_emoji}\n"
                    f"Estado: {'RODANDO 🚀' if status_info['running'] else 'PARADO ⏹️'}\n"
                    f"Modo: {status_info['mode']}\n"
                    f"Saldo: ${status_info['balance']:.2f}\n"
                    f"Disponível: ${status_info['available_balance']:.2f}\n"
                    f"Trades Hoje: {status_info['trades_today']}\n"
                    f"W/L: {status_info['wins_today']}/{status_info['losses_today']}\n"
                    f"Lucro: {profit_emoji} ${status_info['profit_today']:.2f}\n"
                    f"Win Rate: {status_info['win_rate']}%\n"
                    f"Próximo trade: {status_info['next_trade_in']}\n"
                    f"Notificações: {status_info['notifications_count']} não lidas"
                )
                
                update.message.reply_text(message, parse_mode='Markdown')
            except Exception as e:
                update.message.reply_text(f"❌ Erro ao obter status: {e}")
        
        # Comando /balance
        def balance(update: Update, context: CallbackContext):
            try:
                from trader.bybit_analyser import BybitAnalyser
                import asyncio
                
                async def get_balance():
                    analyser = BybitAnalyser()
                    return await analyser.get_balance()
                
                real_balance = asyncio.run(get_balance())
                
                message = (
                    f"*💰 SALDO ATUAL*\n"
                    f"Bybit Real: ${real_balance:.2f}\n"
                    f"Bot Simulado: $1000.00\n"
                    f"🔧 Modo: SIMULATION\n"
                    f"💡 Discrepância: ${abs(real_balance - 1000.00):.2f}"
                )
                
                update.message.reply_text(message, parse_mode='Markdown')
            except Exception as e:
                update.message.reply_text(f"❌ Erro ao obter saldo: {e}")
        
        # Comando /history
        def history(update: Update, context: CallbackContext):
            try:
                from trader.core import UltraBot
                bot = UltraBot()
                history = bot.get_trading_history(10)  # Últimos 10 trades
                
                if not history:
                    update.message.reply_text("📭 Nenhum trade registrado ainda.")
                    return
                
                message = "*📈 ÚLTIMOS TRADES*\n\n"
                for trade in reversed(history[-10:]):  # Mostra do mais recente
                    emoji = "✅" if trade['type'] == 'WIN' else "❌"
                    profit = trade['profit_loss']
                    profit_str = f"+${profit:.2f}" if profit > 0 else f"-${abs(profit):.2f}"
                    time = trade['timestamp'][11:16]  # Apenas hora:minuto
                    
                    message += f"{emoji} {time} | {profit_str} | ${trade['amount']:.2f}\n"
                
                update.message.reply_text(message, parse_mode='Markdown')
            except Exception as e:
                update.message.reply_text(f"❌ Erro ao obter histórico: {e}")
        
        # Comando /notifications
        def notifications(update: Update, context: CallbackContext):
            try:
                from trader.core import UltraBot
                bot = UltraBot()
                notifications = bot.get_notifications(True)  # Apenas não lidas
                
                if not notifications:
                    update.message.reply_text("✅ Nenhuma notificação não lida.")
                    return
                
                message = "*🔔 NOTIFICAÇÕES*\n\n"
                for notif in notifications[:10]:  # Máximo 10 notificações
                    time = notif['timestamp'][11:16]
                    level_emoji = {
                        'info': 'ℹ️',
                        'warning': '⚠️',
                        'success': '✅',
                        'error': '❌'
                    }.get(notif['level'], '📢')
                    
                    message += f"{level_emoji} {time} | {notif['message']}\n"
                
                # Marcar como lidas
                for notif in notifications:
                    bot.mark_notification_read(notif['id'])
                
                update.message.reply_text(message, parse_mode='Markdown')
            except Exception as e:
                update.message.reply_text(f"❌ Erro ao obter notificações: {e}")
        
        # Comando /stats
        def stats(update: Update, context: CallbackContext):
            try:
                from trader.core import UltraBot
                bot = UltraBot()
                daily_stats = bot.get_daily_stats()
                status_info = bot.get_status()
                
                profit_emoji = "📈" if daily_stats['profit'] >= 0 else "📉"
                
                message = (
                    f"*📊 ESTATÍSTICAS DO DIA*\n"
                    f"Data: {daily_stats['date']}\n"
                    f"Trades: {daily_stats['trades']}\n"
                    f"Vitórias: {daily_stats['wins']}\n"
                    f"Derrotas: {daily_stats['losses']}\n"
                    f"Win Rate: {daily_stats['win_rate']}%\n"
                    f"Lucro: {profit_emoji} ${daily_stats['profit']:.2f}\n"
                    f"Saldo Final: ${daily_stats['balance']:.2f}\n\n"
                    f"*Performance:*\n"
                )
                
                if daily_stats['trades'] > 0:
                    if daily_stats['win_rate'] >= 60:
                        message += "🎯 EXCELENTE performance!"
                    elif daily_stats['win_rate'] >= 50:
                        message += "👍 BOA performance!"
                    else:
                        message += "⚠️ Performance abaixo do esperado"
                else:
                    message += "⏳ Nenhum trade hoje"
                
                update.message.reply_text(message, parse_mode='Markdown')
            except Exception as e:
                update.message.reply_text(f"❌ Erro ao obter estatísticas: {e}")
        
        # Registrar handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("status", status))
        dispatcher.add_handler(CommandHandler("balance", balance))
        dispatcher.add_handler(CommandHandler("history", history))
        dispatcher.add_handler(CommandHandler("notifications", notifications))
        dispatcher.add_handler(CommandHandler("stats", stats))
        dispatcher.add_handler(CommandHandler("notifs", notifications))  # Alias
    
    async def stop(self):
        """Para o bot do Telegram"""
        if self.updater and self.running:
            self.updater.stop()
            self.running = False
            logger.info("✅ Telegram bot parado")
    
    async def send_message(self, chat_id: str, message: str):
        """Envia mensagem para um chat específico"""
        if self.updater and self.running:
            try:
                self.updater.bot.send_message(
                    chat_id=chat_id, 
                    text=message,
                    parse_mode='Markdown'
                )
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao enviar mensagem Telegram: {e}")
                return False
        return False
    
    async def send_notification(self, notification: dict):
        """Envia notificação formatada para o Telegram"""
        if not self.updater or not self.running:
            return False
        
        try:
            level_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'success': '✅',
                'error': '❌'
            }.get(notification['level'], '📢')
            
            message = (
                f"{level_emoji} *NOTIFICAÇÃO ULTRABOT*\n"
                f"{notification['message']}\n"
                f"_{notification['timestamp'][11:16]}_"
            )
            
            self.updater.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao enviar notificação Telegram: {e}")
            return False
    
    def is_running(self):
        """Verifica se o bot está rodando"""
        return self.running
