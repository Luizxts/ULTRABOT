import logging
import asyncio
from typing import Dict, List, Optional
import random
from datetime import datetime, timedelta
import json
import os

try:
    from config import (
        TRADING_INTERVAL, TRADE_PROBABILITY, WIN_RATE, 
        MAX_TRADE_AMOUNT, TRADE_PERCENTAGE, SAVE_HISTORY,
        MAX_HISTORY_ENTRIES, MAX_NOTIFICATIONS
    )
except ImportError:
    # Valores padrão
    TRADING_INTERVAL = 600  # 10 minutos
    TRADE_PROBABILITY = 0.3  # 30%
    WIN_RATE = 0.65  # 65%
    MAX_TRADE_AMOUNT = 50  # $50
    TRADE_PERCENTAGE = 0.05  # 5%
    SAVE_HISTORY = True
    MAX_HISTORY_ENTRIES = 100
    MAX_NOTIFICATIONS = 50

logger = logging.getLogger(__name__)

class UltraBot:
    def __init__(self, mode: str = "CONSERVATIVE"):
        self.mode = mode
        self.running = False
        self.balance = 1000.00
        self.available_balance = 850.00
        self.allocated_balance = 150.00
        self.trades_today = 0
        self.wins_today = 0
        self.losses_today = 0
        self.profit_today = 0.00
        self.last_update = datetime.now()
        self.last_trade_time = None
        self.consecutive_no_trades = 0
        self.history = []
        self.notification_queue = []
        
        # Configurações do config.py
        self.trading_interval = TRADING_INTERVAL
        self.trade_probability = TRADE_PROBABILITY
        self.win_rate = WIN_RATE
        self.max_trade_amount = MAX_TRADE_AMOUNT
        self.trade_percentage = TRADE_PERCENTAGE
        self.save_history = SAVE_HISTORY
        self.max_history_entries = MAX_HISTORY_ENTRIES
        self.max_notifications = MAX_NOTIFICATIONS
        
        # Carregar histórico se existir
        if self.save_history:
            self.load_history()
        
        logger.info(f"🤖 ULTRABOT inicializado - Modo {mode} Ativado!")
        logger.info(f"⚙️  Configurações: Intervalo {self.trading_interval}s, Probabilidade {self.trade_probability*100}%, Win Rate {self.win_rate*100}%")
    
    def load_history(self):
        """Carrega o histórico de trades do arquivo"""
        try:
            if os.path.exists('trading_history.json'):
                with open('trading_history.json', 'r') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    # Carregar estatísticas do dia se for o mesmo dia
                    today = datetime.now().strftime('%Y-%m-%d')
                    if data.get('last_date') == today:
                        self.trades_today = data.get('trades_today', 0)
                        self.wins_today = data.get('wins_today', 0)
                        self.losses_today = data.get('losses_today', 0)
                        self.profit_today = data.get('profit_today', 0.0)
                logger.info(f"📁 Histórico carregado: {len(self.history)} trades")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar histórico: {e}")
    
    def save_history(self):
        """Salva o histórico de trades no arquivo"""
        if not self.save_history:
            return
            
        try:
            data = {
                'history': self.history[-self.max_history_entries:],
                'last_date': datetime.now().strftime('%Y-%m-%d'),
                'trades_today': self.trades_today,
                'wins_today': self.wins_today,
                'losses_today': self.losses_today,
                'profit_today': self.profit_today,
                'last_update': datetime.now().isoformat()
            }
            with open('trading_history.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar histórico: {e}")
    
    def add_notification(self, message: str, level: str = "info"):
        """Adiciona notificação para enviar via Telegram/Web"""
        notification = {
            'id': len(self.notification_queue) + 1,
            'message': message,
            'level': level,  # info, warning, success, error
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        self.notification_queue.append(notification)
        
        # Manter apenas últimas notificações
        if len(self.notification_queue) > self.max_notifications:
            self.notification_queue = self.notification_queue[-self.max_notifications:]
        
        logger.info(f"📢 Notificação: {message}")
        return notification
    
    def get_notifications(self, unread_only: bool = False):
        """Retorna notificações"""
        if unread_only:
            return [n for n in self.notification_queue if not n['read']]
        return self.notification_queue
    
    def mark_notification_read(self, notification_id: int):
        """Marca notificação como lida"""
        for notification in self.notification_queue:
            if notification['id'] == notification_id:
                notification['read'] = True
                break
    
    async def start(self):
        """Inicia o bot de trading"""
        if self.running:
            logger.warning("⚠️ Bot já está rodando")
            return False
        
        self.running = True
        start_msg = f"🚀 ULTRABOT INICIADO - Modo Ganancioso | Intervalo: {self.trading_interval//60}min"
        logger.info(start_msg)
        self.add_notification(start_msg, "success")
        
        # Iniciar loop de trading
        asyncio.create_task(self.trading_loop())
        
        return True
    
    async def stop(self):
        """Para o bot de trading"""
        if not self.running:
            return True
            
        self.running = False
        stop_msg = f"⏹️ ULTRABOT PARADO | Trades: {self.trades_today} | Lucro: ${self.profit_today:.2f}"
        logger.info(stop_msg)
        self.add_notification(stop_msg, "info")
        
        # Salvar histórico ao parar
        if self.save_history:
            self.save_history()
        
        return True
    
    async def trading_loop(self):
        """Loop principal de trading"""
        analysis_count = 0
        
        while self.running:
            try:
                analysis_count += 1
                
                # Mensagem de análise iniciada
                if analysis_count % 3 == 1:  # A cada 3 análises
                    analysis_msg = f"🔍 Análise #{analysis_count} em andamento..."
                    self.add_notification(analysis_msg, "info")
                
                # Simular análise de mercado
                should_trade = await self.analyze_market()
                
                if should_trade:
                    trade_result = await self.execute_trade()
                    if trade_result:
                        self.consecutive_no_trades = 0
                        self.last_trade_time = datetime.now()
                        
                        # Notificação de trade bem-sucedido
                        trade_msg = f"💰 TRADE EXECUTADO: {trade_result}"
                        self.add_notification(trade_msg, "success")
                else:
                    self.consecutive_no_trades += 1
                    
                    # Notificar a cada 2 vezes seguidas sem trade
                    if self.consecutive_no_trades % 2 == 0:
                        no_trade_msg = f"⏸️  Análise #{analysis_count}: Mercado não favorável - Aguardando oportunidade..."
                        self.add_notification(no_trade_msg, "warning")
                        self.consecutive_no_trades = 0
                
                # Salvar histórico periodicamente
                if self.save_history and analysis_count % 5 == 0:
                    self.save_history()
                
                # Esperar intervalo configurado
                await asyncio.sleep(self.trading_interval)
                
            except Exception as e:
                error_msg = f"❌ Erro no loop de trading: {e}"
                logger.error(error_msg)
                self.add_notification(error_msg, "error")
                await asyncio.sleep(60)
    
    async def analyze_market(self) -> bool:
        """Analisa condições de mercado para decidir se deve trade"""
        # Usar probabilidade configurada
        market_conditions = random.random()
        
        if market_conditions < self.trade_probability:
            logger.info("✅ Sinal de compra identificado - Mercado favorável")
            return True
        else:
            logger.info("⏸️  Condições de mercado não ideais - Aguardando...")
            return False
    
    async def execute_trade(self):
        """Executa um trade simulado"""
        try:
            trade_amount = min(self.available_balance * self.trade_percentage, self.max_trade_amount)
            if trade_amount < 5:
                logger.info("💡 Valor de trade muito baixo - Aguardando...")
                return None
            
            # Simular resultado do trade com win rate configurado
            is_win = random.random() < self.win_rate
            profit_loss = trade_amount * 0.03 if is_win else -trade_amount * 0.02
            
            # Criar registro do trade
            trade_record = {
                'id': len(self.history) + 1,
                'timestamp': datetime.now().isoformat(),
                'amount': trade_amount,
                'profit_loss': profit_loss,
                'type': 'WIN' if is_win else 'LOSS',
                'balance_after': self.balance + profit_loss,
                'symbol': 'BTCUSDT'
            }
            
            # Atualizar estatísticas
            self.trades_today += 1
            if is_win:
                self.wins_today += 1
            else:
                self.losses_today += 1
            
            self.profit_today += profit_loss
            self.balance += profit_loss
            self.available_balance += profit_loss
            
            # Adicionar ao histórico
            self.history.append(trade_record)
            
            # Log detalhado
            log_msg = f"💰 Trade executado: {'✅ WIN' if is_win else '❌ LOSS'} - ${profit_loss:+.2f}"
            logger.info(log_msg)
            logger.info(f"📊 Estatísticas: Trades {self.trades_today} | W/L: {self.wins_today}/{self.losses_today} | Lucro: ${self.profit_today:.2f}")
            
            return f"{'✅ WIN' if is_win else '❌ LOSS'} | ${profit_loss:+.2f} | Saldo: ${self.balance:.2f}"
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar trade: {e}")
            return None
    
    def get_trading_history(self, limit: int = 20):
        """Retorna histórico de trades"""
        return self.history[-limit:] if self.history else []
    
    def get_daily_stats(self):
        """Retorna estatísticas do dia"""
        win_rate = (self.wins_today / self.trades_today * 100) if self.trades_today > 0 else 0.0
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'trades': self.trades_today,
            'wins': self.wins_today,
            'losses': self.losses_today,
            'profit': round(self.profit_today, 2),
            'win_rate': round(win_rate, 1),
            'balance': round(self.balance, 2),
            'config': {
                'interval': self.trading_interval,
                'probability': self.trade_probability,
                'win_rate': self.win_rate
            }
        }
    
    def get_status(self) -> Dict:
        """Retorna status atual do bot"""
        win_rate = (self.wins_today / self.trades_today * 100) if self.trades_today > 0 else 0.0
        
        # Calcular próximo trade
        next_trade_in = "AGORA"
        if self.last_trade_time:
            time_since_last = datetime.now() - self.last_trade_time
            minutes_since = time_since_last.total_seconds() / 60
            next_in = max(0, self.trading_interval/60 - minutes_since)
            next_trade_in = f"{next_in:.1f}min"
        
        return {
            'running': self.running,
            'mode': self.mode,
            'balance': round(self.balance, 2),
            'available_balance': round(self.available_balance, 2),
            'allocated_balance': round(self.allocated_balance, 2),
            'trades_today': self.trades_today,
            'wins_today': self.wins_today,
            'losses_today': self.losses_today,
            'profit_today': round(self.profit_today, 2),
            'win_rate': round(win_rate, 1),
            'next_trade_in': next_trade_in,
            'notifications_count': len([n for n in self.notification_queue if not n['read']]),
            'total_notifications': len(self.notification_queue),
            'config': {
                'interval': self.trading_interval,
                'probability': self.trade_probability,
                'win_rate': self.win_rate
            },
            'last_update': datetime.now().isoformat()
        }
    
    def reset_daily_stats(self):
        """Reseta estatísticas diárias"""
        self.trades_today = 0
        self.wins_today = 0
        self.losses_today = 0
        self.profit_today = 0.00
        self.last_update = datetime.now()
        self.consecutive_no_trades = 0
        self.add_notification("📊 Estatísticas diárias resetadas", "info")
        logger.info("📊 Estatísticas diárias resetadas")
