import logging
import numpy as np
from datetime import datetime

class RiskManagement:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_risk_level = "medium"
        self.max_daily_trades = 50
        self.trade_count_today = 0
        self.last_reset = datetime.now()
        
    def approve_trade(self, decision, daily_stats):
        try:
            if self.trade_count_today >= self.max_daily_trades:
                return {
                    "approved": False,
                    "reason": f"Máximo de trades: {self.max_daily_trades}"
                }
            
            confidence = decision.get('confidence', 0)
            if confidence < 0.6:
                return {
                    "approved": False,
                    "reason": f"Confiança baixa: {confidence:.2%}"
                }
            
            leverage = decision.get('leverage', 10)
            if leverage > 25:
                return {
                    "approved": False, 
                    "reason": f"Leverage alta: {leverage}x"
                }
            
            current_drawdown = self._calculate_drawdown(daily_stats)
            if current_drawdown > 0.08:
                return {
                    "approved": False,
                    "reason": f"Drawdown alto: {current_drawdown:.2%}"
                }
            
            self.trade_count_today += 1
            return {
                "approved": True,
                "reason": "Trade aprovado",
                "risk_level": self.current_risk_level
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro aprovação: {e}")
            return {"approved": False, "reason": f"Erro: {str(e)}"}

    def _calculate_drawdown(self, daily_stats):
        total_profit = daily_stats.get('total_profit', 0)
        if total_profit < 0:
            return abs(total_profit) / 1000
        return 0

    def update_risk_level(self, market_conditions):
        volatility = market_conditions.get('volatility', 0)
        
        if volatility > 0.08:
            self.current_risk_level = "low"
        elif volatility < 0.03:
            self.current_risk_level = "high" 
        else:
            self.current_risk_level = "medium"
            
        self.logger.info(f"🔄 Risco: {self.current_risk_level}")

    def reset_daily_count(self):
        now = datetime.now()
        if now.date() != self.last_reset.date():
            self.trade_count_today = 0
            self.last_reset = now
            self.logger.info("🔄 Contador diário resetado")

    def get_risk_status(self):
        return {
            "current_risk_level": self.current_risk_level,
            "trades_today": self.trade_count_today,
            "max_daily_trades": self.max_daily_trades,
            "last_reset": self.last_reset
        }
