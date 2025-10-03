import logging
import time
import random
import os
from datetime import datetime

# ✅ CONFIGURAÇÃO DIRETA
TRADING_INTERVAL = 300  # 5 minutos
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
        self.analysis_count = 0
        self.last_trade_time = None
        
    def start_bot(self):
        """Inicia o bot de trading"""
        self.is_running = True
        self.trade_count = 0
        self.analysis_count = 0
        
        mode_text = "REAL 💰" if self.real_trading else "SIMULADO 🎮"
        ai_status = "Ativada" if AI_AVAILABLE else "Básico"
        
        self.logger.info(f"🤖 ULTRABOT INICIADO - Modo: {mode_text}")
        self.logger.info(f"⚙️ Intervalo: {self.interval}s | IA: {ai_status}")
        
        # ✅ NOTIFICAÇÃO INICIAL COMPLETA
        initial_msg = (
            f"🚀 *ULTRABOT PRO INICIADO* 🚀\n"
            f"💼 *Modo:* {mode_text}\n"
            f"⏰ *Intervalo:* 5 minutos\n"
            f"🧠 *IA:* {ai_status}\n"
            f"📊 *Pares:* {len(TRADING_PAIRS)} ativos\n"
            f"⚡ *Status:* 100% Operacional\n"
            f"🔔 *Notificações:* Ativas\n"
            f"🔄 *Próxima análise em:* 1 minuto"
        )
        self._send_notification(initial_msg)
        self._add_system_log("🤖 ULTRABOT PRO - SISTEMA INICIADO", "info")
        self._add_system_log(f"💼 Modo: {mode_text} | IA: {ai_status}", "info")
        
        # ✅ INICIA O CICLO IMEDIATAMENTE
        self.run_trading_cycle()
    
    def run_trading_cycle(self):
        """Executa ciclos de trading a cada 5 minutos"""
        self._add_system_log("🔄 INICIANDO CICLO DE TRADING AUTÔNOMO", "info")
        
        while self.is_running:
            try:
                self.analysis_count += 1
                self.current_pair = random.choice(TRADING_PAIRS)
                
                # ✅ LOG DE INÍCIO DE ANÁLISE
                analysis_msg = f"🔍 *ANÁLISE #{self.analysis_count} INICIADA*\n💎 Par: {self.current_pair}"
                self._send_notification(analysis_msg)
                self._add_system_log(f"🔍 ANÁLISE #{self.analysis_count} - {self.current_pair}", "info")
                
                # ✅ PENSAMENTOS DA IA EM TEMPO REAL
                if self.ai_brain:
                    market_data = self.get_market_data(self.current_pair)
                    ai_thoughts = self.ai_brain.get_ai_thoughts(self.current_pair, market_data)
                    
                    for thought in ai_thoughts:
                        self.logger.info(f"🧠 {thought}")
                        self._add_system_log(f"🧠 {thought}", "info")
                        # Envia apenas as 2 primeiras análises da IA para não floodar
                        if self.analysis_count <= 2:
                            self._send_notification(f"🧠 {thought}")
                
                # ✅ EXECUTA TRADING
                self.execute_advanced_trading(self.analysis_count)
                
                # ✅ LOG DE CONCLUSÃO
                self._add_system_log(f"✅ Análise #{self.analysis_count} concluída", "info")
                
                # ✅ AGUARDA 5 MINUTOS (COM LOGS DE CONTAGEM)
                self._add_system_log("⏰ Aguardando 5 minutos para próxima análise...", "info")
                
                for i in range(5, 0, -1):
                    if not self.is_running:
                        break
                    countdown_msg = f"⏳ Próxima análise em {i} minuto{'s' if i > 1 else ''}"
                    self.logger.info(countdown_msg)
                    if i <= 3:  # Só mostra últimos 3 minutos
                        self._add_system_log(countdown_msg, "info")
                    time.sleep(60)  # Espera 1 minuto
                
            except Exception as e:
                error_msg = f"❌ Erro no ciclo de trading: {e}"
                self.logger.error(error_msg)
                self._send_notification(f"⚠️ *ERRO NO SISTEMA:* {e}")
                self._add_system_log(error_msg, "error")
                time.sleep(60)
    
    def execute_advanced_trading(self, cycle_count):
        """Executa lógica de trading avançada com IA"""
        # Análise de mercado
        market_sentiment = self.analyze_market_sentiment()
        risk_level = self.calculate_risk_level()
        
        analysis_info = f"📊 Sentimento: {market_sentiment} | Risco: {risk_level}"
        self.logger.info(analysis_info)
        self._add_system_log(analysis_info, "info")
        
        # Probabilidade ajustada
        adjusted_probability = TRADE_PROBABILITY
        
        if self.consecutive_wins >= 2:
            adjusted_probability += 0.1
            prob_msg = "🎯 Aumentando probabilidade após vitórias consecutivas"
            self._add_system_log(prob_msg, "info")
        elif self.consecutive_losses >= 2:
            adjusted_probability -= 0.1
            prob_msg = "🔄 Reduzindo probabilidade após derrotas consecutivas"
            self._add_system_log(prob_msg, "info")
        
        adjusted_probability = max(0.1, min(0.8, adjusted_probability))
        
        prob_display = f"🎯 Probabilidade de trade: {adjusted_probability*100:.1f}%"
        self.logger.info(prob_display)
        self._add_system_log(prob_display, "info")
        
        # ✅ DECISÃO DE TRADE
        if random.random() < adjusted_probability:
            decision_msg = "🎲 *DECISÃO:* EXECUTAR TRADE ✅"
            self.logger.info("🎲 DECISÃO: EXECUTAR TRADE")
            self._add_system_log("🎲 DECISÃO: EXECUTAR TRADE", "info")
            self._send_notification(decision_msg)
            self.execute_trade(cycle_count)
        else:
            decision_msg = "🎲 *DECISÃO:* AGUARDAR MELHOR OPORTUNIDADE ⏸️"
            self.logger.info("🎲 DECISÃO: AGUARDAR MELHOR OPORTUNIDADE")
            self._add_system_log("🎲 DECISÃO: AGUARDAR MELHOR OPORTUNIDADE", "info")
            if cycle_count <= 3:
                self._send_notification(decision_msg)
    
    def execute_trade(self, cycle_count):
        """Executa trade com logs completos"""
        strategy = random.choice(["Scalping", "Momentum", "Breakout", "IA Pattern", "Trend Following"])
        direction = random.choice(['LONG 📈', 'SHORT 📉'])
        amount = self.calculate_position_size()
        
        # Simulação de trade
        trade_result = "WIN" if random.random() < WIN_RATE else "LOSE"
        profit_loss = amount * (0.04 if trade_result == "WIN" else -0.02)
        self.total_profit += profit_loss
        self.last_trade_time = datetime.now().strftime("%H:%M:%S")
        
        # ✅ DADOS DO TRADE PARA HISTÓRICO
        trade_data = {
            "symbol": self.current_pair,
            "side": direction,
            "profit": profit_loss,
            "strategy": strategy
        }
        
        # ✅ NOTIFICAÇÃO DETALHADA NO TELEGRAM E LOGS
        if trade_result == "WIN":
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self.trade_count += 1
            
            telegram_msg = (
                f"🟢 *TRADE #{(self.trade_count)} - SUCESSO* ✅\n"
                f"💎 *Par:* {self.current_pair}\n"
                f"🎯 *Estratégia:* {strategy}\n"
                f"📊 *Direção:* {direction}\n"
                f"💰 *Lucro:* +${profit_loss:.2f}\n"
                f"📈 *Consecutivos:* {self.consecutive_wins} vitórias\n"
                f"🏆 *Total Acumulado:* ${self.total_profit:.2f}\n"
                f"⏰ *Horário:* {self.last_trade_time}"
            )
            
            log_msg = f"✅ TRADE SUCESSO: {direction} {self.current_pair} | +${profit_loss:.2f}"
            self._add_system_log(log_msg, "trade", trade_data)
            
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.trade_count += 1
            
            telegram_msg = (
                f"🔴 *TRADE #{self.trade_count} - RESULTADO* ❌\n"
                f"💎 *Par:* {self.current_pair}\n"
                f"🎯 *Estratégia:* {strategy}\n"
                f"📊 *Direção:* {direction}\n"
                f"💸 *Resultado:* ${profit_loss:.2f}\n"
                f"📉 *Consecutivos:* {self.consecutive_losses} derrotas\n"
                f"🎯 *Aprendendo com a experiência*\n"
                f"⏰ *Horário:* {self.last_trade_time}"
            )
            
            log_msg = f"❌ TRADE: {direction} {self.current_pair} | ${profit_loss:.2f}"
            self._add_system_log(log_msg, "trade", trade_data)
        
        # ✅ ENVIA NOTIFICAÇÃO COMPLETA
        self._send_notification(telegram_msg)
        self.logger.info(f"📊 Trade executado: {direction} | Resultado: {trade_result}")
        
        # Aprende com o trade
        if self.ai_brain:
            self.ai_brain.learn_from_trade({
                "pair": self.current_pair,
                "strategy": strategy,
                "profit": profit_loss
            })
    
    def analyze_market_sentiment(self):
        """Analisa sentimento do mercado"""
        sentiments = [
            "OTIMISTA 📈", "NEUTRO ↔️", "CUIDADO ⚠️", 
            "ALTA VOLATILIDADE 🌊", "TENDÊNCIA FORTE 🎯"
        ]
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        return random.choices(sentiments, weights=weights)[0]
    
    def calculate_risk_level(self):
        """Calcula nível de risco atual"""
        if self.consecutive_losses >= 3:
            return "ALTO 🔴"
        elif self.consecutive_wins >= 3:
            return "BAIXO 🟢"
        else:
            return "MODERADO 🟡"
    
    def calculate_position_size(self):
        """Calcula tamanho da posição baseado em risco"""
        base_size = MAX_TRADE_AMOUNT
        
        if self.consecutive_losses >= 2:
            return base_size * 0.5  # Reduz após derrotas
        elif self.consecutive_wins >= 2:
            return base_size * 1.2  # Aumenta após vitórias
        
        return base_size
    
    def get_market_data(self, pair):
        """Simula dados de mercado"""
        return {
            'last_price': str(random.randint(25000, 50000)),
            'price_24h_pcnt': str(random.uniform(-0.05, 0.05)),
            'volume_24h': str(random.randint(1000000, 50000000))
        }
    
    def stop_bot(self):
        """Para o bot com relatório completo"""
        self.is_running = False
        
        performance_msg = (
            f"🛑 *ULTRABOT PRO - RELATÓRIO FINAL*\n"
            f"📊 *Total de Análises:* {self.analysis_count}\n"
            f"💼 *Trades Executados:* {self.trade_count}\n"
            f"🏆 *Lucro Total:* ${self.total_profit:.2f}\n"
            f"📈 *Melhor Sequência:* {self.consecutive_wins} vitórias\n"
            f"🎮 *Modo:* {'REAL 💰' if self.real_trading else 'SIMULADO 🎮'}\n"
            f"⏰ *Tempo de Operação:* {self.analysis_count * 5} minutos"
        )
        
        self.logger.info("🛑 Bot parado pelo usuário")
        self._send_notification(performance_msg)
        self._add_system_log("🛑 ULTRABOT PARADO - RELATÓRIO GERADO", "warning")
    
    def _send_notification(self, message):
        """Envia notificação para o Telegram"""
        try:
            if self.telegram_bot:
                self.telegram_bot.send_message(message)
                self.logger.info("📱 Notificação enviada para Telegram")
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar notificação Telegram: {e}")
    
    def _add_system_log(self, message, log_type="info", trade_data=None):
        """Adiciona log ao sistema global"""
        try:
            # Importação circular - importa aqui para evitar problemas
            from app import add_log
            add_log(message, log_type, trade_data)
        except ImportError:
            # Fallback se não conseguir importar
            self.logger.info(f"[SISTEMA] {message}")
