import numpy as np
import pandas as pd
from typing import Dict, List
import logging

class TradingStrategies:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.strategies = {
            "rsi_momentum": self.rsi_momentum,
            "macd_crossover": self.macd_crossover,
            "bollinger_bands": self.bollinger_bands_strategy,
            "volume_spike": self.volume_spike_detection,
            "support_resistance": self.support_resistance_breakout
        }
    
    def analyze(self, market_data: Dict) -> List[Dict]:
        signals = []
        
        for strategy_name, strategy_func in self.strategies.items():
            try:
                signal = strategy_func(market_data)
                if signal:
                    signal['type'] = strategy_name
                    signals.append(signal)
            except Exception as e:
                self.logger.error(f"❌ Erro estratégia {strategy_name}: {e}")
        
        return signals

    def rsi_momentum(self, market_data: Dict) -> Dict:
        if not market_data or 'close' not in market_data:
            return None
            
        prices = market_data['close']
        if len(prices) < 15:
            return None
        
        # Calcular RSI
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        if rsi < 30:
            return {
                "action": "buy", 
                "confidence": 0.8, 
                "reason": f"RSI oversold: {rsi:.1f}",
                "rsi_value": rsi
            }
        elif rsi > 70:
            return {
                "action": "sell", 
                "confidence": 0.8, 
                "reason": f"RSI overbought: {rsi:.1f}",
                "rsi_value": rsi
            }
        
        return None

    def macd_crossover(self, market_data: Dict) -> Dict:
        if not market_data or 'close' not in market_data:
            return None
            
        prices = market_data['close']
        if len(prices) < 30:
            return None
        
        # Calcular MACD
        exp1 = pd.Series(prices).ewm(span=12).mean()
        exp2 = pd.Series(prices).ewm(span=26).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9).mean()
        
        current_macd = macd.iloc[-1]
        current_signal = signal_line.iloc[-1]
        previous_macd = macd.iloc[-2]
        previous_signal = signal_line.iloc[-2]
        
        # Bullish crossover
        if current_macd > current_signal and previous_macd <= previous_signal:
            return {
                "action": "buy",
                "confidence": 0.75,
                "reason": "MACD crossover bullish",
                "macd_value": current_macd
            }
        # Bearish crossover  
        elif current_macd < current_signal and previous_macd >= previous_signal:
            return {
                "action": "sell",
                "confidence": 0.75,
                "reason": "MACD crossover bearish", 
                "macd_value": current_macd
            }
        
        return None

    def bollinger_bands_strategy(self, market_data: Dict) -> Dict:
        if not market_data or 'close' not in market_data:
            return None
            
        prices = market_data['close']
        if len(prices) < 21:
            return None
        
        # Calcular Bollinger Bands
        period = 20
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        current_price = prices[-1]
        
        if current_price <= lower_band:
            return {
                "action": "buy",
                "confidence": 0.7,
                "reason": "Preço na banda inferior",
                "current_price": current_price,
                "lower_band": lower_band
            }
        elif current_price >= upper_band:
            return {
                "action": "sell",
                "confidence": 0.7,
                "reason": "Preço na banda superior",
                "current_price": current_price, 
                "upper_band": upper_band
            }
        
        return None

    def volume_spike_detection(self, market_data: Dict) -> Dict:
        if not market_data or 'volume' not in market_data:
            return None
            
        volumes = market_data['volume']
        if len(volumes) < 10:
            return None
        
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[-10:-1])
        
        if avg_volume == 0:
            return None
            
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 2.0:
            if market_data['close'][-1] > market_data['close'][-2]:
                return {
                    "action": "buy",
                    "confidence": 0.65,
                    "reason": f"Volume bullish: {volume_ratio:.1f}x",
                    "volume_ratio": volume_ratio
                }
            else:
                return {
                    "action": "sell",
                    "confidence": 0.65,
                    "reason": f"Volume bearish: {volume_ratio:.1f}x",
                    "volume_ratio": volume_ratio
                }
        
        return None

    def support_resistance_breakout(self, market_data: Dict) -> Dict:
        if not market_data or 'high' not in market_data or 'low' not in market_data:
            return None
            
        highs = market_data['high']
        lows = market_data['low']
        
        if len(highs) < 20 or len(lows) < 20:
            return None
        
        resistance = max(highs[-20:])
        support = min(lows[-20:])
        current_price = market_data['close'][-1]
        
        if current_price >= resistance * 0.995:
            return {
                "action": "buy",
                "confidence": 0.7,
                "reason": f"Breakout resistência: {current_price:.1f}",
                "resistance_level": resistance
            }
        elif current_price <= support * 1.005:
            return {
                "action": "sell",
                "confidence": 0.7,
                "reason": f"Breakout suporte: {current_price:.1f}",
                "support_level": support
            }
        
        return None
