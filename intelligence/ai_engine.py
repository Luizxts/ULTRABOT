import pandas as pd
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger('AIEngine')

class AIEngine:
    def __init__(self):
        self.historico_sinais = []
        logger.info("✅ IA ENGINE INICIALIZADA")
    
    def calcular_indicadores(self, df):
        """Calcular indicadores técnicos"""
        try:
            # EMA
            df['ema_9'] = df['close'].ewm(span=9).mean()
            df['ema_21'] = df['close'].ewm(span=21).mean()
            df['ema_50'] = df['close'].ewm(span=50).mean()
            
            # RSI
            df['rsi'] = self._calcular_rsi(df['close'])
            
            # MACD
            df['macd'], df['macd_signal'] = self._calcular_macd(df['close'])
            
            # Bollinger Bands
            df['bb_upper'], df['bb_lower'] = self._calcular_bollinger_bands(df['close'])
            
            return df
            
        except Exception as e:
            logger.error(f"❌ ERRO AO CALCULAR INDICADORES: {e}")
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
        return macd, macd_signal
    
    def _calcular_bollinger_bands(self, prices, period=20, std=2):
        """Calcular Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()
        upper_band = sma + (rolling_std * std)
        lower_band = sma - (rolling_std * std)
        return upper_band, lower_band
    
    def analisar_mercado(self, dados_mercado):
        """Analisar dados de mercado e gerar sinais"""
        sinais = []
        
        for par, timeframes in dados_mercado.items():
            try:
                if timeframes is None:
                    continue
                
                df_15m = timeframes.get('15m')
                if df_15m is None or len(df_15m) < 50:
                    continue
                
                # Calcular indicadores
                df_com_indicadores = self.calcular_indicadores(df_15m.copy())
                
                # Obter últimos valores
                ultimo = df_com_indicadores.iloc[-1]
                
                # Análise simples
                confianca = 50.0
                
                # Análise RSI
                rsi = ultimo['rsi']
                if not pd.isna(rsi):
                    if rsi < 30:
                        confianca += 20
                    elif rsi > 70:
                        confianca -= 20
                
                # Análise EMA
                if ultimo['ema_9'] > ultimo['ema_21']:
                    confianca += 15
                else:
                    confianca -= 15
                
                # Gerar sinal se confiança suficiente
                if confianca >= 65:
                    sinal = {
                        'par': par,
                        'direcao': 'BUY' if ultimo['ema_9'] > ultimo['ema_21'] else 'SELL',
                        'confianca': min(confianca, 95.0),
                        'preco': ultimo['close'],
                        'timestamp': datetime.now().isoformat(),
                        'estrategia': 'IA_BASICA'
                    }
                    sinais.append(sinal)
                    logger.info(f"🎯 SINAL IA: {par} - {sinal['direcao']} (Conf: {confianca:.1f}%)")
                
            except Exception as e:
                logger.error(f"❌ ERRO NA ANÁLISE {par}: {e}")
                continue
        
        return sinais
