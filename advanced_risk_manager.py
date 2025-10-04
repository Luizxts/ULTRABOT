# advanced_risk_manager.py - RISK MANAGER MELHORADO
import numpy as np
from datetime import datetime, timedelta

class AdvancedRiskManager:
    """Gerenciamento de risco avançado com VaR e stress testing"""
    
    def __init__(self):
        self.var_confidences = [0.95, 0.99]
        self.stress_scenarios = [
            'flash_crash',
            'volatility_spike', 
            'liquidity_crisis',
            'correlation_breakdown'
        ]
        
    def calculate_var(self, portfolio_returns, confidence_level=0.95):
        """Calcula Value at Risk (VaR)"""
        if len(portfolio_returns) < 30:
            return 0.0
            
        var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        return abs(var)
    
    def stress_test_portfolio(self, portfolio, current_market_conditions):
        """Executa testes de stress no portfólio"""
        stress_results = {}
        
        for scenario in self.stress_scenarios:
            if scenario == 'flash_crash':
                loss = self.simulate_flash_crash(portfolio)
            elif scenario == 'volatility_spike':
                loss = self.simulate_volatility_spike(portfolio)
            elif scenario == 'liquidity_crisis':
                loss = self.simulate_liquidity_crisis(portfolio)
            elif scenario == 'correlation_breakdown':
                loss = self.simulate_correlation_breakdown(portfolio)
                
            stress_results[scenario] = {
                'max_loss_pct': loss,
                'severity': 'HIGH' if loss > 0.1 else 'MEDIUM' if loss > 0.05 else 'LOW'
            }
            
        return stress_results
    
    def simulate_flash_crash(self, portfolio):
        """Simula um flash crash (20% de queda instantânea)"""
        total_exposure = sum(pos['exposure'] for pos in portfolio.values())
        if total_exposure == 0:
            return 0.0
        return min(0.2, total_exposure * 0.2 / total_exposure)
    
    def simulate_volatility_spike(self, portfolio):
        """Simula spike de volatilidade"""
        # Aumento de 300% na volatilidade
        return 0.15  # 15% de perda estimada
    
    def simulate_liquidity_crisis(self, portfolio):
        """Simula crise de liquidez"""
        # Spreads aumentam 500%, execução piora
        return 0.08  # 8% de perda por execução
    
    def simulate_correlation_breakdown(self, portfolio):
        """Simula quebra de correlações (diversificação falha)"""
        return 0.12  # 12% de perda
    
    def calculate_max_drawdown(self, equity_curve):
        """Calcula máximo drawdown histórico"""
        if len(equity_curve) < 2:
            return 0.0
            
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
                
        return max_dd
    
    def adaptive_position_sizing(self, market_volatility, account_balance, win_rate):
        """Tamanho de posição adaptativo baseado em condições"""
        base_size = account_balance * 0.01  # 1% base
        
        # Ajustar baseado na volatilidade
        if market_volatility > 0.05:  # Alta volatilidade
            vol_adjustment = 0.5
        elif market_volatility < 0.02:  # Baixa volatilidade
            vol_adjustment = 1.5
        else:
            vol_adjustment = 1.0
            
        # Ajustar baseado no win rate
        if win_rate > 0.7:
            win_rate_adjustment = 1.2
        elif win_rate < 0.4:
            win_rate_adjustment = 0.8
        else:
            win_rate_adjustment = 1.0
            
        final_size = base_size * vol_adjustment * win_rate_adjustment
        return min(final_size, account_balance * 0.03)  # Máximo 3%

advanced_risk_manager = AdvancedRiskManager()
