# debug_trader.py - VERSÃO MAIS AGRESSIVA PARA TESTES
import random
import numpy as np
from datetime import datetime

class DebugTrader:
    """Sistema de debug OTIMIZADO para gerar mais trades"""
    
    def __init__(self, main_bot):
        self.bot = main_bot
        self.cycle_count = 0
        self.debug_enabled = True
        
    def force_debug_trades(self):
        """Força trades de debug MAIS FREQUENTES"""
        if not self.debug_enabled:
            return
            
        self.cycle_count += 1
        
        # Executar debug a cada 2 ciclos (ERA 3)
        if self.cycle_count % 2 == 0:
            return
            
        assets = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        selected_asset = random.choice(assets)
        
        # MAIS AGRESSIVO: 50% HOLD, 25% BUY, 25% SELL (ERA 70/15/15)
        signal_roll = random.random()
        if signal_roll < 0.25:
            signal = "BUY"
            confidence = random.uniform(0.7, 0.9)
            self.bot.logger.info(f"🎯 DEBUG SIGNAL: BUY {selected_asset} | Conf: {confidence:.1%}")
            self.execute_debug_trade(selected_asset, signal, confidence)
            
        elif signal_roll < 0.5:
            signal = "SELL" 
            confidence = random.uniform(0.7, 0.9)
            self.bot.logger.info(f"🎯 DEBUG SIGNAL: SELL {selected_asset} | Conf: {confidence:.1%}")
            self.execute_debug_trade(selected_asset, signal, confidence)
        else:
            self.bot.logger.info(f"🎯 DEBUG SIGNAL: HOLD {selected_asset}")

    def execute_debug_trade(self, asset, signal, confidence):
        """Executa trade de debug OTIMIZADO"""
        try:
            # Criar dados de sinal realistas
            signal_data = {
                'base_signal': signal,
                'final_confidence': confidence,
                'sentiment': {
                    'classification': 'BULLISH' if signal == 'BUY' else 'BEARISH',
                    'score': 0.8 if signal == 'BUY' else -0.8
                },
                'market_regime': 'TRENDING_BULL' if signal == 'BUY' else 'TRENDING_BEAR',
                'asset': asset,
                'timestamp': datetime.now()
            }
            
            # Calcular tamanho da posição (0.5% do saldo para testes mais visíveis)
            position_size = self.bot.bybit.calculate_position_size()
            test_position_size = position_size * 0.5  # 50% do tamanho normal
            
            allocation = {
                'capital': self.bot.balance * 0.005,  # 0.5% do saldo
                'position_size': test_position_size,
                'risk_score': 1.0,
                'signal_strength': confidence
            }
            
            # Executar trade via sistema principal
            success = self.bot.execute_enhanced_trade(asset, signal_data, allocation)
            
            if success:
                self.bot.logger.info(f"✅ TRADE DEBUG EXECUTADO COM SUCESSO!")
            else:
                self.bot.logger.warning("⚠️ TRADE DEBUG NÃO EXECUTADO")
            
        except Exception as e:
            self.bot.logger.error(f"❌ ERRO NO TRADE DEBUG: {e}")
