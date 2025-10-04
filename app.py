from flask import Flask, render_template, jsonify
import threading
import time
import json
from datetime import datetime
import os

app = Flask(__name__)

# Importar estado global
try:
    from shared_state import shared_state
except ImportError:
    # Fallback se não conseguir importar
    class FallbackState:
        def __init__(self):
            self.bot_status = "🔧 INICIANDO"
            self.performance = {'ciclos': 0, 'trades': 0, 'saldo': 0.0, 'lucro': 0.0, 'vitorias': 0, 'derrotas': 0}
            self.conexao_exchange = False
            self.modalidade = "REAL"
            self.ultimos_sinais = []
            self.ultima_atualizacao = datetime.now().strftime("%H:%M:%S")
    
    shared_state = FallbackState()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/status')
def get_status():
    return jsonify({
        'bot_status': shared_state.bot_status,
        'performance': shared_state.performance,
        'conexao_exchange': shared_state.conexao_exchange,
        'modalidade': shared_state.modalidade,
        'ultima_atualizacao': shared_state.ultima_atualizacao,
        'ultimos_sinais': shared_state.ultimos_sinais[-10:]
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/performance')
def api_performance():
    return jsonify(shared_state.performance)

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_flask()
