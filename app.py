# app.py - INTERFACE WEB DASHBOARD
from flask import Flask, render_template, jsonify, request
import json
import threading
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# Dados simulados para o dashboard
class DashboardData:
    def __init__(self):
        self.performance_data = {
            'total_profit': 0.0,
            'daily_profit': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'active_trades': 0,
            'balance': 0.0
        }
        self.trade_history = []
        self.market_data = {}
        self.bot_status = "INITIALIZING"

dashboard_data = DashboardData()

@app.route('/')
def index():
    """Página principal do dashboard"""
    return render_template('index.html')

@app.route('/api/performance')
def get_performance():
    """API para dados de performance"""
    return jsonify({
        'total_profit': dashboard_data.performance_data['total_profit'],
        'daily_profit': dashboard_data.performance_data['daily_profit'],
        'win_rate': dashboard_data.performance_data['win_rate'],
        'total_trades': dashboard_data.performance_data['total_trades'],
        'active_trades': dashboard_data.performance_data['active_trades'],
        'balance': dashboard_data.performance_data['balance'],
        'bot_status': dashboard_data.bot_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trades')
def get_trades():
    """API para histórico de trades"""
    return jsonify(dashboard_data.trade_history[-50:])  # Últimos 50 trades

@app.route('/api/market')
def get_market_data():
    """API para dados de mercado"""
    return jsonify(dashboard_data.market_data)

@app.route('/api/control', methods=['POST'])
def control_bot():
    """API para controlar o bot"""
    action = request.json.get('action')
    
    if action == 'start':
        dashboard_data.bot_status = "RUNNING"
        # Aqui você integraria com o start real do bot
    elif action == 'stop':
        dashboard_data.bot_status = "STOPPED"
        # Aqui você integraria com o stop real do bot
    elif action == 'pause':
        dashboard_data.bot_status = "PAUSED"
    
    return jsonify({'status': 'success', 'bot_status': dashboard_data.bot_status})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """API para atualizar configurações"""
    settings = request.json
    # Aqui você salvaria as configurações no config.py
    return jsonify({'status': 'success', 'message': 'Settings updated'})

def update_dashboard_data():
    """Atualiza dados do dashboard em tempo real"""
    # Esta função seria integrada com o robô principal
    # para atualizar os dados em tempo real
    while True:
        try:
            # Simular atualização de dados
            dashboard_data.performance_data['balance'] += 0.1
            dashboard_data.performance_data['total_trades'] += 1
            
            # Adicionar trade simulado
            if len(dashboard_data.trade_history) < 100:
                new_trade = {
                    'id': len(dashboard_data.trade_history) + 1,
                    'symbol': 'BTCUSDT',
                    'side': 'BUY' if len(dashboard_data.trade_history) % 2 == 0 else 'SELL',
                    'size': 0.001,
                    'price': 50000 + len(dashboard_data.trade_history) * 10,
                    'profit': round(np.random.uniform(-10, 15), 2),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'CLOSED'
                }
                dashboard_data.trade_history.append(new_trade)
            
            # Atualizar dados de mercado
            dashboard_data.market_data = {
                'btc_price': 50000 + np.random.uniform(-1000, 1000),
                'eth_price': 3000 + np.random.uniform(-100, 100),
                'market_sentiment': 'BULLISH' if np.random.random() > 0.5 else 'BEARISH',
                'fear_greed': np.random.randint(20, 80)
            }
            
            threading.Event().wait(5)  # Atualizar a cada 5 segundos
            
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")

if __name__ == '__main__':
    # Iniciar thread de atualização de dados
    update_thread = threading.Thread(target=update_dashboard_data, daemon=True)
    update_thread.start()
    
    # Iniciar servidor web
    app.run(host='0.0.0.0', port=5000, debug=False)
