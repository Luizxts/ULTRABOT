# app.py - DASHBOARD WEB AVANÇADO PARA ULTRABOT
from flask import Flask, render_template, jsonify, request
import json
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import logging
from collections import deque

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('UltraBotDashboard')

# Dados do bot em tempo real
class DashboardData:
    def __init__(self):
        self.performance_data = {
            'total_profit': 0.0,
            'daily_profit': 0.0,
            'win_rate': 75.4,
            'total_trades': 47,
            'active_trades': 2,
            'balance': 5280.50,
            'bot_status': 'RUNNING',
            'consecutive_wins': 5,
            'consecutive_losses': 0,
            'daily_drawdown': 1.2,
            'cycles_completed': 128
        }
        
        # Histórico de performance para gráficos
        self.equity_history = deque([5000.00] * 50, maxlen=50)
        self.profit_history = deque([0.0] * 50, maxlen=50)
        
        # Histórico de trades
        self.trade_history = self.generate_initial_trades()
        
        # Dados de mercado em tempo real
        self.market_data = {
            'btc_price': 51250.75,
            'eth_price': 2850.30,
            'sol_price': 102.45,
            'ada_price': 0.48,
            'market_sentiment': 'BULLISH',
            'fear_greed': 68,
            'total_volume': '245B',
            'btc_dominance': '52.3%'
        }
        
        # Ativos sendo monitorados
        self.watchlist = [
            {'symbol': 'BTCUSDT', 'price': 51250.75, 'change': 2.34, 'signal': 'BUY', 'confidence': 78},
            {'symbol': 'ETHUSDT', 'price': 2850.30, 'change': 1.56, 'signal': 'BUY', 'confidence': 65},
            {'symbol': 'SOLUSDT', 'price': 102.45, 'change': -0.45, 'signal': 'HOLD', 'confidence': 45},
            {'symbol': 'ADAUSDT', 'price': 0.48, 'change': 3.21, 'signal': 'BUY', 'confidence': 72},
            {'symbol': 'DOTUSDT', 'price': 6.89, 'change': 1.23, 'signal': 'HOLD', 'confidence': 52},
            {'symbol': 'LINKUSDT', 'price': 13.45, 'change': -1.20, 'signal': 'SELL', 'confidence': 61}
        ]
        
        # Métricas de risco
        self.risk_metrics = {
            'var_95': 125.50,
            'max_drawdown': 8.5,
            'sharpe_ratio': 2.1,
            'volatility': 12.3,
            'exposure': 45.2
        }
        
        # Sistema ativo
        self.last_update = datetime.now()
        self.update_thread = None
        self.start_simulation()

    def generate_initial_trades(self):
        """Gera histórico inicial de trades realista"""
        trades = []
        base_time = datetime.now() - timedelta(days=7)
        base_balance = 5000.00
        
        for i in range(47):
            trade_time = base_time + timedelta(hours=i*4)
            is_profitable = np.random.random() > 0.25  # 75% win rate
            
            if is_profitable:
                profit = np.random.uniform(15, 120)
            else:
                profit = -np.random.uniform(20, 80)
                
            trade = {
                'id': i + 1,
                'symbol': np.random.choice(['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT']),
                'side': 'BUY' if profit > 0 else 'SELL',
                'size': round(np.random.uniform(0.01, 0.1), 4),
                'price': round(np.random.uniform(100, 60000), 2),
                'profit': round(profit, 2),
                'timestamp': trade_time.isoformat(),
                'status': 'CLOSED',
                'confidence': np.random.randint(60, 95)
            }
            trades.append(trade)
            base_balance += profit
            
        return sorted(trades, key=lambda x: x['timestamp'], reverse=True)

    def simulate_live_activity(self):
        """Simula atividade em tempo real do bot"""
        while True:
            try:
                # Atualizar preços de mercado
                self.update_market_prices()
                
                # Simular novo trade ocasionalmente (5% de chance a cada atualização)
                if np.random.random() < 0.05 and len(self.trade_history) < 100:
                    self.add_new_trade()
                
                # Atualizar histórico de equity
                current_equity = self.performance_data['balance']
                self.equity_history.append(current_equity)
                
                # Atualizar métricas de performance
                self.update_performance_metrics()
                
                # Atualizar timestamp
                self.last_update = datetime.now()
                
                # Log de atividade
                logger.info("📊 Dashboard atualizado com dados simulados")
                
                # Esperar 3 segundos entre atualizações
                threading.Event().wait(3)
                
            except Exception as e:
                logger.error(f"Erro na simulação: {e}")
                threading.Event().wait(5)

    def update_market_prices(self):
        """Atualiza preços de mercado com movimentos realistas"""
        # BTC
        btc_change = np.random.normal(0, 0.001)
        self.market_data['btc_price'] *= (1 + btc_change)
        self.market_data['btc_price'] = round(self.market_data['btc_price'], 2)
        
        # ETH
        eth_change = np.random.normal(0, 0.0012)
        self.market_data['eth_price'] *= (1 + eth_change)
        self.market_data['eth_price'] = round(self.market_data['eth_price'], 2)
        
        # SOL
        sol_change = np.random.normal(0, 0.002)
        self.market_data['sol_price'] *= (1 + sol_change)
        self.market_data['sol_price'] = round(self.market_data['sol_price'], 2)
        
        # ADA
        ada_change = np.random.normal(0, 0.0015)
        self.market_data['ada_price'] *= (1 + ada_change)
        self.market_data['ada_price'] = round(self.market_data['ada_price'], 2)
        
        # Atualizar watchlist
        for asset in self.watchlist:
            change = np.random.normal(0, 0.0015)
            asset['price'] *= (1 + change)
            asset['price'] = round(asset['price'], 2)
            asset['change'] = round(change * 100, 2)
            
            # Atualizar sinais ocasionalmente
            if np.random.random() < 0.1:
                asset['signal'] = np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.4, 0.3, 0.3])
                asset['confidence'] = np.random.randint(50, 90)

    def add_new_trade(self):
        """Adiciona novo trade simulado"""
        last_id = max([t['id'] for t in self.trade_history]) if self.trade_history else 0
        is_profitable = np.random.random() > 0.25  # 75% win rate
        
        if is_profitable:
            profit = np.random.uniform(20, 150)
            side = 'BUY'
        else:
            profit = -np.random.uniform(25, 100)
            side = 'SELL'
        
        new_trade = {
            'id': last_id + 1,
            'symbol': np.random.choice(['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT']),
            'side': side,
            'size': round(np.random.uniform(0.02, 0.15), 4),
            'price': round(np.random.uniform(5000, 55000), 2),
            'profit': round(profit, 2),
            'timestamp': datetime.now().isoformat(),
            'status': 'CLOSED',
            'confidence': np.random.randint(65, 95)
        }
        
        self.trade_history.insert(0, new_trade)
        self.performance_data['balance'] += profit
        self.performance_data['total_profit'] += profit
        self.performance_data['total_trades'] += 1
        
        # Atualizar sequência
        if profit > 0:
            self.performance_data['consecutive_wins'] += 1
            self.performance_data['consecutive_losses'] = 0
        else:
            self.performance_data['consecutive_losses'] += 1
            self.performance_data['consecutive_wins'] = 0

    def update_performance_metrics(self):
        """Atualiza métricas de performance"""
        # Calcular win rate baseado nos últimos trades
        recent_trades = list(self.trade_history)[:20]
        if recent_trades:
            profitable = len([t for t in recent_trades if t['profit'] > 0])
            self.performance_data['win_rate'] = round((profitable / len(recent_trades)) * 100, 1)
        
        # Atualizar drawdown
        if self.equity_history:
            current_equity = self.equity_history[-1]
            peak_equity = max(self.equity_history)
            drawdown = ((peak_equity - current_equity) / peak_equity) * 100
            self.performance_data['daily_drawdown'] = round(drawdown, 2)
        
        # Incrementar ciclos
        self.performance_data['cycles_completed'] += 1

    def start_simulation(self):
        """Inicia a simulação em thread separada"""
        if not self.update_thread or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self.simulate_live_activity, daemon=True)
            self.update_thread.start()
            logger.info("🚀 Simulação do dashboard iniciada")

# Instância global dos dados
dashboard_data = DashboardData()

# Rotas da API
@app.route('/')
def index():
    """Página principal do dashboard"""
    return render_template('index.html')

@app.route('/api/performance')
def get_performance():
    """API para dados de performance"""
    return jsonify(dashboard_data.performance_data)

@app.route('/api/trades')
def get_trades():
    """API para histórico de trades"""
    return jsonify(list(dashboard_data.trade_history)[:20])

@app.route('/api/market')
def get_market_data():
    """API para dados de mercado"""
    return jsonify(dashboard_data.market_data)

@app.route('/api/watchlist')
def get_watchlist():
    """API para watchlist"""
    return jsonify(dashboard_data.watchlist)

@app.route('/api/risk')
def get_risk_metrics():
    """API para métricas de risco"""
    return jsonify(dashboard_data.risk_metrics)

@app.route('/api/equity-history')
def get_equity_history():
    """API para histórico de equity"""
    return jsonify(list(dashboard_data.equity_history))

@app.route('/api/profit-history')
def get_profit_history():
    """API para histórico de profit"""
    return jsonify(list(dashboard_data.profit_history))

@app.route('/api/control', methods=['POST'])
def control_bot():
    """API para controlar o bot"""
    action = request.json.get('action')
    
    if action == 'start':
        dashboard_data.performance_data['bot_status'] = "RUNNING"
        status = "🟢 OPERANDO"
    elif action == 'stop':
        dashboard_data.performance_data['bot_status'] = "STOPPED" 
        status = "🔴 PARADO"
    elif action == 'pause':
        dashboard_data.performance_data['bot_status'] = "PAUSED"
        status = "🟡 PAUSADO"
    else:
        return jsonify({'error': 'Ação inválida'}), 400
    
    logger.info(f"Bot controlado: {action} -> {status}")
    return jsonify({'status': 'success', 'bot_status': dashboard_data.performance_data['bot_status']})

@app.route('/api/status')
def get_system_status():
    """API para status completo do sistema"""
    return jsonify({
        'performance': dashboard_data.performance_data,
        'market': dashboard_data.market_data,
        'last_update': dashboard_data.last_update.isoformat(),
        'uptime': str(datetime.now() - (dashboard_data.last_update - timedelta(hours=2))),
        'system_health': 'EXCELLENT',
        'active_connections': 5
    })

# Health check para Railway
@app.route('/health')
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'UltraBot Dashboard'
    })

if __name__ == '__main__':
    # Obter porta do Railway
    port = int(os.environ.get('PORT', 5000))
    
    # Iniciar servidor
    logger.info(f"🚀 INICIANDO ULTRABOT DASHBOARD NA PORTA {port}")
    logger.info("📊 Dashboard: https://ultrabot-production.up.railway.app/")
    logger.info("❤️  Health Check: https://ultrabot-production.up.railway.app/health")
    
    app.run(host='0.0.0.0', port=port, debug=False)
