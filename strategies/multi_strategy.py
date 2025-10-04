import logging
import numpy as np
from datetime import datetime
from typing import Dict, List
from intelligence.ai_engine import AIEngine
from intelligence.evolutionary_ai import EvolutionaryAI

logger = logging.getLogger('MultiStrategy')

class MultiStrategyEngine:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.evolutionary_ai = EvolutionaryAI()
        self.strategy_weights = {
            'AI_ENGINE': 0.4,
            'EVOLUTIONARY_AI': 0.6
        }
        self.strategy_performance = {
            'AI_ENGINE': {'wins': 0, 'losses': 0, 'total_return': 0},
            'EVOLUTIONARY_AI': {'wins': 0, 'losses': 0, 'total_return': 0}
        }
        
        logger.info("✅ MOTOR MULTI-ESTRATÉGIA INICIALIZADO")
    
    def analyze_with_all_strategies(self, dados_mercado):
        """Analisar mercado com todas as estratégias"""
        all_signals = []
        
        try:
            # 1. Análise com IA Básica
            ai_signals = self.ai_engine.analisar_mercado(dados_mercado)
            for signal in ai_signals:
                signal['estrategia'] = 'AI_ENGINE'
                signal['peso'] = self.strategy_weights['AI_ENGINE']
                all_signals.append(signal)
            
            # 2. Análise com IA Evolucionária
            evolutionary_signals = self.evolutionary_ai.analyze_market_conditions(dados_mercado)
            for par, signal in evolutionary_signals.items():
                signal['peso'] = self.strategy_weights['EVOLUTIONARY_AI']
                all_signals.append(signal)
            
            # 3. Combinar sinais do mesmo par
            combined_signals = self._combine_signals(all_signals)
            
            logger.info(f"🔍 MULTI-STRATEGY: {len(combined_signals)} sinais combinados")
            return combined_signals
            
        except Exception as e:
            logger.error(f"❌ ERRO NA ANÁLISE MULTI-ESTRATÉGIA: {e}")
            return []
    
    def _combine_signals(self, signals: List[Dict]) -> List[Dict]:
        """Combinar sinais de diferentes estratégias"""
        combined = {}
        
        for signal in signals:
            par = signal['par']
            
            if par not in combined:
                combined[par] = {
                    'par': par,
                    'direcoes': [],
                    'confiancas': [],
                    'estrategias': [],
                    'pesos': [],
                    'precos': []
                }
            
            combined[par]['direcoes'].append(signal['direcao'])
            combined[par]['confiancas'].append(signal['confianca'])
            combined[par]['estrategias'].append(signal['estrategia'])
            combined[par]['pesos'].append(signal.get('peso', 0.5))
            combined[par]['precos'].append(signal['preco'])
        
        # Processar sinais combinados
        final_signals = []
        for par, data in combined.items():
            final_signal = self._calculate_final_signal(par, data)
            if final_signal:
                final_signals.append(final_signal)
        
        return final_signals
    
    def _calculate_final_signal(self, par: str, data: Dict) -> Dict:
        """Calcular sinal final baseado em consenso"""
        try:
            # Verificar consenso de direção
            buy_votes = data['direcoes'].count('BUY')
            sell_votes = data['direcoes'].count('SELL')
            total_votes = len(data['direcoes'])
            
            # Calcular confiança ponderada
            weighted_confidence = sum(
                conf * peso for conf, peso in zip(data['confiancas'], data['pesos'])
            ) / sum(data['pesos'])
            
            # Determinar direção final
            if buy_votes > sell_votes and buy_votes / total_votes >= 0.6:
                direction = 'BUY'
                consensus_strength = buy_votes / total_votes
            elif sell_votes > buy_votes and sell_votes / total_votes >= 0.6:
                direction = 'SELL'
                consensus_strength = sell_votes / total_votes
            else:
                # Sem consenso claro - manter HOLD
                return None
            
            # Ajustar confiança baseado na força do consenso
            final_confidence = weighted_confidence * consensus_strength
            
            # Aplicar filtro de confiança mínima
            if final_confidence < 65:
                return None
            
            # Preço médio
            avg_price = np.mean(data['precos'])
            
            return {
                'par': par,
                'direcao': direction,
                'confianca': final_confidence,
                'preco': avg_price,
                'timestamp': datetime.now().isoformat(),
                'estrategia': 'MULTI_STRATEGY_CONSENSUS',
                'estrategias_envolvidas': data['estrategias'],
                'consenso_strength': consensus_strength
            }
            
        except Exception as e:
            logger.error(f"❌ ERRO NO CÁLCULO DE SINAL FINAL {par}: {e}")
            return None
    
    def update_strategy_performance(self, trade_result: Dict, estrategia: str):
        """Atualizar performance das estratégias"""
        try:
            if estrategia in self.strategy_performance:
                perf = self.strategy_performance[estrategia]
                
                if trade_result['lucro_percent'] > 0:
                    perf['wins'] += 1
                else:
                    perf['losses'] += 1
                
                perf['total_return'] += trade_result['lucro_percent']
                
                # Rebalancear pesos baseado na performance
                self._rebalance_strategy_weights()
                
        except Exception as e:
            logger.error(f"❌ ERRO AO ATUALIZAR PERFORMANCE: {e}")
    
    def _rebalance_strategy_weights(self):
        """Rebalancear pesos das estratégias baseado na performance"""
        try:
            total_performance = {}
            
            for strategy, perf in self.strategy_performance.items():
                total_trades = perf['wins'] + perf['losses']
                if total_trades > 0:
                    win_rate = perf['wins'] / total_trades
                    avg_return = perf['total_return'] / total_trades if total_trades > 0 else 0
                    total_performance[strategy] = win_rate * (1 + avg_return / 100)
                else:
                    total_performance[strategy] = 0.5  # Performance neutra
            
            # Normalizar pesos
            total_score = sum(total_performance.values())
            if total_score > 0:
                for strategy in self.strategy_weights:
                    self.strategy_weights[strategy] = total_performance.get(strategy, 0.5) / total_score
            
            logger.info(f"⚖️ PESOS REBALANCEADOS: {self.strategy_weights}")
            
        except Exception as e:
            logger.error(f"❌ ERRO NO REBALANCEAMENTO: {e}")
    
    def get_strategy_metrics(self):
        """Obter métricas das estratégias"""
        metrics = {
            'weights': self.strategy_weights,
            'performance': {}
        }
        
        for strategy, perf in self.strategy_performance.items():
            total_trades = perf['wins'] + perf['losses']
            metrics['performance'][strategy] = {
                'total_trades': total_trades,
                'wins': perf['wins'],
                'losses': perf['losses'],
                'win_rate': perf['wins'] / total_trades * 100 if total_trades > 0 else 0,
                'total_return': perf['total_return']
            }
        
        return metrics
