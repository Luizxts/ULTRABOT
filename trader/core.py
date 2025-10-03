import logging
import time
import random
import os
from datetime import datetime

# ✅ CONFIGURAÇÃO DIRETA - Sem import problemático
TRADING_INTERVAL = 300
TRADE_PROBABILITY = 0.3
WIN_RATE = 0.65
MAX_TRADE_AMOUNT = 50
TRADING_PAIRS = [
    "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT",
    "MATICUSDT", "SOLUSDT", "AVAXUSDT", "ATOMUSDT", "ALGOUSDT"
]

# Importação segura da IA
try:
    from ai_brain import AIBrain
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ IA não disponível - modo básico ativado")

class TradingBot:
    def __init__(self, telegram_bot=None, real_trading=False):
        self.logger = logging.getLogger(__name__)
        self.interval = TRADING_INTERVAL
        self.is_running = False
        self.telegram_bot = telegram_bot
        self.trade_count = 0
        self.real_trading = real_trading
        self.ai_brain = AIBrain() if AI_AVAILABLE else None
        self.current_pair = None
        self.total_profit = 0.0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
    def start_bot(self):
        """Inicia o bot de trading"""
        self.is_running = True
        self.trade_count = 0
        
        mode_text = "REAL 💰" if self.real_trading else "SIMULADO 🎮"
        ai_status = "Ativada" if AI_AVAILABLE else "Básico"
        
        self.logger.info(f"🤖 ULTRABOT INICIADO - Modo: {mode_text}")
        self.logger.info(f"⚙️ Intervalo: {self.interval}s | IA: {ai_status} | Pares: {len(TRADING_PAIRS)}")
        
        # ✅ NOTIFICAÇÃO INICIAL
        self._send_notification(
            f"🚀 ULTRABOT PRO INICIADO\n"
            f"💼 Modo: {mode_text}\n"
            f"⏰ Intervalo: 5min\n"
            f"🧠 IA: {ai_status}\n"
            f"📊 Pares: {len(TRADING_PAIRS)} ativos"
        )
        
        self.run_trading_cycle()
    
    def run_trading_cycle(self):
        """Executa ciclos de trading a cada 5 minutos"""
        cycle_count = 0
        while self.is_running:
            try:
                cycle_count += 1
                self.current_pair = random.choice(TRADING_PAIRS)
                
                self.logger.info(f"🔍 Análise #{cycle_count} - {self.current_pair}")
                
                # ✅ PENSAMENTOS DA IA EM TEMPO REAL
                if self.ai_brain:
                    market_data = self.get_market_data(self.current_pair)
                    ai_thoughts = self.ai_brain.get_ai_thoughts(self.current_pair, market_data)
                    
                    for thought in ai_thoughts:
                        self.logger.info(f"🧠 {thought}")
                        if cycle_count <= 2:
                            self._send_notification(f"🧠 {thought}")
                
                # Lógica de trading
                self.execute_advanced_trading(cycle_count)
                
                # ✅ AGUARDA 5 MINUTOS
                self.logger.info("⏰ Próxima análise em 5 minutos...")
                
                for i in range(self.interval, 0, -30):
                    if not self.is_running:
                        break
                    time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no ciclo: {e}")
                time.sleep(60)
    
    def execute_advanced_trading(self, cycle_count):
        """Executa lógica de trading"""
        adjusted_probability = TRADE_PROBABILITY
        
        if self.consecutive_wins >= 2:
            adjusted_probability += 0.1
        elif self.consecutive_losses >= 2:
            adjusted_probability -= 0.1
        
        adjusted_probability = max(0.1, min(0.8, adjusted_probability))
        
        # ✅ DECISÃO DE TRADE
        if random.random() < adjusted_probability:
            self.execute_trade(cycle_count)
        else:
            self.logger.info(f"⏸️ Sem trade - Probabilidade: {adjusted_probability*100:.1f}%")
    
    def execute_trade(self, cycle_count):
        """Executa trade"""
        strategy = random.choice(["Scalping", "Momentum", "Breakout"])
        direction = random.choice(['LONG', 'SHORT'])
        
        # Simulação de trade
        trade_result = "WIN" if random.random() < WIN_RATE else "LOSE"
        profit_loss = MAX_TRADE_AMOUNT * (0.04 if trade_result == "WIN" else -0.02)
        self.total_profit += profit_loss
        
        # ✅ NOTIFICAÇÃO
        if trade_result == "WIN":
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            message = f"🟢 TRADE #{cycle_count} - {direction} | +${profit_loss:.2f} ✅"
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            message = f"🔴 TRADE #{cycle_count} - {direction} | ${profit_loss:.2f} ❌"
        
        self.logger.info(f"📊 Trade: {direction} | Resultado: {trade_result}")
        self._send_notification(message)
    
    def get_market_data(self, pair):
        """Simula dados de mercado"""
        return {
            'last_price': str(random.randint(25000, 50000)),
            'price_24h_pcnt': str(random.uniform(-0.05, 0.05))
        }
    
    def stop_bot(self):
        """Para o bot"""
        self.is_running = False
        self.logger.info("🛑 Bot parado")
        self._send_notification(f"🛑 ULTRABOT PARADO | Lucro: ${self.total_profit:.2f}")
    
    def _send_notification(self, message):
        """Envia notificação para o Telegram"""
        try:
            if self.telegram_bot:
                self.telegram_bot.send_message(message)
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar notificação: {e}")
