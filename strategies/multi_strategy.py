import logging
from intelligence.ai_engine import AIEngine

logger = logging.getLogger('MultiStrategy')

class MultiStrategyEngine:
    def __init__(self):
        self.ai_engine = AIEngine()
        logger.info("✅ MOTOR MULTI-ESTRATÉGIA INICIALIZADO")
    
    def analyze_with_all_strategies(self, dados_mercado):
        """Analisar mercado com estratégias"""
        all_signals = []
        
        try:
            # Estratégia IA Básica
            ai_signals = self.ai_engine.analisar_mercado(dados_mercado)
            for signal in ai_signals:
                signal['estrategia'] = 'AI_ENGINE'
                all_signals.append(signal)
            
            logger.info(f"🔍 MULTI-STRATEGY: {len(all_signals)} sinais gerados")
            return all_signals
            
        except Exception as e:
            logger.error(f"❌ ERRO NA ANÁLISE MULTI-ESTRATÉGIA: {e}")
            return []
