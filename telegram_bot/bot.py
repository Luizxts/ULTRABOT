import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import asyncio
import html
import json
import os
from datetime import datetime

try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    TELEGRAM_BOT_TOKEN = "8444269740:AAE2dlSXozV4cIGNMMs72APIDcrYBvIq31M"
    TELEGRAM_CHAT_ID = "-4977542145"

logger = logging.getLogger(__name__)

# Sistema de estado compartilhado
class SharedState:
    def __init__(self):
        self.state_file = 'bot_state.json'
    
    def get_state(self):
        """Obtém o estado atual do bot"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Verificar se o estado não está muito antigo (mais de 10 minutos)
                    last_update = state.get('last_update')
                    if last_update:
                        last_dt = datetime.fromisoformat(last_update)
                        if (datetime.now() - last_dt).total_seconds() > 600:  # 10 minutos
                            return {'running': False, 'is_stale': True}
                    return {**state, 'is_stale': False}
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar estado compartilhado: {e}")
        
        # Estado padrão
        return {
            'running': False,
            'started_at': None,
            'trades_today': 0,
            'profit_today': 0.0,
            'last_update': datetime.now().isoformat(),
            'is_stale': False
        }
    
    def set_state(self, running, trades=0, profit=0.0):
        """Define o estado do bot"""
        state = {
            'running': running,
            'started_at': datetime.now().isoformat() if running else None,
            'trades_today': trades,
            'profit_today': profit,
            'last_update': datetime.now().isoformat(),
            'is_stale': False
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"💾 Estado compartilhado atualizado: running={running}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar estado compartilhado: {e}")
            return False

# Instância global do estado compartilhado
shared_state = SharedState()

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
            
            # Verificar estado atual do bot principal
            bot_state = shared_state.get_state()
            bot_status = "RODANDO 🚀" if bot_state.get('running') else "PARADO ⏹️"
            
            # Enviar mensagem de inicialização
            await self.send_message(
                self.chat_id, 
                f"🤖 *ULTRABOT PRO INICIADO* 🚀\n"
                f"Modo: SIMULATION 🎮\n"
                f"Estado Bot: {bot_status}\n"
                f"Pronto para operar!\n"
                f"Use /status para verificar o estado atual."
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
            
            # Verificar estado atual
            bot_state = shared_state.get_state()
            bot_status = "🟢 RODANDO" if bot_state.get('running') else "🔴 PARADO"
            
            update.message.reply_text(
                f"🤖 OLÁ {user.first_name}!\n"
                f"*ULTRABOT PRO ATIVO*\n"
                f"Status: {bot_status}\n"
                f"Modo: SIMULATION 🎮\n"
                f"Saldo: $1000.00\n\n"
                f"*Comandos disponíveis:*\n"
                f"/status - Status atual\n"
                f"/balance - Saldos\n"
                f"/history - Últimos trades\n"
                f"/notifications - Ver notificações\n"
                f"/stats - Estatísticas do dia\n"
                f"/start_bot - Iniciar bot\n"
                f"/stop_bot - Parar bot",
                parse_mode='Markdown'
            )
        
        # Comando /status
        def status(update: Update, context: CallbackContext):
            try:
                from trader.core import UltraBot
                bot = UltraBot()
                status_info = bot.get_status()
                
                # Verificar estado global compartilhado
                global_state = shared_state.get_state()
                is_running_global = global_state.get('running', False)
                
                # Determinar estado real (prioridade para estado global)
                actual_running = status_info['running'] or is_running_global
                
                status_emoji = "✅" if actual_running else "⏹️"
                profit_emoji = "📈" if status_info['profit_today'] >= 0 else "📉"
                
                # Informações de sincronização
                sync_info = ""
                if global_state.get('is_stale'):
                    sync_info = "\n⚠️ *Estado desatualizado*"
                elif is_running_global != status_info['running']:
                    sync_info = f"\n🔀 *Sincronizado via Web*" if is_running_global else ""
                
                message = (
                    f"*📊 STATUS ULTRABOT* {status_emoji}\n"
                    f"Estado: {'RODANDO 🚀' if actual_running else 'PARADO ⏹️'}\n"
                    f"Modo: {status_info['mode']}\n"
                    f"Saldo: ${status_info['balance']:.2f}\n"
                    f"Disponível: ${status_info['available_balance']:.2f}\n"
                    f"Trades Hoje: {status_info['trades_today']}\n"
                    f"W/L: {status_info['wins_today']}/{status_info['losses_today']}\n"
                    f"Lucro: {profit_emoji} ${status_info['profit_today']:.2f}\n"
                    f"Win Rate: {status_info['win_rate']}%\n"
                    f"Próximo trade: {status_info['next_trade_in']}\n"
                    f"Notificações: {status_info['notifications_count']} não lidas"
                    f"{sync_info}"
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
                
                # Verificar estado atual
                bot_state = shared_state.get_state()
                bot_status = "🟢 RODANDO" if bot_state.get('running') else "🔴 PARADO"
                
                message = (
                    f"*💰 SALDO ATUAL* | {bot_status}\n"
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
                
                # Verificar estado atual
                bot_state = shared_state.get_state()
                bot_status = "🟢" if bot_state.get('running') else "🔴"
                
                message = f"*📈 ÚLTIMOS TRADES* | Status: {bot_status}\n\n"
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
                
                # Verificar estado atual
                bot_state = shared_state.get_state()
                bot_status = "🟢 RODANDO" if bot_state.get('running') else "🔴 PARADO"
                
                if not notifications:
                    update.message.reply_text(f"✅ Nenhuma notificação não lida | Status: {bot_status}")
                    return
                
                message = f"*🔔 NOTIFICAÇÕES* | Status: {bot_status}\n\n"
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
                
                # Verificar estado atual
                bot_state = shared_state.get_state()
                bot_status = "🟢 RODANDO" if bot_state.get('running') else "🔴 PARADO"
                
                profit_emoji = "📈" if daily_stats['profit'] >= 0 else "📉"
                
                message = (
                    f"*📊 ESTATÍSTICAS DO DIA* | Status: {bot_status}\n"
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
        
        # Comando /start_bot
        def start_bot(update: Update, context: CallbackContext):
            try:
                # Atualizar estado compartilhado
                success = shared_state.set_state(True)
                
                if success:
                    update.message.reply_text(
                        "🚀 *COMANDO ENVIADO: INICIAR BOT*\n"
                        "O bot principal deve iniciar em breve.\n"
                        "Use /status para verificar o estado atual.",
                        parse_mode='Markdown'
                    )
                    
                    # Enviar notificação de comando recebido
                    async def send_notification():
                        await self.send_message(
                            self.chat_id,
                            "📱 *COMANDO RECEBIDO VIA TELEGRAM*\n"
                            "Iniciar bot solicitado!\n"
                            "O bot principal deve processar este comando."
                        )
                    
                    asyncio.create_task(send_notification())
                else:
                    update.message.reply_text("❌ Erro ao enviar comando de início.")
                    
            except Exception as e:
                update.message.reply_text(f"❌ Erro: {e}")
        
        # Comando /stop_bot
        def stop_bot(update: Update, context: CallbackContext):
            try:
                # Atualizar estado compartilhado
                success = shared_state.set_state(False)
                
                if success:
                    update.message.reply_text(
                        "⏹️ *COMANDO ENVIADO: PARAR BOT*\n"
                        "O bot principal deve parar em breve.\n"
                        "Use /status para verificar o estado atual.",
                        parse_mode='Markdown'
                    )
                    
                    # Enviar notificação de comando recebido
                    async def send_notification():
                        await self.send_message(
                            self.chat_id,
                            "📱 *COMANDO RECEBIDO VIA TELEGRAM*\n"
                            "Parar bot solicitado!\n"
                            "O bot principal deve processar este comando."
                        )
                    
                    asyncio.create_task(send_notification())
                else:
                    update.message.reply_text("❌ Erro ao enviar comando de parada.")
                    
            except Exception as e:
                update.message.reply_text(f"❌ Erro: {e}")
        
        # Registrar handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("status", status))
        dispatcher.add_handler(CommandHandler("balance", balance))
        dispatcher.add_handler(CommandHandler("history", history))
        dispatcher.add_handler(CommandHandler("notifications", notifications))
        dispatcher.add_handler(CommandHandler("stats", stats))
        dispatcher.add_handler(CommandHandler("notifs", notifications))  # Alias
        dispatcher.add_handler(CommandHandler("start_bot", start_bot))
        dispatcher.add_handler(CommandHandler("stop_bot", stop_bot))
    
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
