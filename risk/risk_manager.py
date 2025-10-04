import logging
from datetime import datetime
from typing import Dict, List
from core.config_manager import config

logger = logging.getLogger('RiskManager')

class AdvancedRiskManager:
    def __init__(self):
        self.trades_abertos = []
        self.max_positions = config.TRADING_CONFIG['max_positions']
        self.risk_per_trade = config.TRADING_CONFIG['risk_per_trade']
        logger.info("✅ GESTOR DE RISCO INICIALIZADO")
    
    def avaliar_sinal(self, sinal: Dict, saldo_atual: float) -> bool:
        """Avaliar sinal com gestão de risco"""
        try:
            # Verificar confiança mínima
            if sinal['confianca'] < 65:
                return False
            
            # Verificar limite de posições
            if len(self.trades_abertos) >= self.max_positions:
                logger.warning("⏹️ Limite máximo de posições atingido")
                return False
            
            # Verificar se já existe trade no par
            if any(trade['par'] == sinal['par'] for trade in self.trades_abertos):
                logger.warning(f"⏹️ Trade ativo no par {sinal['par']}")
                return False
            
            # Calcular tamanho da posição
            tamanho_posicao = min(
                config.TRADING_CONFIG['valor_por_trade'],
                saldo_atual * self.risk_per_trade
            )
            
            sinal['tamanho_posicao'] = tamanho_posicao
            sinal['stop_loss'] = self._calcular_stop_loss(sinal)
            sinal['take_profit'] = self._calcular_take_profit(sinal)
            
            logger.info(f"✅ SINAL APROVADO: {sinal['par']} {sinal['direcao']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ERRO NA AVALIAÇÃO DE RISCO: {e}")
            return False
    
    def _calcular_stop_loss(self, sinal: Dict) -> float:
        """Calcular stop loss"""
        preco = sinal['preco']
        stop_loss_percent = config.TRADING_CONFIG['stop_loss']
        
        if sinal['direcao'] == 'BUY':
            return preco * (1 - stop_loss_percent)
        else:  # SELL
            return preco * (1 + stop_loss_percent)
    
    def _calcular_take_profit(self, sinal: Dict) -> float:
        """Calcular take profit"""
        preco = sinal['preco']
        take_profit_percent = config.TRADING_CONFIG['take_profit']
        
        if sinal['direcao'] == 'BUY':
            return preco * (1 + take_profit_percent)
        else:  # SELL
            return preco * (1 - take_profit_percent)
    
    def registrar_trade_aberto(self, trade: Dict):
        """Registrar trade aberto"""
        self.trades_abertos.append(trade)
        logger.info(f"📝 TRADE REGISTRADO: {trade['par']} {trade['direcao']}")
    
    def obter_estatisticas_risco(self) -> Dict:
        """Obter estatísticas de risco"""
        return {
            'trades_abertos': len(self.trades_abertos),
            'max_positions': self.max_positions,
            'pares_ativos': [t['par'] for t in self.trades_abertos]
        }
