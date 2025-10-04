import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core.config_manager import config

logger = logging.getLogger('RiskManager')

class AdvancedRiskManager:
    def __init__(self):
        self.trades_abertos = []
        self.historico_trades = []
        self.performance_metrics = {
            'total_trades': 0,
            'trades_lucrativos': 0,
            'trades_prejuizo': 0,
            'lucro_total': 0.0,
            'prejuizo_total': 0.0,
            'maior_lucro': 0.0,
            'maior_prejuizo': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0
        }
        
        # Limites de risco
        self.max_positions = config.TRADING_CONFIG['max_positions']
        self.risk_per_trade = config.TRADING_CONFIG['risk_per_trade']
        self.max_drawdown = config.TRADING_CONFIG['max_drawdown']
        self.max_loss_diario = 0.10  # 10% máximo por dia
        
        self.drawdown_atual = 0.0
        self.loss_diario = 0.0
        self.ultimo_reset_diario = datetime.now().date()
        
        logger.info("✅ GESTOR DE RISCO AVANÇADO INICIALIZADO")
    
    def avaliar_sinal(self, sinal: Dict, saldo_atual: float) -> bool:
        """Avaliar sinal com múltiplas camadas de risco"""
        try:
            # 1. Verificar confiança mínima
            if sinal['confianca'] < 65:
                logger.info(f"⏹️ Confiança insuficiente: {sinal['confianca']}%")
                return False
            
            # 2. Verificar limite de posições
            if len(self.trades_abertos) >= self.max_positions:
                logger.warning("⏹️ Limite máximo de posições atingido")
                return False
            
            # 3. Verificar se já existe trade no par
            if any(trade['par'] == sinal['par'] for trade in self.trades_abertos):
                logger.warning(f"⏹️ Trade ativo no par {sinal['par']}")
                return False
            
            # 4. Verificar drawdown atual
            if self.drawdown_atual >= self.max_drawdown:
                logger.error("🚨 DRAWDOWN MÁXIMO ATINGIDO - TRADING SUSPENSO")
                return False
            
            # 5. Verificar loss diário
            self._atualizar_loss_diario()
            if self.loss_diario >= self.max_loss_diario:
                logger.error("🚨 LOSS DIÁRIO MÁXIMO ATINGIDO")
                return False
            
            # 6. Verificar correlação entre posições
            if self._alta_correlacao_posicoes(sinal['par']):
                logger.warning(f"⏹️ Alta correlação com posições existentes: {sinal['par']}")
                return False
            
            # 7. Verificar volatilidade excessiva
            if self._volatilidade_excessiva(sinal):
                logger.warning(f"⏹️ Volatilidade excessiva: {sinal['par']}")
                return False
            
            # 8. Calcular tamanho da posição baseado no risco
            tamanho_posicao = self._calcular_tamanho_posicao(sinal, saldo_atual)
            if tamanho_posicao <= 0:
                logger.warning("⏹️ Tamanho de posição inválido")
                return False
            
            # Adicionar informações de risco ao sinal
            sinal['tamanho_posicao'] = tamanho_posicao
            sinal['stop_loss'] = self._calcular_stop_loss(sinal)
            sinal['take_profit'] = self._calcular_take_profit(sinal)
            sinal['risk_reward_ratio'] = self._calcular_risk_reward(sinal)
            
            logger.info(f"✅ SINAL APROVADO: {sinal['par']} {sinal['direcao']} "
                       f"(Size: ${tamanho_posicao:.2f}, R/R: {sinal['risk_reward_ratio']:.2f})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ ERRO NA AVALIAÇÃO DE RISCO: {e}")
            return False
    
    def _calcular_tamanho_posicao(self, sinal: Dict, saldo_atual: float) -> float:
        """Calcular tamanho da posição baseado no risco"""
        try:
            # Baseado no risco por trade
            risco_absoluto = saldo_atual * self.risk_per_trade
            
            # Calcular distância para stop loss
            preco_entrada = sinal['preco']
            stop_loss = self._calcular_stop_loss(sinal)
            
            if sinal['direcao'] == 'BUY':
                distancia_sl = preco_entrada - stop_loss
            else:  # SELL
                distancia_sl = stop_loss - preco_entrada
            
            if distancia_sl <= 0:
                return 0
            
            # Calcular tamanho da posição
            tamanho_posicao = risco_absoluto / (distancia_sl / preco_entrada)
            
            # Limitar pelo valor máximo por trade
            valor_maximo = config.TRADING_CONFIG['valor_por_trade']
            return min(tamanho_posicao, valor_maximo)
            
        except Exception as e:
            logger.error(f"❌ ERRO NO CÁLCULO DE POSIÇÃO: {e}")
            return config.TRADING_CONFIG['valor_por_trade']
    
    def _calcular_stop_loss(self, sinal: Dict) -> float:
        """Calcular stop loss dinâmico"""
        preco = sinal['preco']
        stop_loss_percent = config.TRADING_CONFIG['stop_loss']
        
        if sinal['direcao'] == 'BUY':
            return preco * (1 - stop_loss_percent)
        else:  # SELL
            return preco * (1 + stop_loss_percent)
    
    def _calcular_take_profit(self, sinal: Dict) -> float:
        """Calcular take profit dinâmico"""
        preco = sinal['preco']
        take_profit_percent = config.TRADING_CONFIG['take_profit']
        
        if sinal['direcao'] == 'BUY':
            return preco * (1 + take_profit_percent)
        else:  # SELL
            return preco * (1 - take_profit_percent)
    
    def _calcular_risk_reward(self, sinal: Dict) -> float:
        """Calcular ratio risco/recompensa"""
        preco = sinal['preco']
        sl = sinal['stop_loss']
        tp = sinal['take_profit']
        
        if sinal['direcao'] == 'BUY':
            risco = preco - sl
            recompensa = tp - preco
        else:  # SELL
            risco = sl - preco
            recompensa = preco - tp
        
        return recompensa / risco if risco > 0 else 0
    
    def _alta_correlacao_posicoes(self, novo_par: str) -> bool:
        """Verificar correlação com posições existentes"""
        if not self.trades_abertos:
            return False
        
        # Lista de pares correlacionados (exemplo simplificado)
        grupos_correlacao = [
            ['BTCUSDT', 'ETHUSDT'],  # Majors
            ['SOLUSDT', 'AVAXUSDT', 'MATICUSDT'],  # Altcoins
            ['XRPUSDT', 'ADAUSDT', 'DOTUSDT']  # Outros
        ]
        
        for grupo in grupos_correlacao:
            if novo_par in grupo:
                # Verificar se já existe trade no mesmo grupo
                trades_no_grupo = [t for t in self.trades_abertos if t['par'] in grupo]
                return len(trades_no_grupo) > 0
        
        return False
    
    def _volatilidade_excessiva(self, sinal: Dict) -> bool:
        """Detectar volatilidade excessiva (proteção contra notícias)"""
        # Implementar detecção de volatilidade anormal
        # Por enquanto, retornar False (implementação futura)
        return False
    
    def _atualizar_loss_diario(self):
        """Atualizar loss diário e resetar se necessário"""
        hoje = datetime.now().date()
        if hoje != self.ultimo_reset_diario:
            self.loss_diario = 0.0
            self.ultimo_reset_diario = hoje
    
    def registrar_trade_aberto(self, trade: Dict):
        """Registrar trade aberto"""
        trade_registro = {
            **trade,
            'timestamp_abertura': datetime.now().isoformat(),
            'status': 'ABERTO'
        }
        self.trades_abertos.append(trade_registro)
        logger.info(f"📝 TRADE REGISTRADO: {trade['par']} {trade['direcao']}")
    
    def registrar_trade_fechado(self, trade: Dict, resultado: Dict):
        """Registrar trade fechado e atualizar métricas"""
        # Remover dos trades abertos
        self.trades_abertos = [t for t in self.trades_abertos if t.get('id') != trade.get('id')]
        
        # Adicionar ao histórico
        trade_fechado = {
            **trade,
            'timestamp_fechamento': datetime.now().isoformat(),
            'status': 'FECHADO',
            **resultado
        }
        self.historico_trades.append(trade_fechado)
        
        # Atualizar métricas de performance
        self._atualizar_metricas_performance(resultado)
        
        logger.info(f"📊 TRADE FECHADO: {trade['par']} - Resultado: {resultado['lucro_percent']:.2f}%")
    
    def _atualizar_metricas_performance(self, resultado: Dict):
        """Atualizar métricas de performance"""
        self.performance_metrics['total_trades'] += 1
        
        if resultado['lucro_percent'] > 0:
            self.performance_metrics['trades_lucrativos'] += 1
            self.performance_metrics['lucro_total'] += resultado['lucro_absoluto']
            self.performance_metrics['maior_lucro'] = max(
                self.performance_metrics['maior_lucro'], 
                resultado['lucro_absoluto']
            )
        else:
            self.performance_metrics['trades_prejuizo'] += 1
            self.performance_metrics['prejuizo_total'] += abs(resultado['lucro_absoluto'])
            self.performance_metrics['maior_prejuizo'] = min(
                self.performance_metrics['maior_prejuizo'],
                resultado['lucro_absoluto']
            )
            # Atualizar loss diário
            self.loss_diario += abs(resultado['lucro_percent'])
        
        # Calcular win rate e profit factor
        total = self.performance_metrics['total_trades']
        if total > 0:
            self.performance_metrics['win_rate'] = (
                self.performance_metrics['trades_lucrativos'] / total * 100
            )
        
        if self.performance_metrics['prejuizo_total'] > 0:
            self.performance_metrics['profit_factor'] = (
                self.performance_metrics['lucro_total'] / self.performance_metrics['prejuizo_total']
            )
    
    def obter_estatisticas_risco(self) -> Dict:
        """Obter estatísticas completas de risco"""
        return {
            'trades_abertos': len(self.trades_abertos),
            'max_positions': self.max_positions,
            'drawdown_atual': self.drawdown_atual,
            'loss_diario': self.loss_diario,
            'performance': self.performance_metrics,
            'pares_ativos': [t['par'] for t in self.trades_abertos]
        }
    
    def verificar_stops_globais(self, precos_atuais: Dict) -> List[Dict]:
        """Verificar stops globais e retornar trades para fechar"""
        trades_fechar = []
        
        for trade in self.trades_abertos:
            par = trade['par']
            preco_atual = precos_atuais.get(par)
            
            if preco_atual is None:
                continue
            
            # Verificar stop loss
            if ((trade['direcao'] == 'BUY' and preco_atual <= trade['stop_loss']) or
                (trade['direcao'] == 'SELL' and preco_atual >= trade['stop_loss'])):
                
                trades_fechar.append({
                    'trade': trade,
                    'motivo': 'STOP_LOSS',
                    'preco_saida': preco_atual
                })
            
            # Verificar take profit
            elif ((trade['direcao'] == 'BUY' and preco_atual >= trade['take_profit']) or
                  (trade['direcao'] == 'SELL' and preco_atual <= trade['take_profit'])):
                
                trades_fechar.append({
                    'trade': trade,
                    'motivo': 'TAKE_PROFIT', 
                    'preco_saida': preco_atual
                })
        
        return trades_fechar
