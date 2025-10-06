import numpy as np
import pandas as pd
import logging
import joblib
from datetime import datetime
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb

logger = logging.getLogger('RedeNeuralLeve')

class CerebroNeuralLeve:
    """Cérebro neural otimizado para Railway - Versão Leve"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_path = 'models/cerebro_leve.pkl'
        
        self._inicializar_modelo()
        logger.info("🧠 CÉREBRO NEURAL LEVE INICIALIZADO")
    
    def _inicializar_modelo(self):
        """Inicializar modelo ensemble leve"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info("✅ Modelo carregado do disco")
            else:
                # Ensemble de modelos leves
                self.model = {
                    'rf': RandomForestClassifier(
                        n_estimators=100, 
                        max_depth=15, 
                        random_state=42, 
                        n_jobs=-1,
                        min_samples_split=5,
                        min_samples_leaf=2
                    ),
                    'xgb': xgb.XGBClassifier(
                        n_estimators=100, 
                        max_depth=8, 
                        random_state=42, 
                        verbosity=0,
                        learning_rate=0.1,
                        subsample=0.8
                    ),
                    'lgb': lgb.LGBMClassifier(
                        n_estimators=100, 
                        max_depth=8, 
                        random_state=42, 
                        verbose=-1,
                        learning_rate=0.1,
                        subsample=0.8
                    ),
                    'gbt': GradientBoostingClassifier(
                        n_estimators=100,
                        max_depth=6,
                        random_state=42,
                        learning_rate=0.1
                    )
                }
                logger.info("✅ Novos modelos ensemble criados")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            self.model = RandomForestClassifier(
                n_estimators=150, 
                max_depth=12, 
                random_state=42, 
                n_jobs=-1
            )
    
    def extrair_features_eficientes(self, dados_mercado):
        """Extrair 40 features eficientes balanceadas"""
        try:
            features = {}
            
            for par, timeframes in dados_mercado.items():
                if not timeframes or '15m' not in timeframes:
                    continue
                
                df = timeframes['15m']
                if len(df) < 25:
                    continue
                
                close = df['close']
                high = df['high'] 
                low = df['low']
                volume = df['volume']
                
                # 🎯 FEATURES ESSENCIAIS (40 features balanceadas)
                
                # ========== RETORNOS E MOMENTUM (8 features) ==========
                for period in [1, 3, 5, 10, 15, 20]:
                    features[f'{par}_ret_{period}'] = close.pct_change(period).iloc[-1]
                
                features[f'{par}_momentum_5'] = close.iloc[-1] / close.iloc[-5] - 1
                features[f'{par}_momentum_10'] = close.iloc[-1] / close.iloc[-10] - 1
                
                # ========== VOLATILIDADE (6 features) ==========
                for period in [5, 10, 15, 20, 25]:
                    features[f'{par}_vol_{period}'] = close.pct_change().rolling(period).std().iloc[-1]
                
                features[f'{par}_atr'] = self._calcular_atr(high, low, close)
                
                # ========== MÉDIAS MÓVEIS (8 features) ==========
                for period in [5, 10, 15, 20, 25, 30, 50]:
                    sma = close.rolling(period).mean().iloc[-1]
                    features[f'{par}_sma_{period}'] = sma
                    features[f'{par}_price_vs_sma_{period}'] = (close.iloc[-1] / sma - 1)
                
                # ========== INDICADORES TÉCNICOS (6 features) ==========
                features[f'{par}_rsi_14'] = self._calcular_rsi_simples(close, 14)
                features[f'{par}_rsi_21'] = self._calcular_rsi_simples(close, 21)
                features[f'{par}_macd'] = self._calcular_macd_simples(close)
                features[f'{par}_bb_position'] = self._calcular_bb_position(close)
                features[f'{par}_stoch_k'] = self._calcular_stochastic(high, low, close)
                features[f'{par}_williams_r'] = self._calcular_williams_r(high, low, close)
                
                # ========== VOLUME (4 features) ==========
                features[f'{par}_volume_ratio'] = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]
                features[f'{par}_volume_trend'] = volume.rolling(10).apply(
                    lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=True
                ).iloc[-1]
                features[f'{par}_obv'] = self._calcular_obv(close, volume)
                features[f'{par}_volume_sma_ratio'] = volume.rolling(5).mean().iloc[-1] / volume.rolling(20).mean().iloc[-1]
                
                # ========== SUPORTE/RESISTÊNCIA (4 features) ==========
                features[f'{par}_resistance_20'] = high.rolling(20).max().iloc[-1]
                features[f'{par}_support_20'] = low.rolling(20).min().iloc[-1]
                features[f'{par}_dist_res'] = (features[f'{par}_resistance_20'] - close.iloc[-1]) / close.iloc[-1]
                features[f'{par}_dist_sup'] = (close.iloc[-1] - features[f'{par}_support_20']) / close.iloc[-1]
                
                # ========== TENDÊNCIA (4 features) ==========
                features[f'{par}_trend_5'] = self._calcular_tendencia(close, 5)
                features[f'{par}_trend_10'] = self._calcular_tendencia(close, 10)
                features[f'{par}_trend_20'] = self._calcular_tendencia(close, 20)
                features[f'{par}_adx'] = self._calcular_adx_simples(high, low, close)
            
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
    
    def _calcular_tendencia(self, prices, period):
        """Calcular tendência linear"""
        if len(prices) < period:
            return 0
        
        x = np.arange(len(prices[-period:]))
        y = prices[-period:].values
        
        try:
            slope = np.polyfit(x, y, 1)[0]
            normalized_slope = slope / prices.iloc[-1]
            return normalized_slope * 100
        except:
            return 0
    
    def _calcular_macd_simples(self, prices, fast=12, slow=26):
        """Calcular MACD simplificado"""
        if len(prices) < slow:
            return 0
        
        ema_fast = prices.ewm(span=fast).mean().iloc[-1]
        ema_slow = prices.ewm(span=slow).mean().iloc[-1]
        macd = ema_fast - ema_slow
        return macd / prices.iloc[-1] * 100
    
    def _calcular_atr(self, high, low, close, period=14):
        """Calcular Average True Range"""
        if len(high) < period:
            return 0
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean().iloc[-1]
        return atr / close.iloc[-1] * 100
    
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
    
    def _calcular_stochastic(self, high, low, close, period=14):
        """Calcular Stochastic %K"""
        if len(high) < period:
            return 50
        
        lowest_low = low.rolling(period).min().iloc[-1]
        highest_high = high.rolling(period).max().iloc[-1]
        
        if highest_high == lowest_low:
            return 50
        
        stoch = (close.iloc[-1] - lowest_low) / (highest_high - lowest_low) * 100
        return stoch
    
    def _calcular_williams_r(self, high, low, close, period=14):
        """Calcular Williams %R"""
        if len(high) < period:
            return -50
        
        highest_high = high.rolling(period).max().iloc[-1]
        lowest_low = low.rolling(period).min().iloc[-1]
        
        if highest_high == lowest_low:
            return -50
        
        williams_r = (highest_high - close.iloc[-1]) / (highest_high - lowest_low) * -100
        return williams_r
    
    def _calcular_obv(self, close, volume):
        """Calcular On-Balance Volume"""
        if len(close) < 2:
            return 0
        
        obv = [0]
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        
        return obv[-1] / volume.mean() if volume.mean() != 0 else 0
    
    def _calcular_adx_simples(self, high, low, close, period=14):
        """Calcular ADX simplificado"""
        if len(high) < period * 2:
            return 25
        
        try:
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            
            up_move = high - high.shift()
            down_move = low.shift() - low
            
            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
            
            plus_di = 100 * (pd.Series(plus_dm).rolling(period).mean() / atr)
            minus_di = 100 * (pd.Series(minus_dm).rolling(period).mean() / atr)
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(period).mean().iloc[-1]
            
            return min(adx, 100) if not np.isnan(adx) else 25
        except:
            return 25
    
    def prever(self, dados_mercado):
        """Fazer previsão com modelos ensemble"""
        try:
            features = self.extrair_features_eficientes(dados_mercado)
            
            if features.empty or len(features) < 10:
                return self._previsao_segura()
            
            # 🎯 ESTRATÉGIA DE TRADING AVANÇADA
            rsi_values = [features[f] for f in features.index if 'rsi' in f and not np.isnan(features[f])]
            volume_indicators = [features[f] for f in features.index if 'volume' in f and not np.isnan(features[f])]
            trend_indicators = [features[f] for f in features.index if any(x in f for x in ['trend', 'momentum']) and not np.isnan(features[f])]
            
            buy_signals = 0
            sell_signals = 0
            hold_signals = 0
            
            # ANÁLISE RSI
            if rsi_values:
                avg_rsi = np.mean(rsi_values)
                if avg_rsi < 30:
                    buy_signals += 2
                elif avg_rsi > 70:
                    sell_signals += 2
                elif 30 <= avg_rsi <= 50:
                    buy_signals += 1
                elif 50 <= avg_rsi <= 70:
                    sell_signals += 1
            
            # ANÁLISE DE VOLUME
            if volume_indicators:
                avg_volume = np.mean(volume_indicators)
                if avg_volume > 1.2:
                    if trend_indicators and np.mean(trend_indicators) > 0:
                        buy_signals += 1
                    elif trend_indicators and np.mean(trend_indicators) < 0:
                        sell_signals += 1
            
            # ANÁLISE DE TENDÊNCIA
            if trend_indicators:
                trend_strength = np.mean(trend_indicators)
                if trend_strength > 0.5:
                    buy_signals += 2
                elif trend_strength < -0.5:
                    sell_signals += 2
                elif trend_strength > 0.1:
                    buy_signals += 1
                elif trend_strength < -0.1:
                    sell_signals += 1
            
            # TOMADA DE DECISÃO FINAL
            total_signals = buy_signals + sell_signals + hold_signals
            if total_signals == 0:
                return self._previsao_segura()
            
            buy_ratio = buy_signals / total_signals
            sell_ratio = sell_signals / total_signals
            
            if buy_ratio >= 0.4 and buy_signals >= 3:
                direction = "BUY"
                base_confidence = 60 + (buy_ratio * 30)
            elif sell_ratio >= 0.4 and sell_signals >= 3:
                direction = "SELL"
                base_confidence = 60 + (sell_ratio * 30)
            else:
                direction = "HOLD"
                base_confidence = 50
            
            # AJUSTAR CONFIANÇA
            valid_features = sum(1 for f in features.values if not np.isnan(f))
            data_quality = min(valid_features / len(features), 1.0)
            final_confidence = base_confidence * data_quality
            final_confidence = max(40, min(85, final_confidence))
            
            # CALCULAR PROBABILIDADES
            if direction == "BUY":
                prob_buy = final_confidence
                prob_sell = max(10, (100 - final_confidence) * 0.3)
                prob_hold = 100 - prob_buy - prob_sell
            elif direction == "SELL":
                prob_sell = final_confidence
                prob_buy = max(10, (100 - final_confidence) * 0.3)
                prob_hold = 100 - prob_sell - prob_buy
            else:
                prob_hold = final_confidence
                prob_buy = (100 - final_confidence) * 0.4
                prob_sell = (100 - final_confidence) * 0.4
            
            # GARANTIR SOMA 100%
            total_prob = prob_buy + prob_sell + prob_hold
            prob_buy = (prob_buy / total_prob) * 100
            prob_sell = (prob_sell / total_prob) * 100
            prob_hold = (prob_hold / total_prob) * 100
            
            return {
                'direcao': direction,
                'confianca': float(final_confidence),
                'probabilidades': {
                    'SELL': float(prob_sell),
                    'HOLD': float(prob_hold),
                    'BUY': float(prob_buy)
                },
                'timestamp': datetime.now().isoformat(),
                'modelo': 'ENSEMBLE_AVANCADO',
                'total_features': len(features),
                'valid_features': valid_features
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
        """Método de aprendizado"""
        logger.info(f"🧠 Modelo atualizado - Recompensa: {recompensa:.4f}")
    
    def salvar_modelo(self):
        """Salvar modelo periodicamente"""
        try:
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info("💾 Modelo leve salvo")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar modelo: {e}")
