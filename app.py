import logging
import threading
import time
import json
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
trade_history = []
last_update = time.time()

# HTML Template PROFISSIONAL
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 ULTRABOT PRO - TRADING AUTÔNOMO</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="30">
    <style>
        :root {
            --primary: #00ff88;
            --secondary: #0088ff;
            --danger: #ff4444;
            --warning: #ffaa00;
            --dark: #0f0f23;
            --darker: #0a0a1a;
        }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 100%);
            color: white; 
            min-height: 100vh;
        }
        
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
        }
        
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            padding: 25px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 25px;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            padding: 25px;
            border-radius: 20px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.3);
        }
        
        .status { 
            border-left: 6px solid var(--primary);
        }
        
        .mode-card {
            border-left: 6px solid var(--secondary);
        }
        
        .btn { 
            padding: 14px 28px; 
            margin: 8px; 
            border: none; 
            border-radius: 12px; 
            cursor: pointer; 
            font-weight: bold;
            font-size: 1em;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        
        .start { 
            background: var(--primary); 
            color: black; 
        }
        
        .stop { 
            background: var(--danger); 
            color: white; 
        }
        
        .real-mode {
            background: var(--warning);
            color: black;
        }
        
        .simulated-mode {
            background: var(--secondary);
            color: white;
        }
        
        .log-container { 
            background: rgba(0,0,0,0.8); 
            padding: 20px; 
            border-radius: 15px; 
            margin-top: 25px; 
            max-height: 500px; 
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .log-entry {
            margin: 8px 0;
            padding: 10px;
            border-radius: 8px;
            border-left: 4px solid transparent;
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .log-info { 
            background: rgba(0,255,136,0.1); 
            border-left-color: var(--primary);
        }
        
        .log-warning { 
            background: rgba(255,170,0,0.1); 
            border-left-color: var(--warning);
        }
        
        .log-error { 
            background: rgba(255,68,68,0.1); 
            border-left-color: var(--danger);
        }
        
        .log-trade { 
            background: rgba(0,136,255,0.1); 
            border-left-color: var(--secondary);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            margin: 5px 0;
        }
        
        .profit-positive { color: var(--primary); }
        .profit-negative { color: var(--danger); }
        
        .trades-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .trade-item {
            padding: 15px;
            border-radius: 12px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        .trade-win {
            border-left: 4px solid var(--primary);
        }
        
        .trade-loss {
            border-left: 4px solid var(--danger);
        }
        
        .auto-refresh {
            text-align: center;
            margin: 15px 0;
            color: var(--secondary);
            font-size: 0.9em;
        }
        
        .last-update {
            text-align: right;
            font-size: 0.8em;
            color: rgba(255,255,255,0.5);
            margin-top: 10px;
        }
        
        .loading {
            opacity: 0.7;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ULTRABOT PRO - TRADING AUTÔNOMO</h1>
            <p>Sistema de Trading com IA • Intervalo: 5min • Atualização Automática</p>
        </div>
        
        <div class="dashboard">
            <div class="card status">
                <h3>📊 STATUS DO SISTEMA</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div>Status</div>
                        <div class="stat-value">{{ '🟢 RODANDO' if status.running else '🔴 PARADO' }}</div>
                    </div>
                    <div class="stat-item">
                        <div>Modo</div>
                        <div class="stat-value">{{ '💰 REAL' if status.real_trading else '🎮 SIMULADO' }}</div>
                    </div>
                    <div class="stat-item">
                        <div>Análises</div>
                        <div class="stat-value">{{ status.analysis_count }}</div>
                    </div>
                    <div class="stat-item">
                        <div>Lucro Total</div>
                        <div class="stat-value {{ 'profit-positive' if status.total_profit|float > 0 else 'profit-negative' }}">${{ status.total_profit }}</div>
                    </div>
                </div>
            </div>
            
            <div class="card mode-card">
                <h3>⚙️ MODO DE OPERAÇÃO</h3>
                <p><strong>Modo Atual:</strong> {{ '💰 TRADING REAL' if status.real_trading else '🎮 SIMULAÇÃO' }}</p>
                <p><strong>Saldo:</strong> ${{ '18.34' if status.real_trading else '1000.00' }}</p>
                <p><strong>Risco:</strong> {{ 'ALTO ⚠️' if status.real_trading else 'ZERO ✅' }}</p>
                
                <div style="margin-top: 20px;">
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
                <div>🎯 Vitórias Consec.</div>
                <div class="stat-value">{{ status.consecutive_wins }}</div>
            </div>
            <div class="stat-item">
                <div>📉 Derrotas Consec.</div>
                <div class="stat-value">{{ status.consecutive_losses }}</div>
            </div>
            <div class="stat-item">
                <div>⏰ Próxima Análise</div>
                <div class="stat-value">{{ status.next_analysis }} min</div>
            </div>
            <div class="stat-item">
                <div>🧠 IA</div>
                <div class="stat-value">Ativa</div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 25px 0;">
            {% if not status.running %}
            <button class="btn start" onclick="startBot()" id="startBtn">
                ▶️ Iniciar Bot
            </button>
            {% else %}
            <button class="btn stop" onclick="stopBot()" id="stopBtn">
                ⏹️ Parar Bot
            </button>
            {% endif %}
        </div>

        <!-- HISTÓRICO DE TRADES -->
        {% if trades %}
        <div class="card">
            <h3>📈 HISTÓRICO DE TRADES RECENTES</h3>
            <div class="trades-grid">
                {% for trade in trades[-6:] %}
                <div class="trade-item {{ 'trade-win' if trade.profit > 0 else 'trade-loss' }}">
                    <strong>{{ trade.symbol }}</strong> • {{ trade.side }}<br>
                    <span style="color: {{ '#00ff88' if trade.profit > 0 else '#ff4444' }};">
                        {{ '+$' if trade.profit > 0 else '$' }}{{ "%.2f"|format(trade.profit) }}
                    </span><br>
                    <small>{{ trade.time }}</small>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="card">
            <h3>📝 LOGS EM TEMPO REAL</h3>
            <div class="auto-refresh">
                🔄 Atualização automática a cada 30 segundos
            </div>
            <div class="log-container" id="logContainer">
                {% for log in logs %}
                <div class="log-entry log-{{ log.type }}">[{{ log.time }}] {{ log.message }}</div>
                {% endfor %}
            </div>
            <div class="last-update">
                Última atualização: <span id="lastUpdate">{{ status.current_time }}</span>
            </div>
        </div>
    </div>
    
    <!-- Modal de Confirmação Trading Real -->
    <div id="realTradingModal" class="confirmation-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000;">
        <div class="modal-content" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a2e; padding: 30px; border-radius: 15px; text-align: center; border: 2px solid #ff9900;">
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
        // ✅ FUNÇÕES CORRIGIDAS - SEM ERROS
        function startBot() {
            console.log("🎯 Tentando iniciar bot...");
            const btn = document.getElementById('startBtn');
            if (btn) btn.classList.add('loading');
            
            fetch('/start', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    real_trading: {{ 'true' if status.real_trading else 'false' }} 
                })
            })
            .then(response => {
                console.log("📡 Resposta recebida:", response);
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ Dados recebidos:", data);
                if (data.success) {
                    alert('🤖 Bot iniciado com sucesso!');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    alert('❌ Erro: ' + data.message);
                    if (btn) btn.classList.remove('loading');
                }
            })
            .catch(error => {
                console.error('❌ Erro fetch:', error);
                alert('❌ Erro de conexão. Recarregue a página e tente novamente.');
                if (btn) btn.classList.remove('loading');
            });
        }
        
        function stopBot() {
            console.log("🛑 Tentando parar bot...");
            const btn = document.getElementById('stopBtn');
            if (btn) btn.classList.add('loading');
            
            fetch('/stop', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('🛑 Bot parado!');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    alert('❌ Erro: ' + data.message);
                    if (btn) btn.classList.remove('loading');
                }
            })
            .catch(error => {
                console.error('❌ Erro fetch:', error);
                alert('❌ Erro de conexão.');
                if (btn) btn.classList.remove('loading');
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
        
        // Atualiza logs a cada 30 segundos
        setInterval(() => {
            fetch('/logs')
                .then(response => response.json())
                .then(data => {
                    const logContainer = document.getElementById('logContainer');
                    if (logContainer) {
                        logContainer.innerHTML = data.logs;
                        logContainer.scrollTop = logContainer.scrollHeight;
                    }
                })
                .catch(error => console.log('⚠️ Erro ao atualizar logs:', error));
        }, 30000);
        
        // Atualiza status a cada 30 segundos
        setInterval(() => {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    updateLastUpdateTime();
                })
                .catch(error => console.log('⚠️ Erro ao atualizar status:', error));
        }, 30000);
        
        function updateLastUpdateTime() {
            const now = new Date();
            const element = document.getElementById('lastUpdate');
            if (element) {
                element.textContent = now.toLocaleTimeString() + ' ' + now.toLocaleDateString();
            }
        }
        
        // Controle do checkbox de risco
        document.addEventListener('DOMContentLoaded', function() {
            const checkbox = document.getElementById('riskCheckbox');
            const confirmBtn = document.getElementById('confirmRealBtn');
            
            if (checkbox && confirmBtn) {
                checkbox.addEventListener('change', function() {
                    confirmBtn.disabled = !this.checked;
                });
            }
            
            updateLastUpdateTime();
            console.log('🚀 ULTRABOT PRO - Interface carregada');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal"""
    global trading_bot, real_trading_mode, trade_history
    
    status = {
        'running': trading_bot.is_running if trading_bot else False,
        'analysis_count': trading_bot.analysis_count if trading_bot else 0,
        'trade_count': trading_bot.trade_count if trading_bot else 0,
        'total_profit': f"{trading_bot.total_profit:.2f}" if trading_bot else "0.00",
        'real_trading': real_trading_mode,
        'consecutive_wins': trading_bot.consecutive_wins if trading_bot else 0,
        'consecutive_losses': trading_bot.consecutive_losses if trading_bot else 0,
        'next_analysis': 5,
        'current_time': time.strftime("%H:%M:%S %d/%m/%Y")
    }
    
    return render_template_string(HTML_TEMPLATE, status=status, logs=system_logs[-30:], trades=trade_history[-10:])

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
        
        add_log("🤖 Bot iniciado via interface web", "info")
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
    for log in system_logs[-30:]:
        logs_html += f'<div class="log-entry log-{log["type"]}">[{log["time"]}] {log["message"]}</div>'
    
    return jsonify({'logs': logs_html})

@app.route('/status')
def get_status():
    """Retorna status atual para AJAX"""
    global trading_bot
    status = {
        'running': trading_bot.is_running if trading_bot else False,
        'analysis_count': trading_bot.analysis_count if trading_bot else 0,
        'trade_count': trading_bot.trade_count if trading_bot else 0,
        'total_profit': f"{trading_bot.total_profit:.2f}" if trading_bot else "0.00",
        'consecutive_wins': trading_bot.consecutive_wins if trading_bot else 0,
        'consecutive_losses': trading_bot.consecutive_losses if trading_bot else 0,
    }
    return jsonify(status)

def add_log(message, log_type="info", trade_data=None):
    """Adiciona log ao sistema"""
    global system_logs, trade_history
    
    timestamp = time.strftime("%H:%M:%S")
    log_entry = {
        "time": timestamp,
        "message": message,
        "type": log_type
    }
    
    system_logs.append(log_entry)
    
    # Se for um trade, adiciona ao histórico
    if trade_data and ("TRADE" in message or "SUCESSO" in message or "RESULTADO" in message):
        trade_history.append({
            "time": timestamp,
            "symbol": trade_data.get("symbol", "N/A"),
            "side": trade_data.get("side", "N/A"),
            "profit": trade_data.get("profit", 0),
            "type": "win" if trade_data.get("profit", 0) > 0 else "loss"
        })
    
    # Mantém apenas os últimos 100 logs e 50 trades
    system_logs = system_logs[-100:]
    trade_history = trade_history[-50:]

def start_web_server():
    """Inicia o servidor web"""
    add_log("🌐 ULTRABOT PRO - SISTEMA INICIALIZADO", "info")
    add_log("⚡ MODO PROFISSIONAL ATIVADO", "info")
    add_log("🔄 ATUALIZAÇÃO AUTOMÁTICA: 30s", "info")
    add_log("📊 LOGS COMPLETOS HABILITADOS", "info")
    
    logging.info(f"🌐 Servidor profissional rodando em: http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)

if __name__ == '__main__':
    start_web_server()
