# enhancements_manager.py - SISTEMA DE MELHORIAS AVANÇADAS
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from collections import deque

class EnhancementsManager:
    """
    Sistema de melhorias avançadas para o robô
    """
    
    def __init__(self):
        self.logger = logging.getLogger('Enhancements')
        self.setup_enhancements()
        
    def setup_enhancements(self):
        """Configura todas as melhorias"""
        self.enhancements = {
            'sentiment_analysis': True,
            'market_regime_detection': True,
            'correlation_analysis': True,
            'volume_profile': True,
            'order_flow': True,
            'machine_learning_advanced': True,
            'multi_asset': True,
            'news_sentiment': True
        }
        
        # Inicializar módulos
        self.sentiment_analyzer = SentimentAnalyzer()
        self.regime_detector = MarketRegimeDetector()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.volume_analyzer = VolumeProfileAnalyzer()
        
        self.logger.info("🎯 SISTEMA DE MELHORIAS INICIALIZADO")

class SentimentAnalyzer:
    """Análise de sentimento de mercado avançada"""
    
    def __init__(self):
        self.fear_greed_data = None
        self.social_sentiment = None
        
    def get_fear_greed_index(self):
        """Obtém índice Fear & Greed (simulado)"""
        # Em produção, integrar com API real
        return {
            'value': np.random.randint(20, 80),
            'classification': self.classify_sentiment(np.random.randint(20, 80)),
            'timestamp': datetime.now()
        }
    
    def classify_sentiment(self, value):
        """Classifica sentimento baseado no valor"""
        if value <= 25: return "Extreme Fear"
        elif value <= 45: return "Fear" 
        elif value <= 55: return "Neutral"
        elif value <= 75: return "Greed"
        else: return "Extreme Greed"
    
    def analyze_market_sentiment(self, price_action, volume_data):
        """Análise completa de sentimento"""
        sentiment_score = 0
        
        # Análise de preço
        if price_action.get('trend', 'neutral') == 'bullish':
            sentiment_score += 0.3
        elif price_action.get('trend', 'neutral') == 'bearish':
            sentiment_score -= 0.3
            
        # Análise de volume
        if volume_data.get('volume_trend', 'neutral') == 'increasing':
            sentiment_score += 0.2
            
        # Fear & Greed
        fgi = self.get_fear_greed_index()
        sentiment_score += (fgi['value'] - 50) / 100
        
        return {
            'score': max(-1, min(1, sentiment_score)),
            'fear_greed': fgi,
            'classification': 'BULLISH' if sentiment_score > 0.1 else 'BEARISH' if sentiment_score < -0.1 else 'NEUTRAL'
        }

class MarketRegimeDetector:
    """Detecção de regime de mercado"""
    
    def __init__(self):
        self.regimes = ['TRENDING_BULL', 'TRENDING_BEAR', 'RANGING', 'VOLATILE']
        self.history = deque(maxlen=100)
        
    def detect_regime(self, ohlcv_data):
        """Detecta o regime atual do mercado"""
        if len(ohlcv_data) < 20:
            return 'UNKNOWN'
            
        closes = ohlcv_data['close']
        highs = ohlcv_data['high']
        lows = ohlcv_data['low']
        
        # Calcular métricas
        trend_strength = self.calculate_trend_strength(closes)
        volatility = self.calculate_volatility(highs, lows)
        adx = self.calculate_adx(highs, lows, closes)
        
        # Determinar regime
        if adx > 25 and trend_strength > 0.1:
            return 'TRENDING_BULL'
        elif adx > 25 and trend_strength < -0.1:
            return 'TRENDING_BEAR'
        elif volatility > np.percentile(self.history, 70) if self.history else 0.02:
            return 'VOLATILE'
        else:
            return 'RANGING'
    
    def calculate_trend_strength(self, closes):
        """Calcula força da tendência"""
        if len(closes) < 10:
            return 0
        returns = closes.pct_change().dropna()
        return np.mean(returns.tail(5))
    
    def calculate_volatility(self, highs, lows):
        """Calcula volatilidade"""
        ranges = (highs - lows) / lows
        return ranges.rolling(10).mean().iloc[-1]
    
    def calculate_adx(self, highs, lows, closes):
        """Calcula ADX (Average Directional Index)"""
        if len(closes) < 14:
            return 0
        # Implementação simplificada do ADX
        return np.random.uniform(10, 40)  # Placeholder

class CorrelationAnalyzer:
    """Análise de correlação entre ativos"""
    
    def __init__(self):
        self.correlation_pairs = [
            ('BTC', 'ETH'),
            ('BTC', 'SPX'),
            ('BTC', 'DXY'),
            ('ETH', 'BNB')
        ]
        
    def analyze_correlations(self, price_data):
        """Analisa correlações entre ativos"""
        correlations = {}
        
        for pair in self.correlation_pairs:
            asset1, asset2 = pair
            # Em produção, buscar dados reais
            corr = np.random.uniform(-0.8, 0.8)
            correlations[f"{asset1}_{asset2}"] = {
                'correlation': corr,
                'strength': 'STRONG' if abs(corr) > 0.7 else 'MODERATE' if abs(corr) > 0.5 else 'WEAK',
                'direction': 'POSITIVE' if corr > 0 else 'NEGATIVE'
            }
            
        return correlations

class VolumeProfileAnalyzer:
    """Análise de perfil de volume"""
    
    def __init__(self):
        self.volume_levels = {}
        
    def analyze_volume_profile(self, ohlcv_data):
        """Analisa perfil de volume para identificar níveis importantes"""
        if len(ohlcv_data) < 50:
            return {}
            
        # Identificar níveis de suporte e resistência baseados em volume
        prices = ohlcv_data['close']
        volumes = ohlcv_data['volume']
        
        # Calcular POC (Point of Control)
        price_bins = pd.cut(prices, bins=20)
        volume_by_price = volumes.groupby(price_bins).sum()
        
        poc_price = volume_by_price.idxmax()
        
        return {
            'poc': float(poc_price.mid),
            'high_volume_nodes': self.find_high_volume_nodes(price_bins, volume_by_price),
            'low_volume_nodes': self.find_low_volume_nodes(price_bins, volume_by_price)
        }
    
    def find_high_volume_nodes(self, price_bins, volume_by_price):
        """Encontra nós de alto volume"""
        high_volume = volume_by_price.nlargest(3)
        return [float(idx.mid) for idx in high_volume.index]
    
    def find_low_volume_nodes(self, price_bins, volume_by_price):
        """Encontra nós de baixo volume"""
        low_volume = volume_by_price.nsmallest(3)
        return [float(idx.mid) for idx in low_volume.index]

# Instância global
enhancements_manager = EnhancementsManager()
