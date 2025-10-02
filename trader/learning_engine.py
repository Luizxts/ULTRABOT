import logging
import numpy as np
import json
from datetime import datetime
from collections import deque

class LearningEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trade_history = deque(maxlen=1000)
        self.performance_metrics = {}
        self.strategy_success_rates = {}
        
    def record_trade(self, decision, result):
        trade_record = {
            'timestamp': datetime.now(),
            'decision': decision,
            'result': result,
            'success': result.get('success', False),
            'profit': result.get('profit', 0),
            'confidence': decision.get('confidence', 0)
        }
        
        self.trade_history.append(trade_record)
        
        strategy_type = decision.get('type', 'unknown')
        if strategy_type not in self.strategy_success_rates:
            self.strategy_success_rates[strategy_type] = {
                'total': 0,
                'successful': 0,
                'total_profit': 0
            }
        
        self.strategy_success_rates[strategy_type]['total'] += 1
        if result.get('profit', 0) > 0:
            self.strategy_success_rates[strategy_type]['successful'] += 1
            self.strategy_success_rates[strategy_type]['total_profit'] += result.get('profit', 0)

    def analyze_performance(self):
        if not self.trade_history:
            return
            
        recent_trades = list(self.trade_history)[-50:]
        
        if recent_trades:
            profits = [t['profit'] for t in recent_trades]
            total_profit = sum(profits)
            winning_trades = [p for p in profits if p > 0]
            win_rate = len(winning_trades) / len(profits) if profits else 0
            
            self.performance_metrics = {
                'recent_win_rate': win_rate,
                'recent_total_profit': total_profit,
                'avg_profit_per_trade': np.mean(profits) if profits else 0,
                'best_strategy': self._get_best_strategy(),
                'analysis_timestamp': datetime.now()
            }
            
            self.logger.info(f"📊 Performance - Win Rate: {win_rate:.2%}")

    def _get_best_strategy(self):
        if not self.strategy_success_rates:
            return "unknown"
            
        best_strategy = None
        best_success_rate = 0
        
        for strategy, metrics in self.strategy_success_rates.items():
            if metrics['total'] >= 5:
                success_rate = metrics['successful'] / metrics['total']
                if success_rate > best_success_rate:
                    best_success_rate = success_rate
                    best_strategy = strategy
        
        return best_strategy if best_strategy else "unknown"

    def get_recommendations(self):
        recommendations = []
        
        best_strategy = self.performance_metrics.get('best_strategy')
        if best_strategy and best_strategy != 'unknown':
            recommendations.append({
                'type': 'strategy_focus',
                'message': f'Focar na estratégia: {best_strategy}',
                'confidence': self.performance_metrics.get('recent_win_rate', 0)
            })
        
        win_rate = self.performance_metrics.get('recent_win_rate', 0)
        if win_rate < 0.4:
            recommendations.append({
                'type': 'risk_reduction',
                'message': 'Reduzir risco - Win rate baixo',
                'confidence': 0.8
            })
        elif win_rate > 0.7:
            recommendations.append({
                'type': 'increase_aggression',
                'message': 'Aumentar agressividade - Win rate alto',
                'confidence': 0.7
            })
        
        return recommendations

    def get_learning_metrics(self):
        return {
            'performance_metrics': self.performance_metrics,
            'strategy_success': self.strategy_success_rates,
            'total_trades_analyzed': len(self.trade_history),
            'recommendations': self.get_recommendations()
        }
