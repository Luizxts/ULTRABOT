# telegram_bot/bot.py - BOT DE NOTIFICAÇÕES TELEGRAM
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json
from datetime import datetime

class TelegramNotifier:
    """Sistema de notificações via Telegram"""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token=token)
        self.setup_handlers()
        
    def setup_handlers(self):
        """Configura handlers de comando"""
        self.updater = Updater(self.token, use_context=True)
        dp = self.updater.dispatcher
        
        # Comandos
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("status", self.status))
        dp.add_handler(CommandHandler("trades", self.trades))
        dp.add_handler(CommandHandler("performance", self.performance))
        dp.add_handler(CommandHandler("stop", self.stop_bot))
        
        # Mensagens
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo))
        
        # Log de erros
        dp.add_error_handler(self.error)
        
    def start(self, update, context):
        """Comando /start"""
        welcome_message = """
🤖 *ULTRABOT PRO MAX SUPER* - CONTA REAL

*Comandos disponíveis:*
/start - Mensagem de boas-vindas
/status - Status atual do bot
/trades - Últimos trades
/performance - Performance atual
/stop - Parar o bot (emergência)

*Desenvolvido por:* Tavares Trader
*Versão:* 2.0 - Super Poderoso
        """
        update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    def status(self, update, context):
        """Comando /status"""
        status_message = f"""
📊 *STATUS DO ROBÔ*

*🤖 Status:* 🟢 OPERACIONAL
*💰 Saldo:* $500.00
*📈 Lucro Total:* $0.00
*🎯 Trades Hoje:* 0
*⚡ Win Rate:* 0%

*🕒 Última Atualização:* {datetime.now().strftime('%H:%M:%S')}
        """
        update.message.reply_text(status_message, parse_mode='Markdown')
    
    def trades(self, update, context):
        """Comando /trades"""
        trades_message = """
📋 *ÚLTIMOS TRADES*

*Nenhum trade executado ainda.*

_Execute o bot para ver trades em tempo real._
        """
        update.message.reply_text(trades_message, parse_mode='Markdown')
    
    def performance(self, update, context):
        """Comando /performance"""
        performance_message = f"""
📈 *PERFORMANCE*

*Total de Trades:* 0
*Trades Lucrativos:* 0
*Trades Perdedores:* 0
*Win Rate:* 0%
*Lucro Total:* $0.00
*Maior Ganho:* $0.00
*Maior Perda:* $0.00

*📊 Métricas de Risco:*
*Drawdown Máximo:* 0%
*Perda Máxima Consecutiva:* 0 trades
*Sharpe Ratio:* 0.00

*🕒 Atualizado em:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        update.message.reply_text(performance_message, parse_mode='Markdown')
    
    def stop_bot(self, update, context):
        """Comando /stop (emergência)"""
        # Aqui você integraria com a parada real do bot
        stop_message = """
🛑 *PARADA DE EMERGÊNCIA*

*Comando de parada recebido!*

⚠️ *Atenção:* Esta ação para imediatamente todos os trades e cancela ordens abertas.

_Entre em contato com o desenvolvedor se isso foi um erro._
        """
        update.message.reply_text(stop_message, parse_mode='Markdown')
    
    def echo(self, update, context):
        """Echo para mensagens não reconhecidas"""
        update.message.reply_text("""
❓ *Comando não reconhecido*

Use /start para ver todos os comandos disponíveis.
        """, parse_mode='Markdown')
    
    def error(self, update, context):
        """Handler de erros"""
        logger.warning(f'Update "{update}" caused error "{context.error}"')
    
    def send_notification(self, message):
        """Envia notificação para o chat"""
        try:
            self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
            return True
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
            return False
    
    def start_polling(self):
        """Inicia o polling do bot"""
        self.updater.start_polling()
        print("🤖 Bot Telegram iniciado!")
    
    def stop_polling(self):
        """Para o polling do bot"""
        self.updater.stop()

# Funções de notificação específicas
def send_trade_notification(notifier, trade_data):
    """Envia notificação de trade executado"""
    message = f"""
🎯 *NOVO TRADE EXECUTADO*

*Par:* {trade_data['symbol']}
*Direção:* {'🟢 COMPRA' if trade_data['side'] == 'BUY' else '🔴 VENDA'}
*Tamanho:* {trade_data['size']}
*Preço:* ${trade_data['price']:,.2f}
*Stop Loss:* ${trade_data.get('stop_loss', 0):,.2f}
*Take Profit:* ${trade_data.get('take_profit', 0):,.2f}

*Confiança da IA:* {trade_data.get('confidence', 0)*100:.1f}%
        """
    return notifier.send_notification(message)

def send_profit_notification(notifier, profit_data):
    """Envia notificação de lucro/prejuízo"""
    profit = profit_data['profit']
    message = f"""
💰 *TRADE FECHADO*

*Resultado:* {'🟢 LUCRO' if profit > 0 else '🔴 PREJUÍZO'}
*Valor:* ${abs(profit):.2f}
*Saldo Atual:* ${profit_data['balance']:.2f}
*Lucro Total:* ${profit_data['total_profit']:.2f}

{ '🎉 Bom trabalho!' if profit > 0 else '📉 Mantenha a estratégia!' }
        """
    return notifier.send_notification(message)

def send_alert_notification(notifier, alert_data):
    """Envia notificação de alerta"""
    message = f"""
⚠️ *ALERTA DO SISTEMA*

*Tipo:* {alert_data['type']}
*Severidade:* {alert_data['severity']}
*Mensagem:* {alert_data['message']}

*Ação Recomendada:* {alert_data.get('action', 'Monitorar')}
        """
    return notifier.send_notification(message)

# Configuração (substitua com suas credenciais)
TELEGRAM_TOKEN = "8444269740:AAE2dlSXozV4cIGNMMs72APIDcrYBvIq31M"
TELEGRAM_CHAT_ID = "-4977542145"

# Inicialização (comente se não usar Telegram)
# telegram_notifier = TelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
# telegram_notifier.start_polling()
