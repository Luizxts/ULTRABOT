import logging
import numpy as np
from datetime import datetime
import random

class CognitiveEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sentiment_history = []
        
    def get_news_sentiment(self):
        try:
            scenarios = [
                {"sentiment": 0.8, "strength": 0.9, "reason": "Mercado em alta forte"},
                {"sentiment": 0.3, "strength": 0.6, "reason": "Mercado levemente positivo"},
                {"sentiment": -0.2, "strength": 0.4, "reason": "Mercado levemente negativo"},
                {"sentiment": -0.7, "strength": 0.8, "reason": "Mercado em baixa forte"},
                {"sentiment": 0.1, "strength": 0.3, "reason": "Mercado neutro"}
            ]
            
            scenario = random.choice(scenarios)
            
            sentiment_data = {
                "overall_sentiment": scenario["sentiment"],
                "sentiment_strength": scenario["strength"],
                "reason": scenario["reason"],
                "news_count": random.randint(3, 8),
                "timestamp": datetime.now(),
                "source": "market_analysis"
            }
            
            self.sentiment_history.append(sentiment_data)
            return sentiment_data
            
        except Exception as e:
            self.logger.error(f"❌ Erro sentimentos: {e}")
            return {
                "overall_sentiment": 0, 
                "sentiment_strength": 0, 
                "news_count": 0,
                "reason": "Análise não disponível"
            }

    def analyze(self, market_data, news_sentiment):
        signals = []
        
        sentiment = news_sentiment.get('overall_sentiment', 0)
        sentiment_strength = news_sentiment.get('sentiment_strength', 0)
        sentiment_reason = news_sentiment.get('reason', '')
        
        if sentiment > 0.3 and sentiment_strength > 0.5:
            signals.append({
                "action": "buy",
                "confidence": min(sentiment_strength * 0.9, 0.95),
                "reason": f"📈 {sentiment_reason}",
                "type": "sentiment_bullish"
            })
        elif sentiment < -0.3 and sentiment_strength > 0.5:
            signals.append({
                "action": "sell", 
                "confidence": min(sentiment_strength * 0.9, 0.95),
                "reason": f"📉 {sentiment_reason}",
                "type": "sentiment_bearish"
            })
        
        if market_data and 'close' in market_data:
            tech_signals = self._technical_analysis(market_data)
            signals.extend(tech_signals)
        
        return signals

    def _technical_analysis(self, market_data):
        signals = []
        prices = market_data['close']
        
        if len(prices) < 20:
            return signals
            
        current_price = prices[-1]
        sma_10 = np.mean(prices[-10:])
        sma_20 = np.mean(prices[-20:])
        
        if current_price > sma_10 > sma_20:
            signals.append({
                "action": "buy",
                "confidence": 0.75,
                "reason": "Tendência de alta confirmada",
                "type": "cognitive_trend"
            })
        elif current_price < sma_10 < sma_20:
            signals.append({
                "action": "sell",
                "confidence": 0.75,
                "reason": "Tendência de baixa confirmada", 
                "type": "cognitive_trend"
            })
            
        return signals

    def get_market_intuition(self):
        if len(self.sentiment_history) < 3:
            return "🔶 Neutro"
            
        recent_sentiments = [s['overall_sentiment'] for s in self.sentiment_history[-3:]]
        avg_sentiment = np.mean(recent_sentiments)
        
        if avg_sentiment > 0.3:
            return "🟢 Bullish"
        elif avg_sentiment < -0.3:
            return "🔴 Bearish" 
        else:
            return "🔶 Neutro"
