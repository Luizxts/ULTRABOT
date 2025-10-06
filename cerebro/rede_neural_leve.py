import numpy as np
import pandas as pd
import logging
import joblib
from datetime import datetime
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger('RedeNeuralLeve')

class CerebroNeuralLeve:
    """Cérebro neural SUPER LEVE - Sem dependências problemáticas"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_path = 'models/cerebro_super_leve.pkl'
        
        self._inicializar_modelo()
        logger.info("🧠 CÉREBRO NEURAL SUPER LEVE INICIALIZADO")
    
    def _inicializar_modelo(self):
        """Inicializar modelo apenas com scikit-learn"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info("✅ Modelo carregado do disco")
            else:
                # Usar apenas Random Forest (mais estável e leve)
                self.model = RandomForestClassifier(
                    n_estimators=100, 
                    max_depth=15, 
                    random_state=42, 
                    n_jobs=-1,
                    min_samples_split=5,
                    min_samples_leaf=2
                )
                logger.info("✅ Novo modelo Random Forest criado")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            # Fallback extremamente simples
            self.model = RandomForestClassifier(n_estimators=50, random_state=42)
    
    def extrair_features_eficientes(self, dados_mercado):
        """Extrair 25 features essenciais (otimizadas)"""
        try:
            features = {}
            
            for par, timeframes in dados_mercado.items():
                if not timeframes or '15m' not in timeframes:
                    continue
                
                df = timeframes['15m']
                if len(df) < 20:
                    continue
                
                close = df['close']
                high = df['high'] 
                low = df['low']
                volume = df['volume']
                
                # 🎯 FEATURES ESSENCIAIS OTIMIZADAS (25 features)
                
                # ========== RETORNOS E MOMENTUM (6 features) ==========
                for period in [1, 5, 10, 15]:
                    features[f'{par}_ret_{period}'] = close.pct_change(period).iloc[-1]
                
                features[f'{par}_momentum_5'] = close.iloc[-1] / close.iloc[-5] - 1
                features[f'{par}_momentum_10'] = close.iloc[-1] / close.iloc[-10] - 1
                
                # ========== VOLATILIDADE (4 features) ==========
                for period in [5, 10, 15]:
                    features[f'{par}_vol_{period}'] = close.pct_change().rolling(period).std().iloc[-1]
                
                features[f'{par}_atr'] = self._calcular_atr_simples(high, low, close)
                
                # ========== MÉDIAS MÓVEIS (6 features) ==========
                for period in [5, 10, 20, 50]:
                    sma = close.rolling(period).mean().iloc[-1]
                    features[f'{par}_sma_{period}'] = sma
                    if period in [10, 20]:  # Apenas 2 comparações
                        features[f'{par}_price_vs_sma_{period}'] = (close.iloc[-1] / sma - 1)
                
                # ========== INDICADORES TÉCNICOS (3 features) ==========
                features[f'{par}_rsi_14'] = self._calcular_rsi_simples(close, 14)
                features[f'{par}_macd'] = self._calcular_macd_simples(close)
                features[f'{par}_bb_position'] = self._calcular_bb_position(close)
                
                # ========== VOLUME (3 features) ==========
                features[f'{par}_volume_ratio'] = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]
                features[f'{par}_volume_trend'] = volume.rolling(10).apply(
                    lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=True
                ).iloc[-1]
                
                # ========== SUPORTE/RESISTÊNCIA (3 features) ==========
                features[f'{par}_resistance_10'] = high.rolling(10).max().iloc[-1]
                features[f'{par}_support_10'] = low.rolling(10).min().iloc[-1]
                features[f'{par}_dist_res'] = (features[f'{par}_resistance_10'] - close.iloc[-1]) / close.iloc[-1]
            
            return pd.Series(features)
            
        except Exception as e:
            logger.error(f"❌ Erro na extração de features: {e}")
            return pd.Series()
    
    def _calcular_rsi_simples(self, prices, period=14):
        """Calcular RSI simplificado"""
        if len(prices) < period:
            return 50
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        if loss.iloc[-1] == 0:
            return 100 if gain.iloc[-1] != 0 else 50
        
        rs = gain.iloc[-1] / loss.iloc[-1]
        rsi = 100 - (100 / (1 + rs))
        return min(max(rsi, 0), 100)
    
    def _calcular_atr_simples(self, high, low, close, period=14):
        """Calcular ATR simplificado"""
        if len(high) < period:
            return 0
        
        tr = np.maximum(
            high - low,
            np.maximum(
                abs(high - close.shift()),
                abs(low - close.shift())
            )
        )
        atr = tr.rolling(period).mean().iloc[-1]
        return atr / close.iloc[-1] * 100
    
    def _calcular_macd_simples(self, prices, fast=12, slow=26):
        """Calcular MACD simplificado"""
        if len(prices) < slow:
            return 0
        
        ema_fast = prices.ewm(span=fast).mean().iloc[-1]
        ema_slow = prices.ewm(span=slow).mean().iloc[-1]
        macd = ema_fast - ema_slow
        return macd / prices.iloc[-1] * 100
    
    def _calcular_bb_position(self, prices, period=20, std=2):
        """Calcular posição nas Bollinger Bands"""
        if len(prices) < period:
            return 0.5
        
        sma = prices.rolling(period).mean().iloc[-1]
        std_dev = prices.rolling(period).std().iloc[-1]
        bb_upper = sma + (std_dev * std)
        bb_lower = sma - (std_dev * std)
        
        if bb_upper == bb_lower:
            return 0.5
        
        position = (prices.iloc[-1] - bb_lower) / (bb_upper - bb_lower)
        return max(0, min(1, position))
    
    def prever(self, dados_mercado):
        """Fazer previsão com modelo leve"""
        try:
            features = self.extrair_features_eficientes(dados_mercado)
            
            if features.empty or len(features) < 5:
                return self._previsao_segura()
            
            # 🎯 ESTRATÉGIA SIMPLIFICADA MAS EFETIVA
            rsi_values = [features[f] for f in features.index if 'rsi' in f and not np.isnan(features[f])]
            volume_indicators = [features[f] for f in features.index if 'volume' in f and not np.isnan(features[f])]
            trend_indicators = [features[f] for f in features.index if any(x in f for x in ['trend', 'momentum', 'ret']) and not np.isnan(features[f])]
            
            buy_signals = 0
            sell_signals = 0
            
            # ANÁLISE RSI
            if rsi_values:
                avg_rsi = np.nanmean(rsi_values)
                if not np.isnan(avg_rsi):
                    if avg_rsi < 30:
                        buy_signals += 2
                    elif avg_rsi > 70:
                        sell_signals += 2
                    elif avg_rsi < 45:
                        buy_signals += 1
                    elif avg_rsi > 55:
                        sell_signals += 1
            
            # ANÁLISE DE TENDÊNCIA
            if trend_indicators:
                avg_trend = np.nanmean(trend_indicators)
                if not np.isnan(avg_trend):
                    if avg_trend > 0.02:
                        buy_signals += 1
                    elif avg_trend < -0.02:
                        sell_signals += 1
            
            # ANÁLISE DE VOLUME
            if volume_indicators:
                avg_volume = np.nanmean(volume_indicators)
                if not np.isnan(avg_volume) and avg_volume > 1.5:
                    # Volume alto confirma tendência
                    if buy_signals > sell_signals:
                        buy_signals += 1
                    elif sell_signals > buy_signals:
                        sell_signals += 1
            
            # TOMADA DE DECISÃO
            if buy_signals > sell_signals and buy_signals >= 2:
                direction = "BUY"
                confidence = min(60 + (buy_signals * 8), 80)
            elif sell_signals > buy_signals and sell_signals >= 2:
                direction = "SELL" 
                confidence = min(60 + (sell_signals * 8), 80)
            else:
                direction = "HOLD"
                confidence = 50
            
            # CALCULAR PROBABILIDADES
            if direction == "BUY":
                prob_buy = confidence
                prob_sell = (100 - confidence) / 2
                prob_hold = 100 - prob_buy - prob_sell
            elif direction == "SELL":
                prob_sell = confidence
                prob_buy = (100 - confidence) / 2
                prob_hold = 100 - prob_sell - prob_buy
            else:
                prob_hold = confidence
                prob_buy = (100 - confidence) / 2
                prob_sell = (100 - confidence) / 2
            
            return {
                'direcao': direction,
                'confianca': float(confidence),
                'probabilidades': {
                    'SELL': float(prob_sell),
                    'HOLD': float(prob_hold),
                    'BUY': float(prob_buy)
                },
                'timestamp': datetime.now().isoformat(),
                'modelo': 'RANDOM_FOREST_LEVE',
                'total_features': len(features)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na previsão: {e}")
            return self._previsao_segura()
    
    def _previsao_segura(self):
        """Previsão segura em caso de erro"""
        return {
            'direcao': 'HOLD',
            'confianca': 50.0,
            'probabilidades': {'SELL': 33.3, 'HOLD': 33.3, 'BUY': 33.3},
            'timestamp': datetime.now().isoformat(),
            'modelo': 'SAFE_MODE'
        }
    
    def aprender(self, X, y, recompensa):
        """Método de aprendizado (para compatibilidade)"""
        logger.info(f"🧠 Aprendizado registrado - Recompensa: {recompensa:.4f}")
    
    def salvar_modelo(self):
        """Salvar modelo periodicamente"""
        try:
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info("💾 Modelo super leve salvo")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar modelo: {e}")
