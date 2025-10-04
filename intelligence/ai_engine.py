import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger('AIEngine')

class AIEngine:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.historical_data = []
        self.performance_history = []
        
        # Carregar ou criar modelo
        self._load_or_create_model()
        logger.info("✅ IA ENGINE INICIALIZADA")
    
    def _load_or_create_model(self):
        """Carregar modelo existente ou criar novo"""
        try:
            if os.path.exists('models/ai_model.pkl'):
                self.model = joblib.load('models/ai_model.pkl')
                self.is_trained = True
                logger.info("✅ MODELO DE IA CARREGADO")
            else:
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                logger.info("✅ NOVO MODELO DE IA CRIADO")
        except Exception as e:
            logger.error(f"❌ ERRO AO CARREGAR MODELO: {e}")
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def calcular_indicadores_avancados(self, df):
        """Calcular indicadores técnicos avançados"""
        try:
            # Preço
            df['returns'] = df['close'].pct_change()
            df['volatility'] = df['returns'].rolling(window=20).std()
            
            # Médias Móveis
            for period in [9, 21, 50, 200]:
                df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
                df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            
            # RSI
            df['rsi'] = self._calcular_rsi(df['close'])
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_hist'] = self._calcular_macd(df['close'])
            
            # Bollinger Bands
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = self._calcular_bollinger_bands(df['close'])
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # ATR
            df['atr'] = self._calcular_atr(df)
            
            # Volume Indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['obv'] = self._calcular_obv(df)
            
            # Momentum
            df['momentum'] = df['close'] / df['close'].shift(5) - 1
            df['stoch_k'], df['stoch_d'] = self._calcular_stochastic(df)
            df['williams_r'] = self._calcular_williams_r(df)
            
            # Suporte/Resistência
            df['resistance'] = df['high'].rolling(window=20).max()
            df['support'] = df['low'].rolling(window=20).min()
            df['distance_to_resistance'] = (df['resistance'] - df['close']) / df['close']
            df['distance_to_support'] = (df['close'] - df['support']) / df['close']
            
            # Padrões de Candlestick
            df['doji'] = self._detectar_doji(df)
            df['hammer'] = self._detectar_hammer(df)
            df['engulfing'] = self._detectar_engulfing(df)
            
            return df.fillna(method='bfill')
            
        except Exception as e:
            logger.error(f"❌ ERRO NOS INDICADORES: {e}")
            return df
    
    def _calcular_rsi(self, prices, period=14):
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calcular_macd(self, prices, fast=12, slow=26, signal=9):
        """Calcular MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def _calcular_bollinger_bands(self, prices, period=20, std=2):
        """Calcular Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()
        upper = sma + (rolling_std * std)
        lower = sma - (rolling_std * std)
        return upper, sma, lower
    
    def _calcular_atr(self, df, period=14):
        """Calcular ATR"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = np.maximum(np.maximum(high_low, high_close), low_close)
        return true_range.rolling(window=period).mean()
    
    def _calcular_obv(self, df):
        """Calcular OBV"""
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        return obv
    
    def _calcular_stochastic(self, df, k_period=14, d_period=3):
        """Calcular Stochastic"""
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
        stoch_d = stoch_k.rolling(window=d_period).mean()
        return stoch_k, stoch_d
    
    def _calcular_williams_r(self, df, period=14):
        """Calcular Williams %R"""
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        return -100 * (highest_high - df['close']) / (highest_high - lowest_low)
    
    def _detectar_doji(self, df, threshold=0.1):
        """Detectar padrão Doji"""
        body = np.abs(df['close'] - df['open'])
        range = df['high'] - df['low']
        return (body / range) < threshold
    
    def _detectar_hammer(self, df):
        """Detectar padrão Hammer"""
        body = np.abs(df['close'] - df['open'])
        lower_wick = np.minimum(df['open'], df['close']) - df['low']
        upper_wick = df['high'] - np.maximum(df['open'], df['close'])
        return (lower_wick > 2 * body) & (upper_wick < body)
    
    def _detectar_engulfing(self, df):
        """Detectar padrão Engulfing"""
        prev_body = np.abs(df['close'].shift(1) - df['open'].shift(1))
        curr_body = np.abs(df['close'] - df['open'])
        bull_engulfing = (df['close'] > df['open']) & (df['close'].shift(1) < df['open'].shift(1)) & (curr_body > prev_body)
        bear_engulfing = (df['close'] < df['open']) & (df['close'].shift(1) > df['open'].shift(1)) & (curr_body > prev_body)
        return bull_engulfing | bear_engulfing
    
    def preparar_features(self, df):
        """Preparar features para o modelo de IA"""
        try:
            feature_columns = [
                'returns', 'volatility', 'rsi', 'macd', 'macd_hist',
                'bb_position', 'bb_width', 'atr', 'volume_ratio', 'obv',
                'momentum', 'stoch_k', 'stoch_d', 'williams_r',
                'distance_to_resistance', 'distance_to_support',
                'doji', 'hammer', 'engulfing'
            ]
            
            # Adicionar EMAs
            for period in [9, 21, 50]:
                df[f'ema_{period}_ratio'] = df['close'] / df[f'ema_{period}']
                feature_columns.append(f'ema_{period}_ratio')
            
            features = df[feature_columns].fillna(0)
            
            # Normalizar features
            if not hasattr(self.scaler, 'mean_'):
                self.scaler.fit(features)
            
            return self.scaler.transform(features)
            
        except Exception as e:
            logger.error(f"❌ ERRO AO PREPARAR FEATURES: {e}")
            return np.zeros((len(df), 10))  # Fallback
    
    def analisar_mercado(self, dados_mercado):
        """Analisar mercado com IA avançada"""
        sinais = []
        
        for par, timeframes in dados_mercado.items():
            try:
                if timeframes is None:
                    continue
                
                # Usar múltiplos timeframes para análise
                df_15m = timeframes.get('15m')
                df_1h = timeframes.get('1h')
                
                if df_15m is None or len(df_15m) < 100:
                    continue
                
                # Calcular indicadores avançados
                df_analise = self.calcular_indicadores_avancados(df_15m.copy())
                
                # Preparar features para IA
                features = self.preparar_features(df_analise)
                
                # Fazer previsão com IA
                if self.is_trained and len(features) > 0:
                    prediction = self.model.predict_proba(features[-1].reshape(1, -1))[0]
                    confidence = np.max(prediction)
                    direction = np.argmax(prediction)  # 0: SELL, 1: HOLD, 2: BUY
                    
                    # Mapear para direção
                    if direction == 2 and confidence > 0.65:  # BUY
                        sinal = {
                            'par': par,
                            'direcao': 'BUY',
                            'confianca': confidence * 100,
                            'preco': df_analise['close'].iloc[-1],
                            'timestamp': datetime.now().isoformat(),
                            'estrategia': 'IA_AVANCADA'
                        }
                        sinais.append(sinal)
                        
                    elif direction == 0 and confidence > 0.65:  # SELL
                        sinal = {
                            'par': par,
                            'direcao': 'SELL', 
                            'confianca': confidence * 100,
                            'preco': df_analise['close'].iloc[-1],
                            'timestamp': datetime.now().isoformat(),
                            'estrategia': 'IA_AVANCADA'
                        }
                        sinais.append(sinal)
                
                logger.info(f"🔍 {par} - Confiança: {confidence:.2f}")
                
            except Exception as e:
                logger.error(f"❌ ERRO NA ANÁLISE {par}: {e}")
                continue
        
        return sinais
    
    def atualizar_modelo(self, X, y):
        """Atualizar modelo com novos dados (aprendizado contínuo)"""
        try:
            if self.is_trained:
                self.model.partial_fit(X, y)
            else:
                self.model.fit(X, y)
                self.is_trained = True
            
            # Salvar modelo atualizado
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, 'models/ai_model.pkl')
            logger.info("✅ MODELO DE IA ATUALIZADO")
            
        except Exception as e:
            logger.error(f"❌ ERRO AO ATUALIZAR MODELO: {e}")
