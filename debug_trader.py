# debug_trader.py - SISTEMA DE DEBUG PARA TESTAR EXECUÇÃO
import random
import numpy as np
from datetime import datetime

class DebugTrader:
    """
    Sistema de debug para forçar trades de teste
    Remove depois que estiver funcionando!
    """
    
    def __init__(self, main_bot):
        self.bot = main_bot
        self.cycle_count = 0
        self.debug_enabled = True
        
    def force_debug_trades(self):
        """Força trades de debug para testar a execução"""
        if not self.debug_enabled:
            return
            
        self.cycle_count += 1
        
        # Executar debug a cada 2 ciclos para não ser muito agressivo
        if self.cycle_count % 2 != 0:
            return
            
        assets = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        selected_asset = random.choice(assets)
        
        # Gerar sinal aleatório (60% HOLD, 20% BUY, 20% SELL)
        signal_roll = random.random()
        if signal_roll < 0.2:
            signal = "BUY"
            confidence = random.uniform(0.7, 0.9)
            self.bot.logger.info(f"🎯 DEBUG SIGNAL: BUY {selected_asset} | Conf: {confidence:.1%}")
            self.execute_debug_trade(selected_asset, signal, confidence)
            
        elif signal_roll < 0.4:
            signal = "SELL" 
            confidence = random.uniform(0.7, 0.9)
            self.bot.logger.info(f"🎯 DEBUG SIGNAL: SELL {selected_asset} | Conf: {confidence:.1%}")
            self.execute_debug_trade(selected_asset, signal, confidence)
        else:
            self.bot.logger.info(f"🎯 DEBUG SIGNAL: HOLD {selected_asset} | Conf: 50.0%")

    def execute_debug_trade(self, asset, signal, confidence):
        """Executa trade de debug"""
        try:
            # Criar dados de sinal simulados
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
            
            # Calcular tamanho da posição
            position_size = self.bot.bybit.calculate_position_size()
            
            allocation = {
                'capital': self.bot.balance * 0.02,  # 2% do saldo
                'position_size': position_size,
                'risk_score': 1.0,
                'signal_strength': confidence
            }
            
            # Executar trade via sistema principal
            self.bot.execute_enhanced_trade(asset, signal_data, allocation)
            
        except Exception as e:
            self.bot.logger.error(f"❌ ERRO NO TRADE DEBUG: {e}")

    def disable_debug(self):
        """Desabilita o modo debug"""
        self.debug_enabled = False
        self.bot.logger.info("🔧 MODO DEBUG DESATIVADO")
