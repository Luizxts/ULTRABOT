#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
from flask import Flask, render_template_string, jsonify, request
import json
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ultrabot.log')
    ]
)

logger = logging.getLogger(__name__)

class UltraBotApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.bot = None
        self.analyser = None
        self.telegram_available = False
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/')
        def index():
            bot_running = getattr(self.bot, 'running', False) if self.bot else False
            bot_mode = getattr(self.bot, 'mode', 'CONSERVATIVE') if self.bot else 'CONSERVATIVE'
            real_balance = getattr(self.analyser, 'last_balance', 18.34) if self.analyser else 18.34
            
            # Obter estatísticas do bot se estiver rodando
            if self.bot:
                bot_status = self.bot.get_status()
                profit_today = bot_status['profit_today']
                win_rate = bot_status['win_rate']
                trades_today = bot_status['trades_today']
                wins = bot_status['wins_today']
                losses = bot_status['losses_today']
                available_balance = bot_status['available_balance']
                allocated_balance = bot_status['allocated_balance']
                total_balance = bot_status['balance']
                next_trade_in = bot_status['next_trade_in']
                notifications_count = bot_status['notifications_count']
                
                # Obter histórico recente
                recent_trades = self.bot.get_trading_history(5)
                recent_notifications = self.bot.get_notifications()[:5]
            else:
                profit_today = 0.00
                win_rate = 0.0
                trades_today = 0
                wins = 0
                losses = 0
                available_balance = 850.00
                allocated_balance = 150.00
                total_balance = 1000.00
                next_trade_in = "N/A"
                notifications_count = 0
                recent_trades = []
                recent_notifications = []
            
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>ULTRABOT PRO</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 100%);
            color: #fff;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(25, 25, 35, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #00ff88;
            margin: 0;
            font-size: 28px;
        }
        .subtitle {
            color: #888;
            font-size: 14px;
            margin: 5px 0;
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .status {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            text-align: center;
        }
        .status-stopped {
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid #ff4444;
        }
        .balance {
            background: rgba(0, 100, 255, 0.1);
            border: 1px solid #0066ff;
        }
        .profit {
            text-align: center;
            grid-column: 1 / -1;
        }
        .profit-value {
            font-size: 32px;
            font-weight: bold;
            color: #00ff88;
        }
        .profit-negative {
            color: #ff4444;
        }
        .win-rate {
            color: #888;
            font-size: 14px;
        }
        .trades {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .trade-count {
            text-align: center;
        }
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin: 20px 0;
        }
        .button {
            background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
            border: none;
            border-radius: 8px;
            color: #000;
            padding: 12px 20px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
        }
        .button-danger {
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: white;
        }
        .button:disabled {
            background: #666;
            cursor: not-allowed;
        }
        .button-secondary {
            background: linear-gradient(135deg, #666 0%, #444 100%);
            color: white;
        }
        .history-section {
            margin-top: 20px;
        }
        .history-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #00ff88;
        }
        .history-item.loss {
            border-left-color: #ff4444;
        }
        .notification-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #ffc107;
            font-size: 12px;
        }
        .notification-item.success {
            border-left-color: #00ff88;
        }
        .notification-item.error {
            border-left-color: #ff4444;
        }
        .notification-item.info {
            border-left-color: #17a2b8;
        }
        .section-title {
            color: #00ff88;
            margin: 15px 0 10px 0;
            font-size: 16px;
        }
        .alert {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
        }
        .discrepancy-warning {
            background: rgba(255, 87, 87, 0.1);
            border: 1px solid #ff5757;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
            color: #ff5757;
        }
        .success-alert {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
            color: #00ff88;
        }
        .tab-container {
            margin: 20px 0;
        }
        .tabs {
            display: flex;
            margin-bottom: 10px;
        }
        .tab {
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: none;
            color: #fff;
            cursor: pointer;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
        }
        .tab.active {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ULTRABOT PRO</h1>
            <div class="subtitle">Robó de Trading Inteligente - Modo Ganancioso Ativado</div>
        </div>
        
        {% if debug.mode == 'REAL' %}
        <div class="alert">
            ⚠️ <strong>MODO REAL ATIVO</strong><br>
            Operando com dinheiro real!
        </div>
        {% endif %}
        
        {% if debug.show_discrepancy %}
        <div class="discrepancy-warning">
            ⚠️ <strong>DIFERENÇA DE SALDO</strong><br>
            Bybit: ${{ debug.real_balance }} vs Bot: ${{ "%.2f"|format(balance.total) }}
        </div>
        {% endif %}
        
        {% if debug.bot_running %}
        <div class="success-alert">
            ✅ <strong>BOT RODANDO</strong><br>
            Próxima análise em: {{ debug.next_trade_in }} | Notificações: {{ debug.notifications_count }}
        </div>
        {% endif %}
        
        <div class="dashboard">
            <div class="card status {{ 'status-running' if debug.bot_running else 'status-stopped' }}">
                <strong>Status</strong><br>
                {{ '🟢 RODANDO' if debug.bot_running else '🔴 PARADO' }}<br>
                {{ debug.bot_mode }}<br>
                <small>Próximo: {{ debug.next_trade_in }}</small>
            </div>
            
            <div class="card balance">
                <strong>Saldo ${{ "%.2f"|format(balance.total) }}</strong><br>
                Disponível: ${{ "%.2f"|format(balance.available) }}<br>
                Alocado: ${{ "%.2f"|format(balance.allocated) }}
            </div>
            
            <div class="card profit">
                <div class="profit-value {{ 'profit-negative' if profit.today < 0 }}">
                    ${{ "%.2f"|format(profit.today) }}
                </div>
                <div class="win-rate">Lucro Hoje</div>
                <div class="win-rate">Win Rate: {{ "%.1f"|format(profit.win_rate) }}%</div>
            </div>
        </div>
        
        <div class="trades">
            <div class="trade-count">
                <strong>{{ trades.total }}</strong><br>
                Trades Hoje
            </div>
            <div class="trade-count">
                <strong>{{ trades.win_loss }}</strong><br>
                Vitórias / Derrotas
            </div>
            <div class="trade-count">
                <strong>{{ "%.1f"|format(profit.win_rate) }}%</strong><br>
                Win Rate
            </div>
        </div>

        <div class="controls">
            <button class="button" onclick="startBot()" {{ 'disabled' if debug.bot_running }}>▶️ INICIAR BOT</button>
            <button class="button button-danger" onclick="stopBot()" {{ 'disabled' if not debug.bot_running }}>⏹️ PARAR BOT</button>
            <button class="button button-secondary" onclick="refreshData()">🔄 ATUALIZAR</button>
            <button class="button button-secondary" onclick="resetStats()">📊 RESETAR ESTATÍSTICAS</button>
        </div>

        <div class="tab-container">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('notifications')">🔔 Notificações ({{ debug.notifications_count }})</button>
                <button class="tab" onclick="switchTab('history')">📈 Histórico</button>
                <button class="tab" onclick="switchTab('stats')">📊 Estatísticas</button>
            </div>
            
            <div id="notifications-tab" class="tab-content active">
                <div class="section-title">ÚLTIMAS NOTIFICAÇÕES</div>
                {% for notif in notifications %}
                <div class="notification-item {{ notif.level }}">
                    <strong>{{ notif.timestamp[11:16] }}</strong> - {{ notif.message }}
                </div>
                {% else %}
                <div class="notification-item info">
                    Nenhuma notificação recente
                </div>
                {% endfor %}
            </div>
            
            <div id="history-tab" class="tab-content">
                <div class="section-title">ÚLTIMOS TRADES</div>
                {% for trade in history %}
                <div class="history-item {{ 'loss' if trade.type == 'LOSS' else '' }}">
                    <strong>{{ trade.timestamp[11:16] }}</strong> - 
                    {{ '✅ WIN' if trade.type == 'WIN' else '❌ LOSS' }} - 
                    ${{ "%.2f"|format(trade.profit_loss) }} - 
                    Valor: ${{ "%.2f"|format(trade.amount) }}
                </div>
                {% else %}
                <div class="history-item">
                    Nenhum trade registrado ainda
                </div>
                {% endfor %}
            </div>
            
            <div id="stats-tab" class="tab-content">
                <div class="section-title">ESTATÍSTICAS DO DIA</div>
                <div class="card">
                    <strong>Data:</strong> {{ debug.timestamp }}<br>
                    <strong>Trades Realizados:</strong> {{ trades.total }}<br>
                    <strong>Vitórias:</strong> {{ trades.wins }}<br>
                    <strong>Derrotas:</strong> {{ trades.losses }}<br>
                    <strong>Win Rate:</strong> {{ "%.1f"|format(profit.win_rate) }}%<br>
                    <strong>Lucro Total:</strong> ${{ "%.2f"|format(profit.today) }}<br>
                    <strong>Saldo Atual:</strong> ${{ "%.2f"|format(balance.total) }}
                </div>
            </div>
        </div>
    </div>

    <script>
        function startBot() {
            fetch('/api/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('✅ ' + data.message, 'success');
                        setTimeout(() => location.reload(), 1500);
                    } else {
                        showAlert('❌ ' + (data.error || 'Erro ao iniciar bot'), 'error');
                    }
                })
                .catch(error => {
                    showAlert('❌ Erro de conexão: ' + error, 'error');
                });
        }

        function stopBot() {
            fetch('/api/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('✅ ' + data.message, 'success');
                        setTimeout(() => location.reload(), 1500);
                    } else {
                        showAlert('❌ ' + (data.error || 'Erro ao parar bot'), 'error');
                    }
                })
                .catch(error => {
                    showAlert('❌ Erro de conexão: ' + error, 'error');
                });
        }

        function refreshData() {
            location.reload();
        }

        function resetStats() {
            if (confirm('Tem certeza que deseja resetar as estatísticas do dia?')) {
                fetch('/api/reset_stats', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showAlert('✅ ' + data.message, 'success');
                            setTimeout(() => location.reload(), 1500);
                        } else {
                            showAlert('❌ ' + (data.error || 'Erro ao resetar estatísticas'), 'error');
                        }
                    })
                    .catch(error => {
                        showAlert('❌ Erro de conexão: ' + error, 'error');
                    });
            }
        }

        function switchTab(tabName) {
            // Esconde todas as tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Mostra a tab selecionada
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }

        function showAlert(message, type) {
            const alert = document.createElement('div');
            alert.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                z-index: 1000;
                font-weight: bold;
                background: ${type === 'success' ? '#00ff88' : '#ff4444'};
                color: ${type === 'success' ? '#000' : '#fff'};
            `;
            alert.textContent = message;
            document.body.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 3000);
        }

        // Auto-refresh a cada 30 segundos se o bot estiver rodando
        {% if debug.bot_running %}
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    if (data.bot_status && data.bot_status.trades_today > {{ trades.total }}) {
                        location.reload();
                    }
                });
        }, 30000);
        {% endif %}
    </script>
</body>
</html>
            ''', 
            balance={
                'total': total_balance, 
                'available': available_balance, 
                'allocated': allocated_balance
            },
            profit={'today': profit_today, 'win_rate': win_rate},
            trades={
                'total': trades_today, 
                'win_loss': f'{wins} / {losses}',
                'wins': wins,
                'losses': losses
            },
            history=recent_trades,
            notifications=recent_notifications,
            debug={
                'mode': 'SIMULADO',
                'bot_running': bot_running,
                'bot_mode': bot_mode,
                'telegram_status': 'ATIVO' if self.telegram_available else 'NÃO DISPONÍVEL',
                'real_balance': "%.2f" % real_balance,
                'total_trades': trades_today,
                'show_discrepancy': abs(real_balance - total_balance) > 1.0,
                'next_trade_in': next_trade_in,
                'notifications_count': notifications_count,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
        
        @self.app.route('/api/balance')
        def api_balance():
            """Endpoint para verificar saldo real"""
            try:
                if self.analyser is None:
                    from trader.bybit_analyser import BybitAnalyser
                    self.analyser = BybitAnalyser()
                
                async def get_balance_async():
                    return await self.analyser.get_balance()
                
                bybit_balance = asyncio.run(get_balance_async())
                bot_balance = 1000.00
                
                return jsonify({
                    'bybit_balance': bybit_balance,
                    'bot_balance': bot_balance,
                    'discrepancy': abs(bybit_balance - bot_balance),
                    'sync_ok': abs(bybit_balance - bot_balance) < 1.0
                })
            except Exception as e:
                logger.error(f"Erro ao verificar saldo: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/status')
        def api_status():
            """Endpoint para status do sistema"""
            bot_status = self.bot.get_status() if self.bot else {}
            return jsonify({
                'bot_running': getattr(self.bot, 'running', False) if self.bot else False,
                'telegram_available': self.telegram_available,
                'mode': 'SIMULATION',
                'bot_status': bot_status,
                'status': 'OPERATIONAL'
            })
        
        @self.app.route('/api/history')
        def api_history():
            """Endpoint para histórico de trades"""
            try:
                if self.bot is None:
                    return jsonify({'history': [], 'total': 0})
                
                history = self.bot.get_trading_history(50)
                return jsonify({
                    'history': history,
                    'total': len(history)
                })
            except Exception as e:
                logger.error(f"Erro ao obter histórico: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/notifications')
        def api_notifications():
            """Endpoint para notificações"""
            try:
                if self.bot is None:
                    return jsonify({'notifications': [], 'unread': 0})
                
                notifications = self.bot.get_notifications()
                unread_count = len([n for n in notifications if not n['read']])
                
                return jsonify({
                    'notifications': notifications[:20],
                    'unread': unread_count,
                    'total': len(notifications)
                })
            except Exception as e:
                logger.error(f"Erro ao obter notificações: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/start', methods=['POST'])
        def api_start():
            """Inicia o bot de trading"""
            try:
                if self.bot is None:
                    from trader.core import UltraBot
                    self.bot = UltraBot()
                
                if self.bot.running:
                    return jsonify({'success': False, 'error': 'Bot já está rodando'})
                
                # Inicializar analisador se necessário
                if self.analyser is None:
                    from trader.bybit_analyser import BybitAnalyser
                    self.analyser = BybitAnalyser()
                
                # Inicializar Telegram se necessário
                if not self.telegram_available:
                    try:
                        asyncio.run(self.initialize_telegram())
                    except Exception as e:
                        logger.warning(f"Telegram não disponível: {e}")
                
                # Iniciar bot
                try:
                    success = asyncio.run(self.bot.start())
                except Exception as e:
                    logger.error(f"Erro ao iniciar bot: {e}")
                    return jsonify({'success': False, 'error': f'Falha ao iniciar: {str(e)}'}), 500
                
                if success:
                    logger.info("🚀 Bot iniciado via API")
                    
                    # Notificação Telegram (opcional)
                    if self.telegram_available:
                        try:
                            from telegram_bot.bot import TelegramBot
                            telegram_bot = TelegramBot()
                            
                            async def send_msg():
                                await telegram_bot.send_message(
                                    "-4977542145", 
                                    "🚀 *ULTRABOT INICIADO*\nModo: SIMULATION\nSaldo: $1000.00\nIntervalo: 10 minutos"
                                )
                            
                            asyncio.run(send_msg())
                        except Exception as e:
                            logger.warning(f"⚠️ Não foi possível enviar mensagem Telegram: {e}")
                    
                    return jsonify({'success': True, 'message': 'Bot iniciado com sucesso!'})
                else:
                    return jsonify({'success': False, 'error': 'Falha ao iniciar bot'})
                
            except Exception as e:
                logger.error(f"Erro ao iniciar bot: {e}")
                return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500
        
        @self.app.route('/api/stop', methods=['POST'])
        def api_stop():
            """Para o bot de trading"""
            try:
                if self.bot is None:
                    return jsonify({'success': False, 'error': 'Bot não está inicializado'})
                
                if not self.bot.running:
                    return jsonify({'success': False, 'error': 'Bot não está rodando'})
                
                # Parar o bot de forma segura
                self.bot.running = False
                
                # Obter estatísticas antes de parar
                bot_status = self.bot.get_status()
                
                # Criar mensagem de parada
                stop_msg = f"⏹️ ULTRABOT PARADO | Trades: {bot_status['trades_today']} | Lucro: ${bot_status['profit_today']:.2f}"
                logger.info(stop_msg)
                
                # Adicionar notificação
                self.bot.add_notification(stop_msg, "info")
                
                # Salvar histórico se existir o método
                if hasattr(self.bot, 'save_history') and callable(getattr(self.bot, 'save_history')):
                    self.bot.save_history()
                
                logger.info("⏹️ Bot parado via API")
                
                # Enviar notificação Telegram (opcional)
                if self.telegram_available:
                    try:
                        from telegram_bot.bot import TelegramBot
                        telegram_bot = TelegramBot()
                        
                        message = (
                            f"⏹️ *ULTRABOT PARADO*\n"
                            f"Trades hoje: {bot_status['trades_today']}\n"
                            f"W/L: {bot_status['wins_today']}/{bot_status['losses_today']}\n"
                            f"Lucro: ${bot_status['profit_today']:.2f}\n"
                            f"Win Rate: {bot_status['win_rate']}%"
                        )
                        
                        # Executar de forma assíncrona
                        async def send_msg():
                            await telegram_bot.send_message("-4977542145", message)
                        
                        asyncio.run(send_msg())
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Não foi possível enviar mensagem Telegram: {e}")
                
                return jsonify({
                    'success': True, 
                    'message': 'Bot parado com sucesso!',
                    'stats': {
                        'trades': bot_status['trades_today'],
                        'profit': bot_status['profit_today'],
                        'win_rate': bot_status['win_rate']
                    }
                })
                
            except Exception as e:
                logger.error(f"Erro ao parar bot: {e}")
                return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500
        
        @self.app.route('/api/reset_stats', methods=['POST'])
        def api_reset_stats():
            """Reseta estatísticas do dia"""
            try:
                if self.bot is None:
                    return jsonify({'success': False, 'error': 'Bot não inicializado'})
                
                self.bot.reset_daily_stats()
                logger.info("📊 Estatísticas resetadas via API")
                
                return jsonify({'success': True, 'message': 'Estatísticas resetadas com sucesso!'})
                
            except Exception as e:
                logger.error(f"Erro ao resetar estatísticas: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            bot_status = self.bot.get_status() if self.bot else {}
            return jsonify({
                'status': 'healthy', 
                'service': 'ultrabot_pro',
                'bot_running': bot_status.get('running', False),
                'trades_today': bot_status.get('trades_today', 0)
            })

    async def initialize(self):
        """Inicializa a aplicação"""
        try:
            from trader.bybit_analyser import BybitAnalyser
            self.analyser = BybitAnalyser()
            
            real_balance = await self.analyser.get_balance()
            logger.info(f"💰 Saldo real na Bybit: ${real_balance:.2f}")
            
            from trader.core import UltraBot
            self.bot = UltraBot()
            logger.info("🤖 ULTRABOT inicializado - Modo Ganancioso Ativado!")
            
            await self.initialize_telegram()
            
            await self.run_verification()
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            raise

    async def initialize_telegram(self):
        """Inicializa o bot do Telegram"""
        try:
            from telegram_bot.bot import TelegramBot
            telegram_bot = TelegramBot()
            success = await telegram_bot.initialize()
            self.telegram_available = success
            if success:
                logger.info("📱 Telegram bot inicializado com sucesso!")
            else:
                logger.warning("⚠️ Telegram bot não pôde ser inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Telegram não disponível: {e}")
            self.telegram_available = False

    async def run_verification(self):
        """Executa verificação de consistência"""
        try:
            if self.analyser:
                real_balance = await self.analyser.get_balance()
                bot_balance = 1000.00
                
                discrepancy = abs(real_balance - bot_balance)
                if discrepancy > 1.0:
                    logger.error(f"🔴 DISCREPÂNCIA DE SALDO: Bybit=${real_balance:.2f} vs Bot=${bot_balance:.2f} (Dif: ${discrepancy:.2f})")
                else:
                    logger.info(f"✅ Saldos sincronizados: ${real_balance:.2f}")
                    
        except Exception as e:
            logger.error(f"❌ Erro na verificação: {e}")

def main():
    """Função principal"""
    try:
        ultrabot_app = UltraBotApp()
        
        asyncio.run(ultrabot_app.initialize())
        
        logger.info("🚀 Iniciando servidor ULTRABOT PRO...")
        
        from waitress import serve
        
        try:
            from config import HOST, PORT
        except ImportError:
            HOST = "0.0.0.0"
            PORT = 5000

        logger.info(f"🌐 Servidor rodando em: http://{HOST}:{PORT}")
        logger.info("⚠️  Usando Waitress (Produção)")
        
        serve(ultrabot_app.app, host=HOST, port=PORT)
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
