# ai_brain_advanced.py - SISTEMA DE IA AVANÇADO COM PANDAS-TA
import pandas as pd
import numpy as np
import logging
import joblib
import pandas_ta as ta  # Alternativa ao talib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime
import os
from config import BOT_CONFIG, LOG_CONFIG

class AIBrainAdvanced:
    """
    Sistema de IA avançado para análise de mercado
    Usa múltiplos indicadores técnicos e machine learning com pandas-ta
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
                self.logger.info(f"📊 MODELO TREINADO COM {len(self.feature_columns)} FEATURES")
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
            
            # Gerar dados sintéticos realistas para treino
            n_samples = 3000
            n_features = 24
            
            np.random.seed(42)
            
            # Features mais realistas (simulando condições de mercado)
            X = np.zeros((n_samples, n_features))
            
            # Simular padrões de mercado
            for i in range(n_samples):
                # Tendência (features 0-4)
                X[i, 0] = np.random.normal(0, 1)  # SMA ratio
                X[i, 1] = np.random.normal(0, 0.5)  # EMA ratio
                X[i, 2] = np.random.normal(50, 15)  # RSI
                X[i, 3] = np.random.normal(0, 2)  # MACD
                X[i, 4] = np.random.normal(0, 1)  # MACD Hist
                
                # Volatilidade (features 5-9)
                X[i, 5] = np.random.normal(1, 0.1)  # BB Position
                X[i, 6] = np.random.normal(1, 0.2)  # Price vs SMA
                X[i, 7] = np.random.normal(1.01, 0.02)  # High/Low ratio
                X[i, 8] = np.random.normal(0.5, 0.2)  # Body size
                X[i, 9] = np.random.normal(1, 0.3)  # ATR ratio
                
                # Volume (features 10-11)
                X[i, 10] = np.random.normal(1, 0.5)  # Volume ratio
                X[i, 11] = np.random.normal(0, 100000)  # OBV
                
                # Momentum (features 12-15)
                X[i, 12] = np.random.normal(50, 20)  # Stoch K
                X[i, 13] = np.random.normal(50, 20)  # Stoch D
                X[i, 14] = np.random.normal(-50, 30)  # Williams R
                X[i, 15] = np.random.normal(0, 100)  # CCI
                
                # Suporte/Resistência (features 16-17)
                X[i, 16] = np.random.normal(1, 0.1)  # Price vs Recent High
                X[i, 17] = np.random.normal(1, 0.1)  # Price vs Recent Low
                
                # Features adicionais (18-23)
                X[i, 18] = np.random.normal(0, 1)  # Trend strength
                X[i, 19] = np.random.normal(0, 0.5)  # Volatility
                X[i, 20] = np.random.normal(0, 1)  # Momentum strength
                X[i, 21] = np.random.normal(0.5, 0.2)  # Market regime
                X[i, 22] = np.random.normal(0, 1)  # Price acceleration
                X[i, 23] = np.random.normal(0, 0.3)  # Mean reversion
            
            # Gerar labels inteligentes baseados em padrões
            y = np.zeros(n_samples, dtype=int)
            
            for i in range(n_samples):
                buy_signals = 0
                sell_signals = 0
                
                # Regras para BUY
                if X[i, 2] < 35:  # RSI oversold
                    buy_signals += 1
                if X[i, 3] > X[i, 4] and X[i, 3] > 0:  # MACD positivo e acima do sinal
                    buy_signals += 1
                if X[i, 5] < 0.9:  # Preço perto da BB inferior
                    buy_signals += 1
                if X[i, 12] < 30 and X[i, 13] < 30:  # Stoch oversold
                    buy_signals += 1
                if X[i, 16] < 0.95:  # Preço longe da resistência
                    buy_signals += 1
                
                # Regras para SELL
                if X[i, 2] > 65:  # RSI overbought
                    sell_signals += 1
                if X[i, 3] < X[i, 4] and X[i, 3] < 0:  # MACD negativo e abaixo do sinal
                    sell_signals += 1
                if X[i, 5] > 1.1:  # Preço perto da BB superior
                    sell_signals += 1
                if X[i, 12] > 70 and X[i, 13] > 70:  # Stoch overbought
                    sell_signals += 1
                if X[i, 16] > 1.05:  # Preço perto da resistência
                    sell_signals += 1
                
                # Determinar label
                if buy_signals >= 3 and buy_signals > sell_signals:
                    y[i] = 2  # BUY
                elif sell_signals >= 3 and sell_signals > buy_signals:
                    y[i] = 0  # SELL
                else:
                    y[i] = 1  # HOLD
            
            # Balancear classes
            from sklearn.utils import class_weight
            class_weights = class_weight.compute_class_weight(
                class_weight='balanced',
                classes=np.unique(y),
                y=y
            )
            
            # Treinar modelo ensemble
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.08,
                max_depth=5,
                min_samples_split=25,
                min_samples_leaf=12,
                subsample=0.8,
                max_features='sqrt',
                random_state=42,
                validation_fraction=0.1,
                n_iter_no_change=10,
                tol=1e-4
            )
            
            # Split treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Treinar scaler
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model.fit(X_train_scaled, y_train)
            
            # Avaliar
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            # Feature importance
            feature_importance = self.model.feature_importances_
            top_features = np.argsort(feature_importance)[-5:][::-1]
            
            self.feature_columns = [f'feature_{i}' for i in range(n_features)]
            
            # Salvar modelo
            joblib.dump(self.model, 'models/ai_model.pkl')
            joblib.dump(self.scaler, 'models/scaler.pkl')
            joblib.dump(self.feature_columns, 'models/feature_columns.pkl')
            
            self.model_trained = True
            
            self.logger.info(f"✅ MODELO TREINADO COM SUCESSO!")
            self.logger.info(f"📊 Accuracy - Treino: {train_score:.3f} | Teste: {test_score:.3f}")
            self.logger.info(f"🎯 Distribuição - BUY: {np.sum(y==2)} | SELL: {np.sum(y==0)} | HOLD: {np.sum(y==1)}")
            self.logger.info(f"📈 Top 5 Features: {top_features}")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO TREINAMENTO: {e}")
            self.model_trained = False

    def calculate_technical_indicators(self, df):
        """Calcula indicadores técnicos avançados usando pandas-ta"""
        try:
            if df.empty or len(df) < 50:
                self.logger.warning("⚠️ DADOS INSUFICIENTES PARA ANÁLISE")
                return None
            
            high = df['high']
            low = df['low']
            close = df['close']
            volume = df['volume']
            
            indicators = {}
            
            # 🎯 TENDÊNCIA (usando pandas-ta)
            indicators['sma_10'] = ta.sma(close, length=10).iloc[-1]
            indicators['sma_20'] = ta.sma(close, length=20).iloc[-1]
            indicators['sma_50'] = ta.sma(close, length=50).iloc[-1]
            indicators['ema_12'] = ta.ema(close, length=12).iloc[-1]
            indicators['ema_26'] = ta.ema(close, length=26).iloc[-1]
            
            # 📈 MOMENTO
            indicators['rsi'] = ta.rsi(close, length=14).iloc[-1]
            
            macd_data = ta.macd(close, fast=12, slow=26, signal=9)
            if not macd_data.empty and 'MACD_12_26_9' in macd_data.columns:
                indicators['macd'] = macd_data['MACD_12_26_9'].iloc[-1]
                indicators['macd_signal'] = macd_data['MACDs_12_26_9'].iloc[-1]
                indicators['macd_hist'] = macd_data['MACDh_12_26_9'].iloc[-1]
            else:
                indicators['macd'] = 0
                indicators['macd_signal'] = 0
                indicators['macd_hist'] = 0
            
            # 📊 VOLATILIDADE
            bb_data = ta.bbands(close, length=20, std=2)
            if not bb_data.empty and 'BBU_20_2.0' in bb_data.columns:
                indicators['bb_upper'] = bb_data['BBU_20_2.0'].iloc[-1]
                indicators['bb_middle'] = bb_data['BBM_20_2.0'].iloc[-1]
                indicators['bb_lower'] = bb_data['BBL_20_2.0'].iloc[-1]
                # Posição relativa nas BB
                bb_position = (close.iloc[-1] - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
                indicators['bb_position'] = bb_position if not np.isnan(bb_position) else 0.5
            else:
                indicators['bb_upper'] = close.iloc[-1] * 1.1
                indicators['bb_middle'] = close.iloc[-1]
                indicators['bb_lower'] = close.iloc[-1] * 0.9
                indicators['bb_position'] = 0.5
            
            indicators['atr'] = ta.atr(high, low, close, length=14).iloc[-1]
            
            # 📈 VOLUME
            indicators['volume_sma'] = volume.rolling(20).mean().iloc[-1]
            indicators['volume_ratio'] = volume.iloc[-1] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 1
            
            obv_data = ta.obv(close, volume)
            indicators['obv'] = obv_data.iloc[-1] if not obv_data.empty else 0
            
            # 🎯 PRICE ACTION
            indicators['price_vs_sma20'] = close.iloc[-1] / indicators['sma_20'] if indicators['sma_20'] > 0 else 1
            indicators['high_low_ratio'] = high.iloc[-1] / low.iloc[-1] if low.iloc[-1] > 0 else 1
            indicators['body_size'] = abs(close.iloc[-1] - df['open'].iloc[-1]) / (high.iloc[-1] - low.iloc[-1]) if (high.iloc[-1] - low.iloc[-1]) > 0 else 0
            
            # 🔄 MOMENTUM AVANÇADO
            stoch_data = ta.stoch(high, low, close, k=14, d=3)
            if not stoch_data.empty and 'STOCHk_14_3_3' in stoch_data.columns:
                indicators['stoch_k'] = stoch_data['STOCHk_14_3_3'].iloc[-1]
                indicators['stoch_d'] = stoch_data['STOCHd_14_3_3'].iloc[-1]
            else:
                indicators['stoch_k'] = 50
                indicators['stoch_d'] = 50
            
            indicators['williams_r'] = ta.willr(high, low, close, length=14).iloc[-1]
            indicators['cci'] = ta.cci(high, low, close, length=14).iloc[-1]
            
            # 🛡️ SUPORTE E RESISTÊNCIA
            recent_high = high.tail(20).max()
            recent_low = low.tail(20).min()
            indicators['price_vs_recent_high'] = close.iloc[-1] / recent_high if recent_high > 0 else 1
            indicators['price_vs_recent_low'] = close.iloc[-1] / recent_low if recent_low > 0 else 1
            
            # 📊 INDICADORES ADICIONAIS
            # Força da tendência
            trend_strength = abs(indicators['sma_20'] - indicators['sma_50']) / indicators['sma_20'] if indicators['sma_20'] > 0 else 0
            indicators['trend_strength'] = trend_strength
            
            # Volatilidade relativa
            indicators['volatility'] = indicators['atr'] / close.iloc[-1] if close.iloc[-1] > 0 else 0
            
            # Força do momentum
            momentum_strength = abs(indicators['rsi'] - 50) / 50
            indicators['momentum_strength'] = momentum_strength
            
            # Regime de mercado
            if indicators['rsi'] > 60 and indicators['bb_position'] > 0.7:
                indicators['market_regime'] = 0.8  # Bullish
            elif indicators['rsi'] < 40 and indicators['bb_position'] < 0.3:
                indicators['market_regime'] = 0.2  # Bearish
            else:
                indicators['market_regime'] = 0.5  # Neutral
            
            # Aceleração de preço
            price_change_1 = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] if close.iloc[-2] > 0 else 0
            price_change_5 = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] if close.iloc[-6] > 0 else 0
            indicators['price_acceleration'] = price_change_1 - price_change_5
            
            # Mean reversion
            indicators['mean_reversion'] = (close.iloc[-1] - indicators['sma_20']) / indicators['sma_20'] if indicators['sma_20'] > 0 else 0
            
            # Validar valores NaN
            for key, value in indicators.items():
                if np.isnan(value) or np.isinf(value):
                    indicators[key] = 0
            
            self.logger.debug(f"📊 INDICADORES CALCULADOS: RSI={indicators['rsi']:.1f}, MACD={indicators['macd']:.3f}")
            
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
                # Tendência (0-4)
                indicators.get('sma_10', 0),
                indicators.get('sma_20', 0),
                indicators.get('sma_50', 0),
                indicators.get('ema_12', 0),
                indicators.get('ema_26', 0),
                
                # Momento (5-9)
                indicators.get('rsi', 50),
                indicators.get('macd', 0),
                indicators.get('macd_signal', 0),
                indicators.get('macd_hist', 0),
                indicators.get('bb_position', 0.5),
                
                # Volatilidade (10-14)
                indicators.get('price_vs_sma20', 1),
                indicators.get('high_low_ratio', 1),
                indicators.get('body_size', 0),
                indicators.get('atr', 0),
                indicators.get('volatility', 0),
                
                # Volume (15-16)
                indicators.get('volume_ratio', 1),
                indicators.get('obv', 0),
                
                # Momentum Avançado (17-20)
                indicators.get('stoch_k', 50),
                indicators.get('stoch_d', 50),
                indicators.get('williams_r', -50),
                indicators.get('cci', 0),
                
                # Suporte/Resistência (21-22)
                indicators.get('price_vs_recent_high', 1),
                indicators.get('price_vs_recent_low', 1),
                
                # Indicadores Adicionais (23-26)
                indicators.get('trend_strength', 0),
                indicators.get('momentum_strength', 0),
                indicators.get('market_regime', 0.5),
                indicators.get('price_acceleration', 0),
                indicators.get('mean_reversion', 0),
            ]
            
            # Garantir que temos exatamente 24 features
            if len(feature_vector) != 24:
                self.logger.warning(f"⚠️ VETOR DE FEATURES COM TAMANHO {len(feature_vector)}, ESPERADO 24")
                # Preencher ou truncar para 24
                if len(feature_vector) < 24:
                    feature_vector.extend([0] * (24 - len(feature_vector)))
                else:
                    feature_vector = feature_vector[:24]
            
            # Substituir NaN por 0
            feature_vector = [0 if np.isnan(x) or np.isinf(x) else x for x in feature_vector]
            
            return np.array(feature_vector).reshape(1, -1)
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA CRIAÇÃO DO VETOR: {e}")
            return None

    def analyze_market_sentiment(self, df):
        """Analisa sentimento do mercado baseado em múltiplos fatores"""
        try:
            self.logger.info("🧠 INICIANDO ANÁLISE DE SENTIMENTO...")
            
            indicators = self.calculate_technical_indicators(df)
            if not indicators:
                self.logger.warning("⚠️ INDICADORES NÃO DISPONÍVEIS")
                return "HOLD", 0.5
                
            # Análise baseada em regras (fallback)
            rule_based_signal, rule_confidence = self.rule_based_analysis(indicators)
            
            # Se modelo está treinado, usar ML
            if self.model_trained:
                ml_signal, ml_confidence = self.ml_analysis(indicators)
                
                # Combinar sinais - preferir ML se confiança alta
                if ml_confidence > self.config['min_confidence']:
                    final_signal = ml_signal
                    final_confidence = ml_confidence
                    signal_source = "ML"
                else:
                    final_signal = rule_based_signal
                    final_confidence = rule_confidence
                    signal_source = "RULE"
            else:
                final_signal = rule_based_signal
                final_confidence = rule_confidence
                signal_source = "RULE"
            
            # Registrar performance
            self.record_analysis_performance(final_signal, final_confidence, signal_source)
            
            self.logger.info(f"🎯 ANÁLISE CONCLUÍDA: {final_signal} | Conf: {final_confidence:.1%} | Fonte: {signal_source}")
            return final_signal, final_confidence
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE: {e}")
            return "HOLD", 0.5

    def ml_analysis(self, indicators):
        """Análise usando machine learning"""
        try:
            feature_vector = self.create_feature_vector(indicators)
            if feature_vector is None:
                return "HOLD", 0.5
                
            # Escalar features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Fazer predição
            prediction = self.model.predict(feature_vector_scaled)[0]
            probabilities = self.model.predict_proba(feature_vector_scaled)[0]
            confidence = np.max(probabilities)
            
            # Mapear predição para sinal
            signal_map = {0: "SELL", 1: "HOLD", 2: "BUY"}
            signal = signal_map[prediction]
            
            # Log detalhado
            self.logger.debug(f"🤖 ML - Pred: {prediction}, Probs: {probabilities}, Conf: {confidence:.3f}")
            
            return signal, confidence
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE ML: {e}")
            return "HOLD", 0.5

    def rule_based_analysis(self, indicators):
        """Análise baseada em regras técnicas (fallback)"""
        try:
            buy_signals = 0
            sell_signals = 0
            total_signals = 0
            
            # RSI
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                buy_signals += 1
                total_signals += 1
            elif rsi > 70:
                sell_signals += 1
                total_signals += 1
            
            # MACD
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if macd > macd_signal and macd > 0:
                buy_signals += 1
                total_signals += 1
            elif macd < macd_signal and macd < 0:
                sell_signals += 1
                total_signals += 1
            
            # Bollinger Bands
            bb_position = indicators.get('bb_position', 0.5)
            if bb_position < 0.2:
                buy_signals += 1
                total_signals += 1
            elif bb_position > 0.8:
                sell_signals += 1
                total_signals += 1
            
            # Stochastic
            stoch_k = indicators.get('stoch_k', 50)
            stoch_d = indicators.get('stoch_d', 50)
            if stoch_k < 20 and stoch_d < 20:
                buy_signals += 1
                total_signals += 1
            elif stoch_k > 80 and stoch_d > 80:
                sell_signals += 1
                total_signals += 1
            
            # Tendência
            price_vs_sma = indicators.get('price_vs_sma20', 1)
            if price_vs_sma > 1.02:
                buy_signals += 1
                total_signals += 1
            elif price_vs_sma < 0.98:
                sell_signals += 1
                total_signals += 1
            
            # Calcular confiança baseada em concordância
            if total_signals > 0:
                if buy_signals > sell_signals:
                    confidence = buy_signals / total_signals
                    signal = "BUY"
                elif sell_signals > buy_signals:
                    confidence = sell_signals / total_signals
                    signal = "SELL"
                else:
                    signal = "HOLD"
                    confidence = 0.5
            else:
                signal = "HOLD"
                confidence = 0.5
            
            self.logger.debug(f"📋 RULE-BASED - Buy: {buy_signals}, Sell: {sell_signals}, Total: {total_signals}")
            
            return signal, confidence
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE POR REGRAS: {e}")
            return "HOLD", 0.5

    def multi_timeframe_analysis(self, multi_tf_data):
        """Análise consensual multi-timeframe"""
        try:
            signals = {}
            confidences = {}
            
            self.logger.info("🕒 INICIANDO ANÁLISE MULTI-TIMEFRAME...")
            
            for tf, data in multi_tf_data.items():
                signal, confidence = self.analyze_market_sentiment(data)
                signals[tf] = signal
                confidences[tf] = confidence
                self.logger.debug(f"   {tf}: {signal} ({confidence:.1%})")
            
            # Contar sinais
            signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            for signal in signals.values():
                signal_counts[signal] += 1
            
            # Calcular confiança média ponderada (timeframes maiores tem mais peso)
            tf_weights = {'1m': 0.5, '5m': 1.0, '15m': 1.5, '1h': 2.0, '4h': 2.5}
            weighted_confidences = []
            
            for tf, confidence in confidences.items():
                weight = tf_weights.get(tf, 1.0)
                weighted_confidences.append(confidence * weight)
            
            avg_confidence = np.mean(weighted_confidences) if weighted_confidences else 0.5
            
            # Decisão consensual
            if signal_counts['BUY'] > signal_counts['SELL'] and signal_counts['BUY'] >= signal_counts['HOLD']:
                final_signal = "BUY"
            elif signal_counts['SELL'] > signal_counts['BUY'] and signal_counts['SELL'] >= signal_counts['HOLD']:
                final_signal = "SELL"
            else:
                final_signal = "HOLD"
            
            self.logger.info(f"🎯 CONSENSO MULTI-TF: {final_signal}")
            self.logger.info(f"   📊 BUY: {signal_counts['BUY']} | SELL: {signal_counts['SELL']} | HOLD: {signal_counts['HOLD']}")
            self.logger.info(f"   📈 Confiança: {avg_confidence:.1%}")
            
            return final_signal, avg_confidence
            
        except Exception as e:
            self.logger.error(f"❌ ERRO ANÁLISE MULTI-TF: {e}")
            return "HOLD", 0.5

    def record_analysis_performance(self, signal, confidence, source):
        """Registra performance da análise para melhoria contínua"""
        try:
            analysis_data = {
                'timestamp': datetime.now(),
                'signal': signal,
                'confidence': confidence,
                'source': source
            }
            
            self.performance_history.append(analysis_data)
            
            # Manter apenas últimas 500 análises
            if len(self.performance_history) > 500:
                self.performance_history = self.performance_history[-500:]
                
        except Exception as e:
            self.logger.error(f"❌ ERRO AO REGISTRAR PERFORMANCE: {e}")

    def get_analysis_stats(self):
        """Retorna estatísticas das análises realizadas"""
        try:
            if not self.performance_history:
                return "Nenhuma análise registrada"
            
            df = pd.DataFrame(self.performance_history)
            
            stats = {
                'total_analyses': len(df),
                'buy_signals': len(df[df['signal'] == 'BUY']),
                'sell_signals': len(df[df['signal'] == 'SELL']),
                'hold_signals': len(df[df['signal'] == 'HOLD']),
                'avg_confidence': df['confidence'].mean(),
                'ml_analyses': len(df[df['source'] == 'ML']),
                'rule_analyses': len(df[df['source'] == 'RULE']),
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER ESTATÍSTICAS: {e}")
            return {}

# Instância global
ai_brain = AIBrainAdvanced()
