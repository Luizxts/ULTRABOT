import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

logger = logging.getLogger('EvolutionaryAI')

class EvolutionaryAI:
    def __init__(self):
        self.model = None
        self.learning_data = []
        self.performance_history = []
        self.adaptation_threshold = 0.65
        self.retrain_interval = 100  # Número de trades para retreinar
        
        self._initialize_model()
        logger.info("✅ IA EVOLUCIONÁRIA INICIALIZADA")
    
    def _initialize_model(self):
        """Inicializar ou carregar modelo existente"""
        try:
            if os.path.exists('models/evolutionary_model.pkl'):
                self.model = joblib.load('models/evolutionary_model.pkl')
                logger.info("✅ MODELO EVOLUCIONÁRIO CARREGADO")
            else:
                self.model = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=15,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
                logger.info("✅ NOVO MODELO EVOLUCIONÁRIO CRIADO")
        except Exception as e:
            logger.error(f"❌ ERRO AO CARREGAR MODELO: {e}")
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def extract_advanced_features(self, df):
        """Extrair features avançadas para aprendizado"""
        try:
            features = {}
            
            # Price Action Features
            features['price_change_1h'] = (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100
            features['price_change_4h'] = (df['close'].iloc[-1] / df['close'].iloc[-24] - 1) * 100
            features['high_low_ratio'] = df['high'].iloc[-1] / df['low'].iloc[-1] - 1
            
            # Volume Features
            features['volume_spike'] = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
            features['volume_trend'] = df['volume'].iloc[-6:].mean() / df['volume'].iloc[-12:-6].mean()
            
            # Volatility Features
            returns = df['close'].pct_change().dropna()
            features['volatility_1h'] = returns.iloc[-6:].std() * 100
            features['volatility_4h'] = returns.iloc[-24:].std() * 100
            
            # Technical Indicator Features
            features['rsi'] = self._calculate_rsi(df['close']).iloc[-1]
            features['rsi_trend'] = self._calculate_rsi(df['close']).iloc[-1] - self._calculate_rsi(df['close']).iloc[-6]
            
            # MACD Features
            macd, signal, _ = self._calculate_macd(df['close'])
            features['macd_value'] = macd.iloc[-1]
            features['macd_signal_diff'] = macd.iloc[-1] - signal.iloc[-1]
            features['macd_trend'] = macd.iloc[-1] - macd.iloc[-6]
            
            # Bollinger Bands Features
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['close'])
            features['bb_position'] = (df['close'].iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
            features['bb_squeeze'] = (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / bb_middle.iloc[-1]
            
            # Market Structure
            features['support_distance'] = (df['close'].iloc[-1] - df['low'].rolling(20).min().iloc[-1]) / df['close'].iloc[-1]
            features['resistance_distance'] = (df['high'].rolling(20).max().iloc[-1] - df['close'].iloc[-1]) / df['close'].iloc[-1]
            features['market_regime'] = self._detect_market_regime(df)
            
            # Time-based Features
            features['hour_of_day'] = datetime.now().hour
            features['day_of_week'] = datetime.now().weekday()
            
            return pd.Series(features)
            
        except Exception as e:
            logger.error(f"❌ ERRO NA EXTRAÇÃO DE FEATURES: {e}")
            return pd.Series()
    
    def _calculate_rsi(self, prices, period=14):
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calcular MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def _calculate_bollinger_bands(self, prices, period=20, std=2):
        """Calcular Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()
        upper = sma + (rolling_std * std)
        lower = sma - (rolling_std * std)
        return upper, sma, lower
    
    def _detect_market_regime(self, df):
        """Detectar regime de mercado"""
        volatility = df['close'].pct_change().std()
        trend_strength = abs(df['close'].iloc[-1] / df['close'].iloc[-20] - 1)
        
        if volatility > 0.02:  # 2% de volatilidade
            return 2  # Alta volatilidade
        elif trend_strength > 0.05:  # 5% de tendência
            return 1  # Tendência forte
        else:
            return 0  # Mercado lateral
    
    def analyze_market_conditions(self, dados_mercado):
        """Analisar condições de mercado com IA evolucionária"""
        analysis_results = {}
        
        for par, timeframes in dados_mercado.items():
            try:
                if timeframes is None:
                    continue
                
                df_15m = timeframes.get('15m')
                if df_15m is None or len(df_15m) < 50:
                    continue
                
                # Extrair features avançadas
                features = self.extract_advanced_features(df_15m)
                
                if features.empty:
                    continue
                
                # Fazer previsão se o modelo estiver treinado
                if hasattr(self.model, 'classes_'):
                    features_array = features.values.reshape(1, -1)
                    prediction_proba = self.model.predict_proba(features_array)[0]
                    prediction = self.model.predict(features_array)[0]
                    
                    # Mapear previsão para direção
                    direction_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
                    direction = direction_map.get(prediction, 'HOLD')
                    confidence = np.max(prediction_proba) * 100
                    
                    # Aplicar filtros de confiança
                    if confidence >= 70 and direction != 'HOLD':
                        analysis_results[par] = {
                            'direcao': direction,
                            'confianca': confidence,
                            'preco': df_15m['close'].iloc[-1],
                            'timestamp': datetime.now().isoformat(),
                            'estrategia': 'EVOLUTIONARY_AI',
                            'features': features.to_dict()
                        }
                        
                        logger.info(f"🎯 EVOLUTIONARY AI: {par} {direction} (Conf: {confidence:.1f}%)")
                
            except Exception as e:
                logger.error(f"❌ ERRO NA ANÁLISE EVOLUCIONÁRIA {par}: {e}")
                continue
        
        return analysis_results
    
    def learn_from_trade(self, trade_data, trade_result):
        """Aprender com resultado do trade"""
        try:
            learning_example = {
                'features': trade_data.get('features', {}),
                'actual_direction': 2 if trade_result['lucro_percent'] > 0 else 0,  # 2: BUY lucrativo, 0: SELL lucrativo
                'profit_magnitude': abs(trade_result['lucro_percent']),
                'timestamp': datetime.now().isoformat()
            }
            
            self.learning_data.append(learning_example)
            self.performance_history.append(trade_result['lucro_percent'])
            
            logger.info(f"📚 APRENDIZADO REGISTRADO: {trade_result['lucro_percent']:.2f}%")
            
            # Verificar se é hora de retreinar
            if len(self.learning_data) >= self.retrain_interval:
                self.retrain_model()
                
        except Exception as e:
            logger.error(f"❌ ERRO NO APRENDIZADO: {e}")
    
    def retrain_model(self):
        """Retreinar modelo com novos dados"""
        try:
            if len(self.learning_data) < 50:  # Mínimo de exemplos
                return
            
            # Preparar dados para treinamento
            X = []
            y = []
            
            for example in self.learning_data:
                if example['features']:
                    feature_vector = list(example['features'].values())
                    X.append(feature_vector)
                    y.append(example['actual_direction'])
            
            if len(X) < 20:
                return
            
            X = np.array(X)
            y = np.array(y)
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Treinar modelo
            self.model.fit(X_train, y_train)
            
            # Avaliar performance
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"🔄 MODELO RETREINADO - Accuracy: {accuracy:.3f}")
            
            # Salvar modelo
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, 'models/evolutionary_model.pkl')
            
            # Limitar tamanho dos dados de aprendizado
            if len(self.learning_data) > 1000:
                self.learning_data = self.learning_data[-500:]
                
        except Exception as e:
            logger.error(f"❌ ERRO NO RETREINAMENTO: {e}")
    
    def get_performance_metrics(self):
        """Obter métricas de performance da IA"""
        if not self.performance_history:
            return {}
        
        returns = np.array(self.performance_history)
        
        return {
            'total_trades_learned': len(self.performance_history),
            'average_return': np.mean(returns),
            'win_rate': np.sum(returns > 0) / len(returns) * 100,
            'sharpe_ratio': np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0,
            'max_return': np.max(returns),
            'min_return': np.min(returns),
            'learning_effectiveness': min(100, max(0, (np.mean(returns) + 10) * 10))  # Métrica personalizada
        }
