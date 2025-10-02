import logging
import numpy as np
from datetime import datetime, timedelta

class DefenseSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_drawdown = 0.10
        self.consecutive_losses = 0
        self.max_consecutive_losses = 3
        
    def analyze(self, market_data):
        signals = []
        
        if self._check_high_volatility(market_data):
            signals.append({
                "action": "hold",
                "confidence": 0.9,
                "reason": "Volatilidade excessiva",
                "type": "defense"
            })
        
        if self._check_danger_conditions(market_data):
            signals.append({
                "action": "sell", 
                "confidence": 0.8,
                "reason": "Condições perigosas",
                "type": "defense"
            })
        
        return signals

    def _check_high_volatility(self, market_data):
        if not market_data or 'close' not in market_data:
            return False
            
        prices = market_data['close']
        if len(prices) < 20:
            return False
            
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        
        return volatility > 0.05

    def _check_danger_conditions(self, market_data):
        if not market_data or 'close' not in market_data:
            return False
            
        prices = market_data['close']
        if len(prices) < 50:
            return False
            
        recent_prices = prices[-10:]
        if len(recent_prices) >= 5:
            current_price = recent_prices[-1]
            avg_5_period = sum(recent_prices[-5:]) / 5
            avg_10_period = sum(recent_prices) / len(recent_prices)
            
            if current_price < avg_5_period * 0.97:
                return True
                
            if avg_5_period < avg_10_period * 0.98:
                return True
                
        return False

    def record_loss(self):
        self.consecutive_losses += 1
        
    def record_win(self):
        self.consecutive_losses = 0

    def should_stop_trading(self, daily_stats):
        if daily_stats.get('max_drawdown', 0) > self.max_drawdown:
            return True, "Drawdown máximo excedido"
            
        if self.consecutive_losses >= self.max_consecutive_losses:
            return True, f"Muitas perdas consecutivas: {self.consecutive_losses}"
            
        return False, ""

    def get_defense_status(self):
        return {
            "consecutive_losses": self.consecutive_losses,
            "max_consecutive_losses": self.max_consecutive_losses,
            "max_drawdown": self.max_drawdown,
            "status": "active"
        }
