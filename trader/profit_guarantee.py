import logging
from datetime import datetime

class ProfitGuarantee:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.daily_target = 0.05
        self.force_take_profit = False
        
    def check_daily_target(self, daily_stats):
        try:
            current_profit = daily_stats.get('total_profit', 0)
            total_trades = daily_stats.get('total_trades', 0)
            
            profit_percentage = min(current_profit / 1000, 0.20)
            
            if profit_percentage >= self.daily_target:
                self.logger.info(f"🎯 TARGET ATINGIDO! Profit: {profit_percentage:.2%}")
                self.force_take_profit = True
                return True
            else:
                remaining = self.daily_target - profit_percentage
                self.logger.info(f"🎯 Progresso: {profit_percentage:.2%} | Faltam: {remaining:.2%}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro target: {e}")
            return False

    def should_take_profit(self, current_profit, trade_duration):
        if self.force_take_profit:
            return True, "Target diário atingido"
            
        if current_profit > 0.03:
            return True, f"Profit alto: {current_profit:.2%}"
            
        if trade_duration > 300 and current_profit > 0.01:
            return True, f"Profit por tempo: {current_profit:.2%}"
            
        return False, ""

    def reset_daily(self):
        self.force_take_profit = False
        self.logger.info("🔄 Garantia de lucro resetada")

    def get_profit_status(self):
        return {
            "daily_target": self.daily_target,
            "force_take_profit": self.force_take_profit,
            "status": "active"
        }
