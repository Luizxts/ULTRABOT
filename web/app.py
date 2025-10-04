from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime
import os
import sys

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.state_manager import GlobalState
    from core.config_manager import config
except ImportError as e:
    print(f"❌ Erro de importação: {e}")

app = Flask(__name__)
state = GlobalState()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API para status completo do bot"""
    try:
        status_data = {
            'bot_status': state.bot_status,
            'performance': state.performance,
            'conexao_exchange': state.conexao_exchange,
            'modalidade': state.modalidade,
            'ultima_atualizacao': state.ultima_atualizacao,
            'ultimos_sinais': state.ultimos_sinais,
            'risk_metrics': state.risk_metrics,
            'ai_metrics': state.ai_metrics,
            'strategy_metrics': state.strategy_metrics,
            'trades_ativos': state.trades_ativos,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(status_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def api_performance():
    """API específica para dados de performance"""
    try:
        return jsonify(state.performance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    """Health check para monitoramento"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'ultrabot-pro-max'
    })

@app.route('/api/config')
def api_config():
    """API para configurações (sem dados sensíveis)"""
    try:
        safe_config = {
            'trading': {
                'pares_monitorados': config.TRADING_CONFIG['pares_monitorados'],
                'intervalo_analise': config.TRADING_CONFIG['intervalo_analise'],
                'max_positions': config.TRADING_CONFIG['max_positions'],
                'risk_per_trade': config.TRADING_CONFIG['risk_per_trade']
            },
            'ai': {
                'learning_enabled': config.AI_CONFIG['learning_enabled'],
                'adaptive_parameters': config.AI_CONFIG['adaptive_parameters']
            }
        }
        return jsonify(safe_config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/actions', methods=['POST'])
def api_actions():
    """API para ações no bot"""
    try:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'status_update':
            # Forçar atualização de status
            return jsonify({'status': 'updated'})
        elif action == 'get_logs':
            # Retornar últimos logs (simplificado)
            return jsonify({'logs': []})
        else:
            return jsonify({'error': 'Ação não reconhecida'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

def run_flask():
    """Executar servidor Flask"""
    try:
        port = config.WEB_CONFIG['port']
        host = config.WEB_CONFIG['host']
        
        print(f"🌐 Iniciando servidor web em {host}:{port}")
        
        # Não usar reloader em produção
        app.run(
            host=host,
            port=port,
            debug=config.WEB_CONFIG['debug'],
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor web: {e}")

if __name__ == "__main__":
    run_flask()
