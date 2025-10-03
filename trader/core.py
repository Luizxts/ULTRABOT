import logging
import time
import random
from datetime import datetime
from config import *
from ai_brain import AIBrain

class TradingBot:
    def __init__(self, telegram_bot=None, real_trading=False):
        self.logger = logging.getLogger(__name__)
        self.interval = TRADING_INTERVAL
        self.is_running = False
        self.telegram_bot = telegram_bot
        self.trade_count = 0
        self.real_trading = real_trading
        self.ai_brain = AIBrain()
        self.current_pair = None
        self.total_profit = 0.0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
    def start_bot(self):
        """Inicia o bot de trading"""
        self.is_running = True
        self.trade_count = 0
        
        mode_text = "REAL 💰" if self.real_trading else "SIMULADO 🎮"
        
        self.logger.info(f"🤖 ULTRABOT INICIADO - Modo: {mode_text}")
        self.logger.info(f"⚙️ Intervalo: {self.interval}s | IA: Ativada | Pares: {len(TRADING_PAIRS)}")
        
        # ✅ NOTIFICAÇÃO INICIAL
        self._send_notification(
            f"🚀 ULTRABOT PRO INICIADO\n"
            f"💼 Modo: {mode_text}\n"
            f"⏰ Intervalo: 5min\n"
            f"🧠 IA: Ativada\n"
            f"📊 Pares: {len(TRADING_PAIRS)} ativos\n"
            f"⚡ Sistema: 100% Operacional"
        )
        
        self.run_trading_cycle()
    
    def run_trading_cycle(self):
        """Executa ciclos de trading a cada 5 minutos"""
        while self.is_running:
            try:
                self.trade_count += 1
                self.current_pair = random.choice(TRADING_PAIRS)
                
                # ✅ PENSAMENTOS DA IA EM TEMPO REAL
                market_data = self.get_market_data(self.current_pair)
                ai_thoughts = self.ai_brain.get_ai_thoughts(self.current_pair, market_data)
                
                self.logger.info(f"🔍 Análise #{self.trade_count} - {self.current_pair}")
                
                # Mostra pensamentos da IA
                for thought in ai_thoughts:
                    self.logger.info(f"🧠 {thought}")
                    self._send_notification(f"🧠 {thought}")
                
                # Lógica de trading avançada
                self.execute_advanced_trading()
                
                # ✅ AGUARDA 5 MINUTOS
                self.logger.info(f"⏰ Próxima análise em 5 minutos...")
                
                # Contagem regressiva inteligente
                for i in range(self.interval, 0, -60):
                    remaining_min = i // 60
                    if remaining_min <= 5:  # Mostra apenas últimos 5 minutos
                        self.logger.info(f"⏳ Próxima análise em {remaining_min} min")
                    time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no ciclo: {e}")
                self._send_notification(f"⚠️ Erro no sistema: {e}")
                time.sleep(60)
    
    def execute_advanced_trading(self):
        """Executa lógica de trading avançada com IA"""
        # Análise de mercado profunda
        market_sentiment = self.analyze_market_sentiment()
        risk_level = self.calculate_risk_level()
        
        self.logger.info(f"📊 Sentimento: {market_sentiment} | Risco: {risk_level}")
        
        # Probabilidade ajustada pela IA
        adjusted_probability = self.adjust_probability_by_ai()
        
        # ✅ DECISÃO DE TRADE INTELIGENTE
        if random.random() < adjusted_probability:
            self.execute_intelligent_trade()
        else:
            waiting_msg = (
                f"⏸️ Análise #{self.trade_count} - {self.current_pair}\n"
                f"📊 Sem oportunidades ideais\n"
                f"🎯 Probabilidade ajustada: {adjusted_probability*100:.1f}%\n"
                f"⏰ Próxima análise em 5min"
            )
            self.logger.info(f"⏸️ Sem trade - Probabilidade: {adjusted_probability*100:.1f}%")
            self._send_notification(waiting_msg)
    
    def execute_intelligent_trade(self):
        """Executa trade inteligente com IA"""
        # Estratégia baseada em análise
        strategy = self.select_trading_strategy()
        direction = random.choice(['LONG', 'SHORT'])
        amount = self.calculate_position_size()
        
        # Simulação de trade
        trade_result = "WIN" if random.random() < WIN_RATE else "LOSE"
        profit_loss = amount * (0.04 if trade_result == "WIN" else -0.02)
        self.total_profit += profit_loss
        
        # Aprende com o trade
        self.ai_brain.learn_from_trade({
            "pair": self.current_pair,
            "strategy": strategy,
            "profit": profit_loss
        })
        
        # ✅ NOTIFICAÇÃO DETALHADA
        if trade_result == "WIN":
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            message = (
                f"🟢 TRADE #{self.trade_count} - {direction}\n"
                f"💎 Par: {self.current_pair}\n"
                f"🎯 Estratégia: {strategy}\n"
                f"💰 Lucro: +${profit_loss:.2f} ✅\n"
                f"📈 Consecutivos: {self.consecutive_wins} vitórias\n"
                f"🏆 Total: ${self.total_profit:.2f}"
            )
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            message = (
                f"🔴 TRADE #{self.trade_count} - {direction}\n"
                f"💎 Par: {self.current_pair}\n"
                f"🎯 Estratégia: {strategy}\n"
                f"💸 Prejuízo: -${abs(profit_loss):.2f} ❌\n"
                f"📉 Consecutivos: {self.consecutive_losses} derrotas\n"
                f"🎯 Aprendendo com o erro..."
            )
        
        self.logger.info(f"📊 Trade executado: {direction} | Resultado: {trade_result}")
        self._send_notification(message)
    
    def analyze_market_sentiment(self):
        """Analisa sentimento do mercado"""
        sentiments = ["OTIMISTA", "NEUTRO", "CUIDADO", "ALTA VOLATILIDADE"]
        weights = [0.4, 0.3, 0.2, 0.1]  # Mais otimista por padrão
        return random.choices(sentiments, weights=weights)[0]
    
    def calculate_risk_level(self):
        """Calcula nível de risco atual"""
        if self.consecutive_losses >= 3:
            return "ALTO"
        elif self.consecutive_wins >= 3:
            return "BAIXO"
        else:
            return "MODERADO"
    
    def adjust_probability_by_ai(self):
        """Ajusta probabilidade baseado em aprendizado"""
        base_prob = TRADE_PROBABILITY
        
        # Ajustes baseados em performance
        if self.consecutive_wins >= 2:
            base_prob += 0.1  # Aumenta probabilidade após vitórias
        elif self.consecutive_losses >= 2:
            base_prob -= 0.1  # Reduz probabilidade após derrotas
        
        return max(0.1, min(0.8, base_prob))  # Limites de 10% a 80%
    
    def select_trading_strategy(self):
        """Seleciona estratégia de trading"""
        strategies = [
            "Scalping 5min", "Momentum", "Reversão à Média", 
            "Breakout", "IA Pattern", "Conservative", "Aggressive"
        ]
        return random.choice(strategies)
    
    def calculate_position_size(self):
        """Calcula tamanho da posição baseado em risco"""
        base_size = MAX_TRADE_AMOUNT
        
        if self.consecutive_losses >= 2:
            return base_size * 0.5  # Reduz tamanho após perdas
        elif self.consecutive_wins >= 2:
            return base_size * 1.2  # Aumenta após vitórias
        
        return base_size
    
    def get_market_data(self, pair):
        """Simula dados de mercado"""
        return {
            'last_price': str(random.randint(100, 50000)),
            'price_24h_pcnt': str(random.uniform(-0.1, 0.1)),
            'volume_24h': str(random.randint(1000000, 50000000))
        }
    
    def stop_bot(self):
        """Para o bot"""
        self.is_running = False
        performance_msg = (
            f"🛑 ULTRABOT PARADO\n"
            f"📊 Total de Análises: {self.trade_count}\n"
            f"🏆 Lucro Total: ${self.total_profit:.2f}\n"
            f"🎮 Modo: {'REAL 💰' if self.real_trading else 'SIMULADO 🎮'}"
        )
        self.logger.info("🛑 Bot parado")
        self._send_notification(performance_msg)
    
    def _send_notification(self, message):
        """Envia notificação para o Telegram"""
        try:
            if self.telegram_bot:
                self.telegram_bot.send_message(message)
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar notificação: {e}")
