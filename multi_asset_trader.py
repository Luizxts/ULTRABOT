# multi_asset_trader.py - SISTEMA MULTI-ATIVOS
import pandas as pd
import numpy as np
from datetime import datetime

class MultiAssetTrader:
    """Sistema de trading para múltiplos ativos"""
    
    def __init__(self):
        self.assets = {
            'BTCUSDT': {
                'weight': 0.4,
                'risk_multiplier': 1.0,
                'correlation_group': 'crypto_major'
            },
            'ETHUSDT': {
                'weight': 0.3, 
                'risk_multiplier': 1.2,
                'correlation_group': 'crypto_major'
            },
            'SOLUSDT': {
                'weight': 0.2,
                'risk_multiplier': 1.5,
                'correlation_group': 'crypto_alt'
            },
            'BNBUSDT': {
                'weight': 0.1,
                'risk_multiplier': 1.3,
                'correlation_group': 'crypto_alt'
            }
        }
        
        self.portfolio = {}
        self.correlation_matrix = {}
        
    def calculate_portfolio_allocation(self, total_capital, signals):
        """Calcula alocação ótima do portfólio"""
        allocations = {}
        
        for asset, signal_data in signals.items():
            if asset in self.assets:
                weight = self.assets[asset]['weight']
                risk_multiplier = self.assets[asset]['risk_multiplier']
                signal_strength = signal_data.get('confidence', 0.5)
                
                # Calcular alocação baseada em peso, risco e sinal
                base_allocation = total_capital * weight
                risk_adjusted = base_allocation * risk_multiplier
                signal_adjusted = risk_adjusted * signal_strength
                
                allocations[asset] = {
                    'capital': signal_adjusted,
                    'position_size': 0,
                    'risk_score': risk_multiplier,
                    'signal_strength': signal_strength
                }
                
        return allocations
    
    def diversify_signals(self, signals):
        """Diversifica sinais para evitar correlação excessiva"""
        diversified = {}
        crypto_major_signals = []
        crypto_alt_signals = []
        
        # Agrupar sinais por categoria
        for asset, signal_data in signals.items():
            if asset in self.assets:
                group = self.assets[asset]['correlation_group']
                if group == 'crypto_major':
                    crypto_major_signals.append((asset, signal_data))
                elif group == 'crypto_alt':
                    crypto_alt_signals.append((asset, signal_data))
        
        # Selecionar melhores sinais de cada grupo
        if crypto_major_signals:
            best_major = max(crypto_major_signals, key=lambda x: x[1].get('confidence', 0))
            diversified[best_major[0]] = best_major[1]
            
        if crypto_alt_signals:
            best_alt = max(crypto_alt_signals, key=lambda x: x[1].get('confidence', 0))
            diversified[best_alt[0]] = best_alt[1]
            
        return diversified
    
    def calculate_correlation_penalties(self, signals):
        """Aplica penalidades por correlação excessiva"""
        penalized_signals = signals.copy()
        
        # Simular análise de correlação (em produção usar dados reais)
        for asset1, signal1 in signals.items():
            for asset2, signal2 in signals.items():
                if asset1 != asset2:
                    # Penalizar ativos altamente correlacionados
                    correlation = self.estimate_correlation(asset1, asset2)
                    if abs(correlation) > 0.7:
                        penalty = 1.0 - abs(correlation)
                        if asset1 in penalized_signals:
                            current_conf = penalized_signals[asset1].get('confidence', 0)
                            penalized_signals[asset1]['confidence'] = current_conf * penalty
                            
        return penalized_signals
    
    def estimate_correlation(self, asset1, asset2):
        """Estima correlação entre ativos (simulado)"""
        # Em produção, calcular correlação real baseada em dados históricos
        correlation_map = {
            ('BTCUSDT', 'ETHUSDT'): 0.8,
            ('BTCUSDT', 'SOLUSDT'): 0.6,
            ('BTCUSDT', 'BNBUSDT'): 0.5,
            ('ETHUSDT', 'SOLUSDT'): 0.7,
            ('ETHUSDT', 'BNBUSDT'): 0.6,
            ('SOLUSDT', 'BNBUSDT'): 0.8,
        }
        
        pair = (asset1, asset2)
        reverse_pair = (asset2, asset1)
        
        if pair in correlation_map:
            return correlation_map[pair]
        elif reverse_pair in correlation_map:
            return correlation_map[reverse_pair]
        else:
            return 0.3  # Correlação baixa padrão

multi_asset_trader = MultiAssetTrader()
