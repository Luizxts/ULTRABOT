import logging
import threading
import time
from flask import Flask, render_template_string, jsonify, request
from trader.core import TradingBot
from telegram_bot.bot import TelegramBot
from config import HOST, PORT, FLASK_SECRET_KEY

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Variáveis globais
trading_bot = None
bot_thread = None
system_logs = []
real_trading_mode = False

# HTML Template para a interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ULTRABOT PRO - Sistema Avançado</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: white; 
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status { 
            border-left: 5px solid {{ '#00ff00' if status.running else '#ff0000' }};
        }
        .mode-card {
            border-left: 5px solid {{ '#ff9900' if status.real_trading else '#0099ff' }};
        }
        .btn { 
            padding: 12px 25px; 
            margin: 5px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .start { 
            background: #00ff00; 
            color: black; 
        }
        .stop { 
            background: #ff0000; 
            color: white; 
        }
        .real-mode {
            background: #ff9900;
            color: black;
        }
        .simulated-mode {
            background: #0099ff;
            color: white;
        }
        .log { 
            background: rgba(0,0,0,0.7); 
            padding: 15px; 
            border-radius: 10px; 
            margin-top: 20px; 
            max-height: 400px; 
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .log-entry {
            margin: 5px 0;
            padding: 5px;
            border-radius: 3px;
        }
        .log-info { background: rgba(0,255,0,0.1); }
        .log-warning { background: rgba(255,255,0,0.1); }
        .log-error { background: rgba(255,0,0,0.1); }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }
        .stat-item {
            text-align: center;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        .confirmation-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
        }
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1a2e;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #ff9900;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ULTRABOT PRO - SISTEMA AVANÇADO</h1>
            <p>Bot de Trading com IA - Intervalo: 5min - Modo Autônomo</p>
        </div>
        
        <div class="dashboard">
            <div class="card status">
                <h3>Status do Sistema</h3>
                <p><strong>Status:</strong> {{ '🟢 RODANDO' if status.running else '🔴 PARADO' }}</p>
                <p><strong>Modo:</strong> {{ '💰 REAL' if status.real_trading else '🎮 SIMULADO' }}</p>
                <p><strong>Análises:</strong> {{ status.trade_count }}</p>
                <p><strong>Lucro Total:</strong> ${{ status.total_profit }}</p>
                <p><strong>IA:</strong> 🧠 Ativa e Aprendendo</p>
            </div>
            
            <div class="card mode-card">
                <h3>Modo de Operação</h3>
                <p><strong>Modo Atual:</strong> {{ '💰 TRADING REAL' if status.real_trading else '🎮 SIMULAÇÃO' }}</p>
                <p><strong>Saldo:</strong> ${{ '18.34' if status.real_trading else '1000.00' }}</p>
                <p><strong>Risco:</strong> {{ 'ALTO ⚠️' if status.real_trading else 'ZERO ✅' }}</p>
                
                <div style="margin-top: 15px;">
                    {% if not status.real_trading %}
                    <button class="btn real-mode" onclick="showRealTradingConfirmation()">
                        🚀 Ativar Trading Real
                    </button>
                    {% else %}
                    <button class="btn simulated-mode" onclick="switchToSimulated()">
                        🎮 Voltar para Simulado
                    </button>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-item">
                <div>📊 Vitórias Consec.</div>
                <div><strong>{{ status.consecutive_wins }}</strong></div>
            </div>
            <div class="stat-item">
                <div>📉 Derrotas Consec.</div>
                <div><strong>{{ status.consecutive_losses }}</strong></div>
            </div>
            <div class="stat-item">
                <div>⏰ Próxima Análise</div>
                <div><strong>5 min</strong></div>
            </div>
            <div class="stat-item">
                <div>🧠 IA</div>
                <div><strong>Ativa</strong></div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            {% if not status.running %}
            <button class="btn start" onclick="startBot()">
                ▶️ Iniciar Bot
            </button>
            {% else %}
            <button class="btn stop" onclick="stopBot()">
                ⏹️ Parar Bot
            </button>
            {% endif %}
        </div>
        
        <div class="card">
            <h3>📝 Logs em Tempo Real</h3>
            <div class="log" id="logContainer">
                {% for log in logs %}
                <div class="log-entry log-{{ log.type }}">[{{ log.time }}] {{ log.message }}</div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <!-- Modal de Confirmação Trading Real -->
    <div id="realTradingModal" class="confirmation-modal">
        <div class="modal-content">
            <h2>⚠️ ALERTA DE RISCO ⚠️</h2>
            <p><strong>Você está prestes a ativar o MODO REAL</strong></p>
            <p>🔸 Serão utilizados fundos REAIS da sua conta</p>
            <p>🔸 Risco de PERDA FINANCEIRA real</p>
            <p>🔸 Saldo atual: <strong>$18.34</strong></p>
            <p>🔸 Máximo por trade: <strong>$50.00</strong></p>
            
            <div style="margin: 20px 0;">
                <label>
                    <input type="checkbox" id="riskCheckbox">
                    Eu entendo os riscos e desejo continuar
                </label>
            </div>
            
            <div>
                <button class="btn stop" onclick="hideRealTradingConfirmation()">Cancelar</button>
                <button class="btn real-mode" id="confirmRealBtn" disabled onclick="activateRealTrading()">
                    🚀 ATIVAR TRADING REAL
                </button>
            </div>
        </div>
    </div>
    
    <script>
        function startBot() {
            fetch('/start', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ real_trading: {{ 'true' if status.real_trading else 'false' }} })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('🤖 Bot iniciado com sucesso!');
                    location.reload();
                } else {
                    alert('❌ Erro: ' + data.message);
                }
            });
        }
        
        function stopBot() {
            fetch('/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('🛑 Bot parado!');
                    location.reload();
                }
            });
        }
        
        function showRealTradingConfirmation() {
            document.getElementById('realTradingModal').style.display = 'block';
        }
        
        function hideRealTradingConfirmation() {
            document.getElementById('realTradingModal').style.display = 'none';
        }
        
        function switchToSimulated() {
            if (confirm('Deseja voltar para o modo SIMULADO?')) {
                fetch('/switch_mode', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ real_trading: false })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('🎮 Modo simulado ativado!');
                        location.reload();
                    }
                });
            }
        }
        
        function activateRealTrading() {
            fetch('/switch_mode', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ real_trading: true })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('🚀 TRADING REAL ATIVADO! Use com cuidado!');
                    location.reload();
                }
            });
        }
        
        // Atualiza logs a cada 3 segundos
        setInterval(() => {
            fetch('/logs')
                .then(response => response.json())
                .then(data => {
                    const logContainer = document.getElementById('logContainer');
                    logContainer.innerHTML = data.logs;
                    logContainer.scrollTop = logContainer.scrollHeight;
                });
        }, 3000);
        
        // Controle do checkbox de risco
        document.addEventListener('DOMContentLoaded', function() {
            const checkbox = document.getElementById('riskCheckbox');
            const confirmBtn = document.getElementById('confirmRealBtn');
            
            if (checkbox && confirmBtn) {
                checkbox.addEventListener('change', function() {
                    confirmBtn.disabled = !this.checked;
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal"""
    global trading_bot, real_trading_mode
    
    status = {
        'running': trading_bot.is_running if trading_bot else False,
        'trade_count': trading_bot.trade_count if trading_bot else 0,
        'total_profit': f"{trading_bot.total_profit:.2f}" if trading_bot else "0.00",
        'real_trading': real_trading_mode,
        'consecutive_wins': trading_bot.consecutive_wins if trading_bot else 0,
        'consecutive_losses': trading_bot.consecutive_losses if trading_bot else 0,
    }
    
    return render_template_string(HTML_TEMPLATE, status=status, logs=system_logs[-20:])

@app.route('/start', methods=['POST'])
def start_bot():
    """Inicia o bot"""
    global trading_bot, bot_thread, real_trading_mode
    
    try:
        data = request.get_json()
        real_trading = data.get('real_trading', False) if data else real_trading_mode
        
        if trading_bot and trading_bot.is_running:
            return jsonify({'success': False, 'message': 'Bot já está rodando'})
        
        # Inicializa bots
        telegram_bot = TelegramBot()
        trading_bot = TradingBot(telegram_bot, real_trading=real_trading)
        
        # Inicia em thread separada
        bot_thread = threading.Thread(target=trading_bot.start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        add_log("🤖 Bot iniciado", "info")
        add_log(f"💼 Modo: {'REAL' if real_trading else 'SIMULADO'}", "info")
        add_log("🧠 IA ativada e aprendendo", "info")
        
        return jsonify({'success': True, 'message': 'Bot iniciado com sucesso'})
        
    except Exception as e:
        error_msg = f"❌ Erro ao iniciar bot: {e}"
        add_log(error_msg, "error")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/stop', methods=['POST'])
def stop_bot():
    """Para o bot"""
    global trading_bot
    
    try:
        if trading_bot:
            trading_bot.stop_bot()
            add_log("🛑 Bot parado pelo usuário", "warning")
            return jsonify({'success': True, 'message': 'Bot parado com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Nenhum bot ativo'})
            
    except Exception as e:
        error_msg = f"❌ Erro ao parar bot: {e}"
        add_log(error_msg, "error")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/switch_mode', methods=['POST'])
def switch_mode():
    """Alterna entre modo real e simulado"""
    global trading_bot, real_trading_mode, bot_thread
    
    try:
        data = request.get_json()
        new_mode = data.get('real_trading', False)
        
        # Para o bot se estiver rodando
        if trading_bot and trading_bot.is_running:
            trading_bot.stop_bot()
            time.sleep(2)
        
        real_trading_mode = new_mode
        
        mode_text = "REAL 💰" if new_mode else "SIMULADO 🎮"
        add_log(f"🔄 Modo alterado para: {mode_text}", "info")
        
        return jsonify({'success': True, 'message': f'Modo alterado para {mode_text}'})
        
    except Exception as e:
        error_msg = f"❌ Erro ao alterar modo: {e}"
        add_log(error_msg, "error")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/logs')
def get_logs():
    """Retorna logs atualizados"""
    logs_html = ""
    for log in system_logs[-20:]:
        logs_html += f'<div class="log-entry log-{log["type"]}">[{log["time"]}] {log["message"]}</div>'
    
    return jsonify({'logs': logs_html})

def add_log(message, log_type="info"):
    """Adiciona log ao sistema"""
    global system_logs
    timestamp = time.strftime("%H:%M:%S")
    system_logs.append({
        "time": timestamp,
        "message": message,
        "type": log_type
    })
    # Mantém apenas os últimos 50 logs
    system_logs = system_logs[-50:]

def start_web_server():
    """Inicia o servidor web"""
    add_log("🌐 Servidor ULTRABOT PRO inicializado", "info")
    add_log("⚡ Sistema 100% operacional", "info")
    add_log("🧠 IA carregada e pronta", "info")
    
    logging.info(f"🌐 Servidor rodando em: http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)

if __name__ == '__main__':
    start_web_server()
