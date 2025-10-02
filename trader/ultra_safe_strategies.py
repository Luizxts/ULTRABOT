import numpy as np
from typing import Dict, List
import logging

class UltraSafeStrategies:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, market_data: Dict) -> List[Dict]:
        signals = []
        
        safe_signals = [
            self.trend_following_safe(market_data),
            self.mean_reversion_safe(market_data),
            self.volume_confirmation_safe(market_data)
        ]
        
        for signal in safe_signals:
            if signal:
                signal['type'] = 'ultra_safe'
                signals.append(signal)
        
        return signals

    def trend_following_safe(self, market_data: Dict) -> Dict:
        if not market_data or 'close' not in market_data:
            return None
            
        prices = market_data['close']
        if len(prices) < 50:
            return None
        
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        current_price = prices[-1]
        
        if current_price > sma_20 > sma_50:
            return {
                "action": "buy",
                "confidence": 0.85,
                "reason": "Tendência de alta forte",
                "sma_20": sma_20,
                "sma_50": sma_50
            }
        elif current_price < sma_20 < sma_50:
            return {
                "action": "sell",
                "confidence": 0.85,
                "reason": "Tendência de baixa forte",
                "sma_20": sma_20,
                "sma_50": sma_50
            }
        
        return None

    def mean_reversion_safe(self, market_data: Dict) -> Dict:
        if not market_data or 'close' not in market_data:
            return None
            
        prices = market_data['close']
        if len(prices) < 30:
            return None
        
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        current_price = prices[-1]
        
        z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
        
        if z_score < -2.0:
            return {
                "action": "buy",
                "confidence": 0.9,
                "reason": f"Reversão à média - Z-score: {z_score:.2f}",
                "z_score": z_score
            }
        elif z_score > 2.0:
            return {
                "action": "sell",
                "confidence": 0.9,
                "reason": f"Reversão à média - Z-score: {z_score:.2f}",
                "z_score": z_score
            }
        
        return None

    def volume_confirmation_safe(self, market_data: Dict) -> Dict:
        if not market_data or 'volume' not in market_data or 'close' not in market_data:
            return None
            
        volumes = market_data['volume']
        prices = market_data['close']
        
        if len(volumes) < 10 or len(prices) < 10:
            return None
        
        price_change = (prices[-1] - prices[-2]) / prices[-2]
        volume_change = (volumes[-1] - np.mean(volumes[-10:-1])) / np.mean(volumes[-10:-1])
        
        if price_change > 0.01 and volume_change > 0.5:
            return {
                "action": "buy",
                "confidence": 0.8,
                "reason": "Alta confirmada por volume",
                "price_change": price_change,
                "volume_change": volume_change
            }
        elif price_change < -0.01 and volume_change > 0.5:
            return {
                "action": "sell",
                "confidence": 0.8,
                "reason": "Baixa confirmada por volume",
                "price_change": price_change,
                "volume_change": volume_change
            }
        
        return None
