import logging
from datetime import datetime

logger = logging.getLogger('RiskManager')

class AdvancedRiskManager:
    def __init__(self):
        self.trades_abertos = []
        self.max_positions_simultaneas = 3
        logger.info("✅ GESTOR DE RISCO INICIALIZADO")
    
    def avaliar_sinais(self, sinais):
        """Avaliar sinais com gestão de risco"""
        trades_aprovados = []
        
        for sinal in sinais:
            try:
                if self.verificar_risco_sinal(sinal):
                    trades_aprovados.append(sinal)
                    logger.info(f"✅ SINAL APROVADO: {sinal['par']} {sinal['direcao']}")
                else:
                    logger.info(f"⏹️ SINAL REJEITADO (RISCO): {sinal['par']} {sinal['direcao']}")
                    
            except Exception as e:
                logger.error(f"❌ ERRO NA AVALIAÇÃO DE RISCO: {e}")
                continue
        
        return trades_aprovados
    
    def verificar_risco_sinal(self, sinal):
        """Verificar condições de risco para um sinal"""
        try:
            # Confiança mínima
            if sinal['confianca'] < 55:
                return False
            
            # Limite de posições simultâneas
            if len(self.trades_abertos) >= self.max_positions_simultaneas:
                logger.warning("⏹️ LIMITE DE POSIÇÕES ATINGIDO")
                return False
            
            # Evitar trades no mesmo par
            par = sinal['par']
            trades_par = [t for t in self.trades_abertos if t['par'] == par]
            if trades_par:
                logger.warning(f"⏹️ TRADE ATIVO NO PAR {par}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ ERRO NA VERIFICAÇÃO DE RISCO: {e}")
            return False
    
    def registrar_trade(self, trade):
        """Registrar trade aberto"""
        self.trades_abertos.append({
            'par': trade['par'],
            'direcao': trade['direcao'],
            'timestamp': datetime.now().isoformat(),
            'confianca': trade['confianca']
        })
    
    def remover_trade(self, par):
        """Remover trade da lista de abertos"""
        self.trades_abertos = [t for t in self.trades_abertos if t['par'] != par]
    
    def obter_estatisticas_risco(self):
        """Obter estatísticas de risco atuais"""
        return {
            'trades_abertos': len(self.trades_abertos),
            'max_positions': self.max_positions_simultaneas,
            'pares_ativos': [t['par'] for t in self.trades_abertos]
        }
