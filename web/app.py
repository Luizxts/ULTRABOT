from flask import Flask, render_template, jsonify, request
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
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(status_data)
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

def run_flask():
    """Executar servidor Flask"""
    try:
        port = config.WEB_CONFIG['port']
        host = config.WEB_CONFIG['host']
        
        print(f"🌐 Iniciando servidor web em {host}:{port}")
        
        app.run(
            host=host,
            port=port,
            debug=config.WEB_CONFIG['debug'],
            use_reloader=False
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor web: {e}")

if __name__ == "__main__":
    run_flask()
