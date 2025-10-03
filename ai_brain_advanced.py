# ai_brain_advanced.py - SISTEMA DE IA AVANÇADO SEM PANDAS-TA
import pandas as pd
import numpy as np
import logging
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime
import os
from config import BOT_CONFIG, LOG_CONFIG

class AIBrainAdvanced:
    """
    Sistema de IA avançado para análise de mercado
    Usa múltiplos indicadores técnicos calculados manualmente
    """
    
    def __init__(self):
        self.config = BOT_CONFIG
        self.logger = self.setup_logger()
        self.scaler = StandardScaler()
        self.model = None
        self.feature_columns = []
        self.model_trained = False
        self.performance_history = []
        
        # Criar diretório de modelos
        os.makedirs('models', exist_ok=True)
        
        self.load_or_train_model()
        
    def setup_logger(self):
        """Configura logger para IA"""
        logger = logging.getLogger('AIBrainAdvanced')
        if LOG_CONFIG['log_colors']:
            formatter = logging.Formatter('\033[94m%(asctime)s\033[0m \033[95m%(levelname)s\033[0m \033[92m%(message)s\033[0m')
        else:
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
        
        return logger

    def calculate_rsi(self, prices, period=14):
        """Calcula RSI manualmente"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_ema(self, prices, period):
        """Calcula EMA manualmente"""
        return prices.ewm(span=period, adjust=False).mean()

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calcula MACD manualmente"""
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calcula Bollinger Bands manualmente"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band

    def calculate_atr(self, high, low, close, period=14):
        """Calcula Average True Range manualmente"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def calculate_stochastic(self, high, low, close, k_period=14, d_period=3):
        """Calcula Stochastic Oscillator manualmente"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        stoch_d = stoch_k.rolling(window=d_period).mean()
        return stoch_k, stoch_d

    def calculate_obv(self, close, volume):
        """Calcula On Balance Volume manualmente"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv

    def calculate_cci(self, high, low, close, period=14):
        """Calcula Commodity Channel Index manualmente"""
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=False)
        cci = (tp - sma_tp) / (0.015 * mad)
        return cci

    def calculate_williams_r(self, high, low, close, period=14):
        """Calcula Williams %R manualmente"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
        return williams_r

    def load_or_train_model(self):
        """Carrega modelo existente ou treina novo"""
        try:
            model_path = 'models/ai_model.pkl'
            scaler_path = 'models/scaler.pkl'
            features_path = 'models/feature_columns.pkl'
            
            if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(features_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.feature_columns = joblib.load(features_path)
                self.model_trained = True
                self.logger.info("✅ MODELO DE IA CARREGADO COM SUCESSO")
            else:
                self.logger.warning("🔄 MODELO NÃO ENCONTRADO, TREINANDO NOVO MODELO...")
                self.train_initial_model()
                
        except Exception as e:
            self.logger.error(f"❌ ERRO AO CARREGAR MODELO: {e}")
            self.logger.info("🔄 TREINANDO NOVO MODELO...")
            self.train_initial_model()

    def train_initial_model(self):
        """Treina modelo inicial com dados sintéticos"""
        try:
            self.logger.info("🤖 INICIANDO TREINAMENTO DO MODELO DE IA...")
            
            # Gerar dados sintéticos realistas
            n_samples = 3000
            n_features = 20
            
            np.random.seed(42)
            X = np.random.randn(n_samples, n_features)
            
            # Gerar labels inteligentes
            y = np.zeros(n_samples, dtype=int)
            
            for i in range(n_samples):
                # Simular condições de mercado
                trend_strength = X[i, 0]
                momentum = X[i, 1]
                volatility = X[i, 2]
                volume_strength = X[i, 3]
                
                # Regras para sinais
                buy_signals = 0
                sell_signals = 0
                
                if trend_strength > 0.5 and momentum > 0:
                    buy_signals += 1
                if trend_strength < -0.5 and momentum < 0:
                    sell_signals += 1
                if volatility < 0.3 and volume_strength > 0.5:
                    buy_signals += 1
                if volatility > 0.7 and volume_strength < -0.5:
                    sell_signals += 1
                
                # Determinar label
                if buy_signals >= 2:
                    y[i] = 2  # BUY
                elif sell_signals >= 2:
                    y[i] = 0  # SELL
                else:
                    y[i] = 1  # HOLD
            
            # Treinar modelo
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=42
            )
            
            # Split treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Treinar
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            self.model.fit(X_train_scaled, y_train)
            
            # Avaliar
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(self.scaler.transform(X_test), y_test)
            
            self.feature_columns = [f'feature_{i}' for i in range(n_features)]
            
            # Salvar modelo
            joblib.dump(self.model, 'models/ai_model.pkl')
            joblib.dump(self.scaler, 'models/scaler.pkl')
            joblib.dump(self.feature_columns, 'models/feature_columns.pkl')
            
            self.model_trained = True
            
            self.logger.info(f"✅ MODELO TREINADO COM SUCESSO!")
            self.logger.info(f"📊 Accuracy - Treino: {train_score:.3f} | Teste: {test_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO TREINAMENTO: {e}")
            self.model_trained = False

    def calculate_technical_indicators(self, df):
        """Calcula indicadores técnicos avançados manualmente"""
        try:
            if df.empty or len(df) < 50:
                self.logger.warning("⚠️ DADOS INSUFICIENTES PARA ANÁLISE")
                return None
            
            high = df['high']
            low = df['low']
            close = df['close']
            volume = df['volume']
            
            indicators = {}
            
            # 🎯 TENDÊNCIA
            indicators['sma_10'] = close.rolling(10).mean().iloc[-1]
            indicators['sma_20'] = close.rolling(20).mean().iloc[-1]
            indicators['sma_50'] = close.rolling(50).mean().iloc[-1]
            indicators['ema_12'] = self.calculate_ema(close, 12).iloc[-1]
            indicators['ema_26'] = self.calculate_ema(close, 26).iloc[-1]
            
            # 📈 MOMENTO
            indicators['rsi'] = self.calculate_rsi(close, 14).iloc[-1]
            
            macd_line, signal_line, histogram = self.calculate_macd(close)
            indicators['macd'] = macd_line.iloc[-1]
            indicators['macd_signal'] = signal_line.iloc[-1]
            indicators['macd_hist'] = histogram.iloc[-1]
            
            # 📊 VOLATILIDADE
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close)
            indicators['bb_upper'] = bb_upper.iloc[-1]
            indicators['bb_middle'] = bb_middle.iloc[-1]
            indicators['bb_lower'] = bb_lower.iloc[-1]
            indicators['bb_position'] = (close.iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
            
            indicators['atr'] = self.calculate_atr(high, low, close).iloc[-1]
            
            # 📈 VOLUME
            indicators['volume_sma'] = volume.rolling(20).mean().iloc[-1]
            indicators['volume_ratio'] = volume.iloc[-1] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 1
            indicators['obv'] = self.calculate_obv(close, volume).iloc[-1]
            
            # 🎯 PRICE ACTION
            indicators['price_vs_sma20'] = close.iloc[-1] / indicators['sma_20'] if indicators['sma_20'] > 0 else 1
            indicators['high_low_ratio'] = high.iloc[-1] / low.iloc[-1] if low.iloc[-1] > 0 else 1
            indicators['body_size'] = abs(close.iloc[-1] - df['open'].iloc[-1]) / (high.iloc[-1] - low.iloc[-1]) if (high.iloc[-1] - low.iloc[-1]) > 0 else 0
            
            # 🔄 MOMENTUM AVANÇADO
            stoch_k, stoch_d = self.calculate_stochastic(high, low, close)
            indicators['stoch_k'] = stoch_k.iloc[-1]
            indicators['stoch_d'] = stoch_d.iloc[-1]
            indicators['williams_r'] = self.calculate_williams_r(high, low, close).iloc[-1]
            indicators['cci'] = self.calculate_cci(high, low, close).iloc[-1]
            
            # 🛡️ SUPORTE E RESISTÊNCIA
            recent_high = high.tail(20).max()
            recent_low = low.tail(20).min()
            indicators['price_vs_recent_high'] = close.iloc[-1] / recent_high if recent_high > 0 else 1
            indicators['price_vs_recent_low'] = close.iloc[-1] / recent_low if recent_low > 0 else 1
            
            # Validar valores
            for key, value in indicators.items():
                if np.isnan(value) or np.isinf(value):
                    indicators[key] = 0
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CÁLCULO DE INDICADORES: {e}")
            return None

    def create_feature_vector(self, indicators):
        """Cria vetor de features para o modelo"""
        try:
            if not indicators:
                return None
                
            feature_vector = [
                indicators.get('sma_10', 0),
                indicators.get('sma_20', 0),
                indicators.get('sma_50', 0),
                indicators.get('ema_12', 0),
                indicators.get('ema_26', 0),
                indicators.get('rsi', 50),
                indicators.get('macd', 0),
                indicators.get('macd_signal', 0),
                indicators.get('macd_hist', 0),
                indicators.get('bb_position', 0.5),
                indicators.get('price_vs_sma20', 1),
                indicators.get('high_low_ratio', 1),
                indicators.get('body_size', 0),
                indicators.get('atr', 0),
                indicators.get('volume_ratio', 1),
                indicators.get('stoch_k', 50),
                indicators.get('stoch_d', 50),
                indicators.get('williams_r', -50),
                indicators.get('cci', 0),
                indicators.get('price_vs_recent_high', 1),
            ]
            
            # Garantir tamanho correto e substituir NaN
            feature_vector = [0 if np.isnan(x) or np.isinf(x) else x for x in feature_vector]
            
            return np.array(feature_vector).reshape(1, -1)
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA CRIAÇÃO DO VETOR: {e}")
            return None

    def analyze_market_sentiment(self, df):
        """Analisa sentimento do mercado"""
        try:
            indicators = self.calculate_technical_indicators(df)
            if not indicators:
                return "HOLD", 0.5
                
            # Análise baseada em regras
            rule_based_signal, rule_confidence = self.rule_based_analysis(indicators)
            
            # Se modelo está treinado, usar ML
            if self.model_trained:
                feature_vector = self.create_feature_vector(indicators)
                if feature_vector is not None:
                    feature_vector_scaled = self.scaler.transform(feature_vector)
                    prediction = self.model.predict(feature_vector_scaled)[0]
                    probabilities = self.model.predict_proba(feature_vector_scaled)[0]
                    confidence = np.max(probabilities)
                    
                    signal_map = {0: "SELL", 1: "HOLD", 2: "BUY"}
                    ml_signal = signal_map[prediction]
                    
                    if confidence > self.config['min_confidence']:
                        return ml_signal, confidence
            
            return rule_based_signal, rule_confidence
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE: {e}")
            return "HOLD", 0.5

    def rule_based_analysis(self, indicators):
        """Análise baseada em regras técnicas"""
        try:
            buy_signals = 0
            sell_signals = 0
            
            # RSI
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                buy_signals += 1
            elif rsi > 70:
                sell_signals += 1
            
            # MACD
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if macd > macd_signal:
                buy_signals += 1
            else:
                sell_signals += 1
            
            # Bollinger Bands
            bb_position = indicators.get('bb_position', 0.5)
            if bb_position < 0.2:
                buy_signals += 1
            elif bb_position > 0.8:
                sell_signals += 1
            
            # Decidir sinal
            if buy_signals >= 2:
                return "BUY", 0.7
            elif sell_signals >= 2:
                return "SELL", 0.7
            else:
                return "HOLD", 0.5
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE POR REGRAS: {e}")
            return "HOLD", 0.5

    def multi_timeframe_analysis(self, multi_tf_data):
        """Análise multi-timeframe"""
        try:
            signals = {}
            confidences = {}
            
            for tf, data in multi_tf_data.items():
                signal, confidence = self.analyze_market_sentiment(data)
                signals[tf] = signal
                confidences[tf] = confidence
            
            # Contar sinais
            signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            for signal in signals.values():
                signal_counts[signal] += 1
            
            # Decisão consensual
            if signal_counts['BUY'] > signal_counts['SELL']:
                final_signal = "BUY"
            elif signal_counts['SELL'] > signal_counts['BUY']:
                final_signal = "SELL"
            else:
                final_signal = "HOLD"
            
            avg_confidence = np.mean(list(confidences.values())) if confidences else 0.5
            
            return final_signal, avg_confidence
            
        except Exception as e:
            self.logger.error(f"❌ ERRO ANÁLISE MULTI-TF: {e}")
            return "HOLD", 0.5

# Instância global
ai_brain = AIBrainAdvanced()
