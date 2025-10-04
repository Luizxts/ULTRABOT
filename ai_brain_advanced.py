import pandas as pd
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger('AIBrain')

class AIBrainAdvanced:
    def __init__(self):
        self.historico_sinais = []
        logger.info("✅ IA AVANÇADA INICIALIZADA")
    
    def calcular_indicadores(self, df):
        """Calcular indicadores técnicos sem TA-Lib"""
        try:
            # EMA
            df['ema_9'] = df['close'].ewm(span=9).mean()
            df['ema_21'] = df['close'].ewm(span=21).mean()
            df['ema_50'] = df['close'].ewm(span=50).mean()
            
            # RSI
            df['rsi'] = self.calcular_rsi(df['close'])
            
            # MACD
            df['macd'], df['macd_signal'] = self.calcular_macd(df['close'])
            
            # Bollinger Bands
            df['bb_upper'], df['bb_lower'] = self.calcular_bollinger_bands(df['close'])
            
            # Volume SMA
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # ATR
            df['atr'] = self.calcular_atr(df)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ ERRO AO CALCULAR INDICADORES: {e}")
            return df
    
    def calcular_rsi(self, prices, period=14):
        """Calcular RSI manualmente"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calcular_macd(self, prices, fast=12, slow=26, signal=9):
        """Calcular MACD manualmente"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def calcular_bollinger_bands(self, prices, period=20, std=2):
        """Calcular Bollinger Bands manualmente"""
        sma = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()
        upper_band = sma + (rolling_std * std)
        lower_band = sma - (rolling_std * std)
        return upper_band, lower_band
    
    def calcular_atr(self, df, period=14):
        """Calcular ATR manualmente"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = np.maximum(np.maximum(high_low, high_close), low_close)
        atr = true_range.rolling(window=period).mean()
        return atr
    
    def analisar_mercado(self, dados_mercado):
        """Analisar dados de mercado e gerar sinais"""
        sinais = []
        
        for par, timeframes in dados_mercado.items():
            if timeframes is None:
                continue
            
            try:
                # Usar timeframe de 15m para análise principal
                df_15m = timeframes.get('15m')
                if df_15m is None or len(df_15m) < 50:
                    continue
                
                # Calcular indicadores
                df_com_indicadores = self.calcular_indicadores(df_15m.copy())
                
                # Obter últimos valores
                ultimo = df_com_indicadores.iloc[-1]
                penultimo = df_com_indicadores.iloc[-2]
                
                # Análise de tendência
                tendencia = self.analisar_tendencia(df_com_indicadores)
                
                # Gerar sinal
                sinal = self.gerar_sinal(ultimo, penultimo, tendencia, par)
                
                if sinal:
                    sinais.append(sinal)
                    logger.info(f"🎯 SINAL GERADO: {par} - {sinal['direcao']} (Conf: {sinal['confianca']}%)")
                
            except Exception as e:
                logger.error(f"❌ ERRO NA ANÁLISE {par}: {e}")
                continue
        
        return sinais
    
    def analisar_tendencia(self, df):
        """Analisar tendência do mercado"""
        try:
            # Médias móveis
            ema_9 = df['ema_9'].iloc[-1]
            ema_21 = df['ema_21'].iloc[-1]
            ema_50 = df['ema_50'].iloc[-1]
            
            # Tendência por EMAs
            if ema_9 > ema_21 > ema_50:
                return "ALTA"
            elif ema_9 < ema_21 < ema_50:
                return "BAIXA"
            else:
                return "LATERAL"
                
        except Exception as e:
            logger.error(f"❌ ERRO NA ANÁLISE DE TENDÊNCIA: {e}")
            return "NEUTRA"
    
    def gerar_sinal(self, ultimo, penultimo, tendencia, par):
        """Gerar sinal de trading baseado na análise"""
        try:
            confianca = 50.0  # Base
            
            # Análise RSI
            rsi = ultimo['rsi']
            if not pd.isna(rsi):
                if rsi < 30:
                    confianca += 15
                elif rsi > 70:
                    confianca -= 15
            
            # Análise MACD
            macd = ultimo['macd']
            macd_signal = ultimo['macd_signal']
            if not pd.isna(macd) and not pd.isna(macd_signal):
                if macd > macd_signal and penultimo['macd'] <= penultimo['macd_signal']:
                    confianca += 10
                elif macd < macd_signal and penultimo['macd'] >= penultimo['macd_signal']:
                    confianca -= 10
            
            # Análise Bollinger Bands
            preco = ultimo['close']
            bb_upper = ultimo['bb_upper']
            bb_lower = ultimo['bb_lower']
            
            if not pd.isna(bb_upper) and not pd.isna(bb_lower):
                if preco <= bb_lower:
                    confianca += 10
                elif preco >= bb_upper:
                    confianca -= 10
            
            # Determinar direção baseada na tendência e confiança
            if confianca >= 60:
                direcao = "BUY" if tendencia in ["ALTA", "NEUTRA"] else "HOLD"
            elif confianca <= 40:
                direcao = "SELL" if tendencia in ["BAIXA", "NEUTRA"] else "HOLD"
            else:
                direcao = "HOLD"
            
            # Só retornar se não for HOLD
            if direcao != "HOLD" and confianca >= 55:
                return {
                    'par': par,
                    'direcao': direcao,
                    'confianca': min(confianca, 95.0),
                    'preco': preco,
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ ERRO AO GERAR SINAL: {e}")
            return None
