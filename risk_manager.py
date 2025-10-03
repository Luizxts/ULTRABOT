# risk_manager.py - GERENCIAMENTO DE RISCO INTELIGENTE
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque
from config import SECURITY_CONFIG, LOG_CONFIG

class AdvancedRiskManager:
    """
    Sistema avançado de gerenciamento de risco
    Monitora múltiplas métricas e aplica restrições
    """
    
    def __init__(self):
        self.config = SECURITY_CONFIG
        self.logger = self.setup_logger()
        
        # Histórico de trades
        self.trade_history = []
        self.recent_trades = deque(maxlen=50)
        
        # Estatísticas
        self.daily_stats = self.reset_daily_stats()
        self.weekly_stats = self.reset_weekly_stats()
        
        # Métricas de performance
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'current_streak': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
        }
        
        # Estado de risco
        self.risk_state = {
            'trading_allowed': True,
            'reason': 'OK',
            'cooldown_until': None
        }
        
        self.logger.info("🛡️  GERENCIADOR DE RISCO INICIALIZADO")

    def setup_logger(self):
        """Configura logger para risk manager"""
        logger = logging.getLogger('RiskManager')
        if LOG_CONFIG['log_colors']:
            formatter = logging.Formatter('\033[94m%(asctime)s\033[0m \033[91m%(levelname)s\033[0m \033[92m%(message)s\033[0m')
        else:
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
        
        return logger

    def reset_daily_stats(self):
        """Reseta estatísticas diárias"""
        return {
            'date': datetime.now().date(),
            'trades_count': 0,
            'profit_loss': 0.0,
            'max_drawdown': 0.0,
            'peak_balance': 0.0,
            'winning_trades': 0,
            'losing_trades': 0
        }

    def reset_weekly_stats(self):
        """Reseta estatísticas semanais"""
        return {
            'week_start': datetime.now().date(),
            'trades_count': 0,
            'profit_loss': 0.0,
            'win_rate': 0.0
        }

    def can_execute_trade(self, current_balance, signal_strength, market_conditions, trade_size):
        """Verifica se pode executar trade baseado em múltiplos fatores"""
        try:
            checks = {
                'daily_loss_limit': self.check_daily_loss_limit(current_balance),
                'max_drawdown': self.check_max_drawdown(current_balance),
                'consecutive_losses': self.check_consecutive_losses(),
                'market_volatility': self.check_market_volatility(market_conditions),
                'signal_strength': signal_strength >= self.config.get('min_signal_strength', 0.6),
                'time_restrictions': self.check_time_restrictions(),
                'trade_size_risk': self.check_trade_size_risk(trade_size, current_balance),
                'cooldown_period': self.check_cooldown_period(),
                'weekly_trade_limit': self.check_weekly_trade_limit(),
            }
            
            # Verificar se todos os checks passaram
            can_trade = all(checks.values())
            failed_checks = [k for k, v in checks.items() if not v]
            
            if failed_checks:
                self.risk_state['trading_allowed'] = False
                self.risk_state['reason'] = f"Checks falharam: {failed_checks}"
                self.logger.warning(f"🚫 TRADE BLOQUEADO: {failed_checks}")
            else:
                self.risk_state['trading_allowed'] = True
                self.risk_state['reason'] = 'OK'
                
            return can_trade, checks, self.risk_state
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA VERIFICAÇÃO DE RISCO: {e}")
            return False, {}, {'trading_allowed': False, 'reason': f'Erro: {e}'}

    def check_daily_loss_limit(self, current_balance):
        """Verifica limite de perda diária"""
        try:
            daily_loss_limit = self.config.get('daily_loss_limit', 0.05)
            initial_daily_balance = self.daily_stats.get('initial_balance', current_balance)
            
            # Se é o primeiro trade do dia, setar balance inicial
            if self.daily_stats['trades_count'] == 0:
                self.daily_stats['initial_balance'] = current_balance
                self.daily_stats['peak_balance'] = current_balance
                return True
            
            daily_pl = self.daily_stats['profit_loss']
            daily_loss_pct = abs(min(0, daily_pl)) / initial_daily_balance
            
            if daily_loss_pct > daily_loss_limit:
                self.logger.warning(f"📉 LIMITE DE PERDA DIÁRIA ATINGIDO: {daily_loss_pct:.2%} > {daily_loss_limit:.2%}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CHECK DE PERDA DIÁRIA: {e}")
            return True  # Fail open para segurança

    def check_max_drawdown(self, current_balance):
        """Verifica drawdown máximo"""
        try:
            max_drawdown = self.config.get('max_drawdown', 0.10)
            
            # Atualizar pico do dia
            if current_balance > self.daily_stats['peak_balance']:
                self.daily_stats['peak_balance'] = current_balance
            
            peak = self.daily_stats['peak_balance']
            if peak > 0:
                drawdown = (peak - current_balance) / peak
                self.daily_stats['max_drawdown'] = max(self.daily_stats['max_drawdown'], drawdown)
                
                if drawdown > max_drawdown:
                    self.logger.warning(f"📉 DRAWDOWN MÁXIMO ATINGIDO: {drawdown:.2%} > {max_drawdown:.2%}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CHECK DE DRAWDOWN: {e}")
            return True

    def check_consecutive_losses(self):
        """Verifica perdas consecutivas"""
        try:
            max_consecutive = self.config.get('max_consecutive_losses', 5)
            
            if len(self.recent_trades) < 2:
                return True
            
            consecutive_losses = 0
            for trade in reversed(self.recent_trades):
                if trade.get('profit_loss', 0) < 0:
                    consecutive_losses += 1
                else:
                    break
            
            if consecutive_losses >= max_consecutive:
                # Ativar cooldown
                cooldown_minutes = min(60, consecutive_losses * 15)  # 15min por loss consecutiva
                self.risk_state['cooldown_until'] = datetime.now() + timedelta(minutes=cooldown_minutes)
                self.logger.warning(f"⏳ COOLDOWN ATIVADO: {consecutive_losses} perdas consecutivas. Retorno em {cooldown_minutes}min")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CHECK DE PERDAS CONSECUTIVAS: {e}")
            return True

    def check_market_volatility(self, market_conditions):
        """Verifica condições de mercado"""
        try:
            if not self.config.get('volatility_check', True):
                return True
            
            spread = market_conditions.get('spread', 0)
            volume_health = market_conditions.get('volume_health', 'UNKNOWN')
            
            # Verificar spread
            if spread > 0.15:  # Spread > 0.15%
                self.logger.warning(f"📊 SPREAD ALTO DETECTADO: {spread:.2f}%")
                return False
            
            # Verificar volume
            if volume_health in ['LOW_VOLUME', 'POOR_CONDITIONS']:
                self.logger.warning(f"📊 CONDIÇÕES DE MERCADO RUINS: {volume_health}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CHECK DE VOLATILIDADE: {e}")
            return True

    def check_time_restrictions(self):
        """Restrições de horário"""
        try:
            if not self.config.get('time_restrictions', True):
                return True
            
            now = datetime.now()
            current_hour = now.hour
            current_weekday = now.weekday()
            
            # Não operar em horários de baixa liquidez (madrugada)
            if current_hour in [0, 1, 2, 3, 4]:
                self.logger.info("🌙 HORÁRIO DE BAIXA LIQUIDEZ - Trading não recomendado")
                return False
            
            # Fim de semana - mercados fecham cedo
            if current_weekday >= 5:  # Sábado ou Domingo
                self.logger.info("🎉 FIM DE SEMANA - Trading limitado")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CHECK DE HORÁRIO: {e}")
            return True

    def check_trade_size_risk(self, trade_size, current_balance):
        """Verifica risco do tamanho do trade"""
        try:
            if current_balance <= 0:
                return False
            
            trade_value = trade_size * current_balance  # Estimativa
            risk_per_trade = self.config.get('risk_per_trade', 0.02)
            max_trade_value = current_balance * risk_per_trade
            
            if trade_value > max_trade_value * 1.5:  # 50% de tolerância
                self.logger.warning(f"💰 TAMANHO DE TRADE MUITO ALTO: ${trade_value:.2f} > ${max_trade_value:.2f}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CHECK DE TAMANHO: {e}")
            return True

    def check_cooldown_period(self):
        """Verifica se está em período de cooldown"""
        try:
            if self.risk_state['cooldown_until'] and datetime.now() < self.risk_state['cooldown_until']:
                remaining = (self.risk_state['cooldown_until'] - datetime.now()).total_seconds() / 60
                self.logger.info(f"⏳ EM COOLDOWN: {remaining:.1f}min restantes")
                return False
            else:
                self.risk_state['cooldown_until'] = None
                return True
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CHECK DE COOLDOWN: {e}")
            return True

    def check_weekly_trade_limit(self):
        """Verifica limite semanal de trades"""
        try:
            max_weekly_trades = self.config.get('max_weekly_trades', 100)
            
            # Verificar se semana mudou
            current_week = datetime.now().date().isocalendar()[1]
            stats_week = self.weekly_stats['week_start'].isocalendar()[1]
            
            if current_week != stats_week:
                self.weekly_stats = self.reset_weekly_stats()
                self.weekly_stats['week_start'] = datetime.now().date()
            
            if self.weekly_stats['trades_count'] >= max_weekly_trades:
                self.logger.warning(f"📊 LIMITE SEMANAL DE TRADES ATINGIDO: {self.weekly_stats['trades_count']}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CHECK SEMANAL: {e}")
            return True

    def record_trade(self, trade_data):
        """Registra trade para histórico e estatísticas"""
        try:
            trade_data['timestamp'] = datetime.now()
            self.trade_history.append(trade_data)
            self.recent_trades.append(trade_data)
            
            # Atualizar estatísticas diárias
            current_date = datetime.now().date()
            if current_date != self.daily_stats['date']:
                self.daily_stats = self.reset_daily_stats()
                self.daily_stats['date'] = current_date
            
            self.daily_stats['trades_count'] += 1
            pl = trade_data.get('profit_loss', 0)
            self.daily_stats['profit_loss'] += pl
            
            if pl > 0:
                self.daily_stats['winning_trades'] += 1
                self.performance_metrics['winning_trades'] += 1
                self.performance_metrics['current_streak'] = max(0, self.performance_metrics['current_streak']) + 1
                self.performance_metrics['max_consecutive_wins'] = max(
                    self.performance_metrics['max_consecutive_wins'], 
                    self.performance_metrics['current_streak']
                )
            else:
                self.daily_stats['losing_trades'] += 1
                self.performance_metrics['losing_trades'] += 1
                self.performance_metrics['current_streak'] = min(0, self.performance_metrics['current_streak']) - 1
                self.performance_metrics['max_consecutive_losses'] = max(
                    self.performance_metrics['max_consecutive_losses'], 
                    abs(self.performance_metrics['current_streak'])
                )
            
            # Atualizar métricas gerais
            self.performance_metrics['total_trades'] += 1
            self.performance_metrics['total_profit'] += pl
            
            if pl > self.performance_metrics['largest_win']:
                self.performance_metrics['largest_win'] = pl
            if pl < self.performance_metrics['largest_loss']:
                self.performance_metrics['largest_loss'] = pl
            
            # Atualizar estatísticas semanais
            self.weekly_stats['trades_count'] += 1
            self.weekly_stats['profit_loss'] += pl
            
            self.logger.info(f"📝 TRADE REGISTRADO: {trade_data.get('signal', 'UNKNOWN')} | P/L: ${pl:.2f}")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO REGISTRAR TRADE: {e}")

    def get_risk_metrics(self):
        """Retorna métricas de risco atuais"""
        try:
            total_trades = self.performance_metrics['total_trades']
            winning_trades = self.performance_metrics['winning_trades']
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            return {
                'daily_trades': self.daily_stats['trades_count'],
                'daily_pl': self.daily_stats['profit_loss'],
                'daily_drawdown': self.daily_stats['max_drawdown'],
                'daily_win_rate': self.daily_stats['winning_trades'] / self.daily_stats['trades_count'] if self.daily_stats['trades_count'] > 0 else 0,
                
                'total_trades': total_trades,
                'win_rate': win_rate,
                'total_profit': self.performance_metrics['total_profit'],
                'largest_win': self.performance_metrics['largest_win'],
                'largest_loss': self.performance_metrics['largest_loss'],
                'current_streak': self.performance_metrics['current_streak'],
                'max_consecutive_wins': self.performance_metrics['max_consecutive_wins'],
                'max_consecutive_losses': self.performance_metrics['max_consecutive_losses'],
                
                'weekly_trades': self.weekly_stats['trades_count'],
                'weekly_pl': self.weekly_stats['profit_loss'],
                
                'trading_allowed': self.risk_state['trading_allowed'],
                'risk_reason': self.risk_state['reason'],
                'cooldown_until': self.risk_state['cooldown_until'],
            }
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO OBTER MÉTRICAS: {e}")
            return {}

    def get_trading_recommendation(self, current_balance, market_conditions):
        """Fornece recomendação de trading baseada em risco"""
        try:
            metrics = self.get_risk_metrics()
            
            if not self.risk_state['trading_allowed']:
                return "NO_TRADING", f"Trading bloqueado: {self.risk_state['reason']}"
            
            # Analisar condições
            recommendations = []
            
            # Verificar drawdown
            if metrics['daily_drawdown'] > 0.05:
                recommendations.append("REDUCE_SIZE")
            
            # Verificar streak
            if abs(metrics['current_streak']) >= 3:
                if metrics['current_streak'] > 0:
                    recommendations.append("TAKE_PROFITS")
                else:
                    recommendations.append("REDUCE_RISK")
            
            # Verificar volume de trades
            if metrics['daily_trades'] > 20:
                recommendations.append("SLOW_DOWN")
            
            if not recommendations:
                return "NORMAL", "Condições normais de trading"
            else:
                return "CAUTION", f"Recomendações: {', '.join(recommendations)}"
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NA RECOMENDAÇÃO: {e}")
            return "ERROR", f"Erro na análise: {e}"

# Instância global
risk_manager = AdvancedRiskManager()
