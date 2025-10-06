import numpy as np
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger('RedeNeuralSimples')

class CerebroNeuralSimples:
    """Cérebro neural EXTREMAMENTE LEVE - Sem dependências pesadas"""
    
    def __init__(self):
        logger.info("🧠 CÉREBRO NEURAL SIMPLES INICIALIZADO")
    
    def extrair_features_simples(self, dados_mercado):
        """Extrair 15 features super simples"""
        try:
            features = {}
            
            for par, timeframes in dados_mercado.items():
                if not timeframes or '15m' not in timeframes:
                    continue
                
                df = timeframes['15m']
                if len(df) < 10:
                    continue
                
                close = df['close']
                high = df['high'] 
                low = df['low']
                volume = df['volume']
                
                # 🎯 FEATURES SUPER SIMPLES (15 features)
                
                # Retornos básicos
                features[f'{par}_ret_1'] = close.pct_change(1).iloc[-1]
                features[f'{par}_ret_5'] = close.pct_change(5).iloc[-1]
                features[f'{par}_ret_15'] = close.pct_change(15).iloc[-1]
                
                # Médias móveis simples
                features[f'{par}_sma_10'] = close.rolling(10).mean().iloc[-1]
                features[f'{par}_sma_20'] = close.rolling(20).mean().iloc[-1]
                features[f'{par}_price_vs_sma_10'] = (close.iloc[-1] / features[f'{par}_sma_10'] - 1)
                
                # Volatilidade básica
                features[f'{par}_vol_10'] = close.pct_change().rolling(10).std().iloc[-1]
                
                # RSI manual simples
                features[f'{par}_rsi'] = self._calcular_rsi_manual(close, 14)
                
                # Volume básico
                features[f'{par}_volume_ratio'] = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]
                
                # Suporte/resistência simples
                features[f'{par}_high_10'] = high.rolling(10).max().iloc[-1]
                features[f'{par}_low_10'] = low.rolling(10).min().iloc[-1]
                features[f'{par}_dist_high'] = (features[f'{par}_high_10'] - close.iloc[-1]) / close.iloc[-1]
                features[f'{par}_dist_low'] = (close.iloc[-1] - features[f'{par}_low_10']) / close.iloc[-1]
                
                # Tendência linear simples
                features[f'{par}_trend'] = self._calcular_tendencia_simples(close, 10)
            
            return pd.Series(features)
            
        except Exception as e:
            logger.error(f"❌ Erro na extração de features: {e}")
            return pd.Series()
    
    def _calcular_rsi_manual(self, prices, period=14):
        """Calcular RSI manualmente"""
        if len(prices) < period:
            return 50
        
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)
            
            avg_gain = gain.rolling(window=period).mean().iloc[-1]
            avg_loss = loss.rolling(window=period).mean().iloc[-1]
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return min(max(rsi, 0), 100)
        except:
            return 50
    
    def _calcular_tendencia_simples(self, prices, period):
        """Calcular tendência linear simples"""
        if len(prices) < period:
            return 0
        
        try:
            x = np.arange(len(prices[-period:]))
            y = prices[-period:].values
            slope = np.polyfit(x, y, 1)[0]
            return slope / prices.iloc[-1]
        except:
            return 0
    
    def prever(self, dados_mercado):
        """Fazer previsão com lógica simples mas inteligente"""
        try:
            features = self.extrair_features_simples(dados_mercado)
            
            if features.empty:
                return self._previsao_segura()
            
            # 🎯 ESTRATÉGIA DE DECISÃO SIMPLES MAS EFICAZ
            buy_signals = 0
            sell_signals = 0
            
            for feature_name, value in features.items():
                if np.isnan(value):
                    continue
                    
                # Sinal de COMPRA
                if 'rsi' in feature_name and value < 35:
                    buy_signals += 2
                elif 'rsi' in feature_name and value < 45:
                    buy_signals += 1
                    
                elif 'price_vs_sma' in feature_name and value < -0.02:
                    buy_signals += 1
                elif 'trend' in feature_name and value > 0.001:
                    buy_signals += 1
                elif 'dist_low' in feature_name and value < 0.02:
                    buy_signals += 1
                elif 'vol_10' in feature_name and value > 0.02:
                    buy_signals += 1
                    
                # Sinal de VENDA  
                elif 'rsi' in feature_name and value > 65:
                    sell_signals += 2
                elif 'rsi' in feature_name and value > 55:
                    sell_signals += 1
                    
                elif 'price_vs_sma' in feature_name and value > 0.02:
                    sell_signals += 1
                elif 'trend' in feature_name and value < -0.001:
                    sell_signals += 1
                elif 'dist_high' in feature_name and value < 0.02:
                    sell_signals += 1
                elif 'vol_10' in feature_name and value > 0.03:
                    sell_signals += 1
            
            # TOMADA DE DECISÃO
            if buy_signals > sell_signals and buy_signals >= 3:
                direction = "BUY"
                confidence = min(60 + (buy_signals * 6), 80)
            elif sell_signals > buy_signals and sell_signals >= 3:
                direction = "SELL"
                confidence = min(60 + (sell_signals * 6), 80)
            else:
                direction = "HOLD"
                confidence = 50
            
            # Ajustar confiança baseada na qualidade dos dados
            valid_features = sum(1 for f in features.values if not np.isnan(f))
            if valid_features > 0:
                data_quality = valid_features / len(features)
                confidence = confidence * data_quality
            
            confidence = max(40, min(80, confidence))
            
            # Calcular probabilidades
            if direction == "BUY":
                prob_buy = confidence
                prob_sell = (100 - confidence) * 0.4
                prob_hold = 100 - prob_buy - prob_sell
            elif direction == "SELL":
                prob_sell = confidence
                prob_buy = (100 - confidence) * 0.4
                prob_hold = 100 - prob_sell - prob_buy
            else:
                prob_hold = confidence
                prob_buy = (100 - confidence) * 0.3
                prob_sell = (100 - confidence) * 0.3
            
            return {
                'direcao': direction,
                'confianca': float(confidence),
                'probabilidades': {
                    'SELL': float(prob_sell),
                    'HOLD': float(prob_hold),
                    'BUY': float(prob_buy)
                },
                'timestamp': datetime.now().isoformat(),
                'modelo': 'LOGICA_SIMPLES',
                'total_features': len(features),
                'signals': {'buy': buy_signals, 'sell': sell_signals}
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
