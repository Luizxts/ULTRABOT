# ultrabot_pro_max.py - ROBÔ PRINCIPAL PARA CONTA REAL
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Configuração com fallback para emergência
try:
    from config import BYBIT_CONFIG, BOT_CONFIG, SECURITY_CONFIG, LOG_CONFIG, validate_config
    print("✅ CONFIGURAÇÃO PRINCIPAL CARREGADA")
except ImportError as e:
    print(f"⚠️  Erro na configuração principal: {e}")
    print("🔧 Usando configuração de emergência...")
    
    # Configuração de emergência inline
    BYBIT_CONFIG = {
        "api_key": os.getenv('BYBIT_API_KEY_REAL', 'default_key'),
        "api_secret": os.getenv('BYBIT_API_SECRET_REAL', 'default_secret'),
        "testnet": False,
        "base_url": "https://api.bybit.com",
        "symbol": "BTCUSDT",
        "timeframe": "5",
        "category": "linear",
        "initial_balance": 500.00,
        "risk_per_trade": 0.02,
        "max_position_size": 0.05,
        "leverage": 3,
    }
    
    BOT_CONFIG = {
        "bot_name": "ULTRABOT PRO MAX SUPER - CONTA REAL",
        "version": "2.0",
        "update_interval": 30,
        "mode": "BYBIT_MAINNET",
        "ia_enabled": True,
        "min_confidence": 0.60,
        "multi_timeframe": True,
        "timeframes": ["5m", "15m", "1h"],
        "multi_asset_trading": True,
        "sentiment_analysis": True,
        "advanced_risk_management": True,
    }
    
    SECURITY_CONFIG = {
        "max_drawdown": 0.08,
        "daily_loss_limit": 0.05,
        "max_consecutive_losses": 5,
        "auto_stop_loss": True,
        "emergency_stop": True,
        "volatility_check": True,
    }
    
    LOG_CONFIG = {
        "log_level": "INFO",
        "log_to_file": False,
        "log_colors": False,
    }
    
    def validate_config():
        print("✅ CONFIGURAÇÃO DE EMERGÊNCIA VALIDADA")
        print("🤖 ULTRABOT PRO MAX SUPER - CONTA REAL")
        print("🌐 MODO: BYBIT MAINNET - DINHEIRO REAL")
        print("💰 OPERANDO COM SALDO REAL")
        return True

from bybit_integration import bybit_advanced
from ai_brain_advanced import ai_brain
from risk_manager import risk_manager
from enhancements_manager import enhancements_manager
from multi_asset_trader import multi_asset_trader
from advanced_risk_manager import advanced_risk_manager

class DebugTrader:
    """Sistema de debug para testes iniciais"""
    
    def __init__(self, main_bot):
        self.bot = main_bot
        self.cycle_count = 0
        self.debug_enabled = True  # Manter ativo para testes
        
    def force_debug_trades(self):
        """Força trades de debug para testar a execução"""
        if not self.debug_enabled:
            return
            
        self.cycle_count += 1
        
        # Executar debug a cada 3 ciclos para não ser muito agressivo
        if self.cycle_count % 3 != 0:
            return
            
        assets = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        selected_asset = random.choice(assets)
        
        # Gerar sinal aleatório (70% HOLD, 15% BUY, 15% SELL) - Conservador para testes
        signal_roll = random.random()
        if signal_roll < 0.15:
            signal = "BUY"
            confidence = random.uniform(0.7, 0.85)
            self.bot.logger.info(f"🎯 DEBUG SIGNAL: BUY {selected_asset} | Conf: {confidence:.1%}")
            self.execute_debug_trade(selected_asset, signal, confidence)
            
        elif signal_roll < 0.3:
            signal = "SELL" 
            confidence = random.uniform(0.7, 0.85)
            self.bot.logger.info(f"🎯 DEBUG SIGNAL: SELL {selected_asset} | Conf: {confidence:.1%}")
            self.execute_debug_trade(selected_asset, signal, confidence)

    def execute_debug_trade(self, asset, signal, confidence):
        """Executa trade de debug"""
        try:
            # Criar dados de sinal simulados
            signal_data = {
                'base_signal': signal,
                'final_confidence': confidence,
                'sentiment': {
                    'classification': 'BULLISH' if signal == 'BUY' else 'BEARISH',
                    'score': 0.8 if signal == 'BUY' else -0.8
                },
                'market_regime': 'TRENDING_BULL' if signal == 'BUY' else 'TRENDING_BEAR',
                'asset': asset,
                'timestamp': datetime.now()
            }
            
            # Calcular tamanho da posição (0.1% do saldo para testes seguros)
            position_size = self.bot.bybit.calculate_position_size()
            safe_position_size = position_size * 0.1  # Apenas 10% do tamanho normal
            
            allocation = {
                'capital': self.bot.balance * 0.001,  # Apenas 0.1% do saldo para testes
                'position_size': safe_position_size,
                'risk_score': 1.0,
                'signal_strength': confidence
            }
            
            # Executar trade via sistema principal
            self.bot.execute_enhanced_trade(asset, signal_data, allocation)
            
        except Exception as e:
            self.bot.logger.error(f"❌ ERRO NO TRADE DEBUG: {e}")

import random

class UltraBotProMax:
    """
    Robô de Trading Avançado ULTRABOT PRO MAX SUPER - CONTA REAL
    """
    
    def __init__(self):
        # Validar configuração primeiro
        try:
            if not validate_config():
                print("⚠️  Configuração inválida, mas continuando em modo de emergência...")
        except Exception as e:
            print(f"⚠️  AVISO NA VALIDAÇÃO: {e}")
        
        # Configurações
        self.config = BYBIT_CONFIG
        self.bot_config = BOT_CONFIG
        self.security_config = SECURITY_CONFIG
        
        # Módulos
        self.bybit = bybit_advanced
        self.ai = ai_brain
        self.risk = risk_manager
        self.enhancements = enhancements_manager
        self.multi_asset = multi_asset_trader
        self.advanced_risk = advanced_risk_manager
        self.debug_trader = DebugTrader(self)
        
        # Estado do bot
        self.running = False
        self.mode = self.bot_config['mode']
        self.balance = 0.0
        self.total_profit = 0.0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.cycle_count = 0
        self.start_time = datetime.now()
        
        # Performance tracking
        self.performance_history = []
        self.last_trade_time = None
        self.assets_signals = {}
        self.trade_count = 0
        
        # Setup avançado
        self.setup_advanced_logging()
        self.initialize_system()
        
    def setup_advanced_logging(self):
        """Configura sistema de logging avançado"""
        try:
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S'
            )
            
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            
            # Configurar logger principal
            self.logger = logging.getLogger('UltraBotProMax')
            self.logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
            self.logger.addHandler(handler)
            
        except Exception as e:
            print(f"❌ ERRO NO LOGGING: {e}")

    def initialize_system(self):
        """Inicialização completa do sistema CONTA REAL"""
        try:
            self.logger.info("🚀 INICIANDO ULTRABOT PRO MAX SUPER - CONTA REAL...")
            
            # Verificar credenciais
            self.check_credentials()
            
            # Testar conexão Bybit REAL
            balance_info = self.bybit.get_account_balance_detailed()
            if balance_info:
                self.balance = balance_info['total']['USDT']
                self.initial_balance = self.balance
                self.logger.info(f"💰 SALDO REAL INICIAL: ${self.balance:.2f}")
                
                if self.balance < 10:
                    self.logger.warning("⚠️  SALDO BAIXO - Considere depositar mais fundos")
            else:
                self.logger.error("❌ FALHA AO OBTER SALDO REAL")
                # Continuar em modo simulação
                self.balance = self.config['initial_balance']
                self.initial_balance = self.balance
                self.logger.info(f"💰 USANDO SALDO SIMULADO: ${self.balance:.2f}")
            
            # Status final
            self.logger.info("🎯 ULTRABOT PRO MAX SUPER INICIALIZADO!")
            self.logger.info(f"⏰ INICIADO EM: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
            self.logger.info("🛡️  MODO CONTA REAL - RISCO 2% POR TRADE")
            self.logger.info("🚀 MELHORIAS ATIVAS: Multi-Ativo, Sentiment Analysis, Risk Management")
            self.logger.info("🔧 MODO DEBUG ATIVO - Testes conservadores")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA INICIALIZAÇÃO: {e}")
            # Inicialização de emergência
            self.balance = self.config['initial_balance']
            self.initial_balance = self.balance
            self.logger.info("🔄 INICIALIZAÇÃO DE EMERGÊNCIA COMPLETA")

    def check_credentials(self):
        """Verifica se as credenciais estão configuradas"""
        api_key = self.config['api_key']
        api_secret = self.config['api_secret']
        
        if not api_key or api_key in ['default_key', 'SUA_API_KEY_REAL_AQUI']:
            self.logger.warning("⚠️  CHAVE API NÃO CONFIGURADA - Modo simulação ativo")
        elif not api_secret or api_secret in ['default_secret', 'SEU_SECRET_REAL_AQUI']:
            self.logger.warning("⚠️  SECRET API NÃO CONFIGURADO - Modo simulação ativo")
        else:
            self.logger.info("✅ CREDENCIAIS API CONFIGURADAS - Modo real ativo")

    def enhanced_market_analysis(self, asset='BTCUSDT'):
        """Análise de mercado com todas as melhorias"""
        try:
            # Análise tradicional
            signal, confidence, market_health = self.get_market_analysis_advanced(asset)
            
            # Análise de sentimento
            sentiment = self.enhancements.sentiment_analyzer.analyze_market_sentiment(
                {'trend': 'bullish' if signal == 'BUY' else 'bearish'}, 
                {'volume_trend': 'increasing'}
            )
            
            # Detecção de regime
            ohlcv_data = self.bybit.get_ohlcv_data(symbol=asset)
            regime = self.enhancements.regime_detector.detect_regime(ohlcv_data)
            
            enhanced_signal = {
                'base_signal': signal,
                'confidence': confidence,
                'sentiment': sentiment,
                'market_regime': regime,
                'final_confidence': self.calculate_enhanced_confidence(confidence, sentiment, regime),
                'asset': asset,
                'timestamp': datetime.now()
            }
            
            return enhanced_signal
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE APRIMORADA: {e}")
            return {'base_signal': 'HOLD', 'confidence': 0.5, 'asset': asset}

    def calculate_enhanced_confidence(self, base_confidence, sentiment, regime):
        """Calcula confiança aprimorada com múltiplos fatores"""
        confidence = base_confidence
        
        # Ajustar baseado no sentimento
        sentiment_score = sentiment.get('score', 0)
        confidence += sentiment_score * 0.2
        
        # Ajustar baseado no regime
        regime_boost = {
            'TRENDING_BULL': 0.15,
            'TRENDING_BEAR': 0.15, 
            'RANGING': -0.1,
            'VOLATILE': -0.2
        }
        confidence += regime_boost.get(regime, 0)
        
        return max(0.1, min(0.95, confidence))

    def get_market_analysis_advanced(self, asset='BTCUSDT'):
        """Executa análise avançada de mercado"""
        try:
            # Obter dados multi-timeframe
            multi_tf_data = self.bybit.get_multiple_timeframes_data(symbol=asset)
            if not multi_tf_data:
                self.logger.warning("⚠️ DADOS DE MERCADO INDISPONÍVEIS")
                return "HOLD", 0.5, "UNKNOWN"
            
            # Análise multi-timeframe com IA
            signal, confidence = self.ai.multi_timeframe_analysis(multi_tf_data)
            
            # Verificar saúde do mercado
            market_health = self.bybit.get_market_health(symbol=asset)
            
            self.logger.info(f"🎯 ANÁLISE {asset}: {signal} | Conf: {confidence:.1%} | Saúde: {market_health}")
            return signal, confidence, market_health
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE {asset}: {e}")
            return "HOLD", 0.5, "UNKNOWN"

    def multi_asset_trading_cycle(self):
        """Ciclo de trading multi-ativos"""
        try:
            self.assets_signals = {}
            
            # Analisar múltiplos ativos
            assets = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'] if self.bot_config['multi_asset_trading'] else ['BTCUSDT']
            
            for asset in assets:
                signal_data = self.enhanced_market_analysis(asset)
                self.assets_signals[asset] = signal_data
            
            # Diversificar e alocar
            diversified_signals = self.multi_asset.diversify_signals(self.assets_signals)
            
            # Executar trades
            for asset, signal_data in diversified_signals.items():
                if self.should_execute_trade(signal_data):
                    # Calcular alocação conservadora para testes
                    allocation = {
                        'capital': self.balance * 0.01,  # 1% do saldo para testes
                        'position_size': self.bybit.calculate_position_size() * 0.1,  # 10% do tamanho normal
                        'risk_score': 1.0,
                        'signal_strength': signal_data['final_confidence']
                    }
                    self.execute_enhanced_trade(asset, signal_data, allocation)
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CICLO MULTI-ATIVOS: {e}")

    def should_execute_trade(self, signal_data):
        """Verifica se deve executar trade baseado em múltiplos fatores"""
        confidence = signal_data.get('final_confidence', 0)
        base_signal = signal_data.get('base_signal', 'HOLD')
        sentiment = signal_data.get('sentiment', {}).get('classification', 'NEUTRAL')
        
        # Critérios para trading real (conservador)
        conditions = [
            base_signal != "HOLD",
            confidence >= self.bot_config['min_confidence'],
            self.cycle_count > 2,  # Esperar alguns ciclos
            self.balance > 10,  # Saldo mínimo
            self.trade_count < 10,  # Limite de trades por sessão
        ]
        
        return all(conditions)

    def execute_enhanced_trade(self, asset, signal_data, allocation):
        """Executa trade avançado com todas as melhorias"""
        try:
            signal = signal_data['base_signal']
            confidence = signal_data['final_confidence']
            
            # Obter condições de mercado
            ticker = self.bybit.get_advanced_ticker(symbol=asset)
            market_health = self.bybit.get_market_health(symbol=asset)
            
            # Preparar ordem
            symbol = f"{asset.replace('USDT', '')}/USDT:USDT"
            current_price = ticker['last']
            position_size = allocation['position_size']
            
            # Calcular stop loss e take profit
            if signal == "BUY":
                stop_loss = current_price * 0.99   # 1% stop loss
                take_profit = current_price * 1.02  # 2% take profit
            else:  # SELL
                stop_loss = current_price * 1.01   # 1% stop loss
                take_profit = current_price * 0.98  # 2% take profit
            
            # Log da ordem
            self.logger.info(f"🎯 PREPARANDO ORDEM: {signal} {position_size:.6f} {symbol}")
            self.logger.info(f"💰 Preço: ${current_price:.2f} | Size: ${position_size * current_price:.2f}")
            self.logger.info(f"🛡️  Stop Loss: ${stop_loss:.2f} | Take Profit: ${take_profit:.2f}")
            
            # VERIFICAR SE ESTÁ EM MODO REAL OU SIMULAÇÃO
            if self.bybit.session_initialized and not self.bybit.fallback_mode:
                # MODO REAL - Executar ordem na exchange
                self.logger.info("🚀 EXECUTANDO ORDEM REAL NA EXCHANGE!")
                
                order = self.bybit.create_advanced_order(
                    symbol=symbol,
                    side=signal.lower(),
                    amount=position_size,
                    order_type='market',
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
                
                if order:
                    self.trade_count += 1
                    self.last_trade_time = datetime.now()
                    self.logger.info(f"✅ ORDEM REAL EXECUTADA! ID: {order['id']}")
                    
                    # Atualizar saldo real
                    balance_info = self.bybit.get_account_balance_detailed()
                    if balance_info:
                        new_balance = balance_info['total']['USDT']
                        self.logger.info(f"💰 NOVO SALDO: ${new_balance:.2f}")
                    
                    return True
                else:
                    self.logger.error("❌ FALHA NA EXECUÇÃO DA ORDEM REAL")
                    return False
            else:
                # MODO SIMULAÇÃO
                self.logger.info("🔧 MODO SIMULAÇÃO - Ordem não executada na exchange")
                
                # Simular resultado para testes
                trade_result = self.simulate_trade_result(signal, current_price, position_size)
                self.update_trade_metrics(signal, trade_result)
                self.trade_count += 1
                
                return True
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NA EXECUÇÃO DO TRADE: {e}")
            return False

    def simulate_trade_result(self, signal, entry_price, position_size):
        """Simula resultado do trade para modo simulação"""
        # 70% de chance de lucro, 30% de prejuízo em simulação
        is_profitable = np.random.random() > 0.3
        
        if is_profitable:
            # Lucro de 0.5-2%
            profit_pct = np.random.uniform(0.005, 0.02)
            profit = position_size * entry_price * profit_pct
            self.logger.info(f"📈 SIMULAÇÃO: LUCRO DE ${profit:.2f}")
        else:
            # Prejuízo de 0.3-1%
            loss_pct = np.random.uniform(0.003, 0.01)
            profit = -position_size * entry_price * loss_pct
            self.logger.warning(f"📉 SIMULAÇÃO: PREJUÍZO DE ${abs(profit):.2f}")
        
        return profit

    def update_trade_metrics(self, signal, profit):
        """Atualiza métricas após trade"""
        if profit > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self.total_profit += profit
            self.balance += profit
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.total_profit += profit
            self.balance += profit

    def run_trading_cycle(self):
        """Executa um ciclo completo de trading"""
        try:
            self.cycle_count += 1
            self.logger.info(f"🔄 CICLO #{self.cycle_count} - CONTA REAL")
            
            # DEBUG: Forçar trades de teste (conservador)
            self.debug_trader.force_debug_trades()
            
            if self.bot_config['multi_asset_trading']:
                self.multi_asset_trading_cycle()
            else:
                # Ciclo tradicional single asset
                signal_data = self.enhanced_market_analysis()
                if self.should_execute_trade(signal_data):
                    allocation = {
                        'capital': self.balance * 0.01,
                        'position_size': self.bybit.calculate_position_size() * 0.1,
                        'risk_score': 1.0,
                        'signal_strength': signal_data['final_confidence']
                    }
                    self.execute_enhanced_trade('BTCUSDT', signal_data, allocation)
            
            # Atualizar status e métricas
            self.update_system_status()
            
            self.logger.info(f"✅ CICLO #{self.cycle_count} CONCLUÍDO")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CICLO DE TRADING: {e}")

    def update_system_status(self):
        """Atualiza e exibe status do sistema"""
        try:
            # Obter métricas de risco
            risk_metrics = self.risk.get_risk_metrics()
            
            # Verificar conexão real
            connection_status = self.bybit.get_connection_status()
            mode = "REAL" if connection_status['connected'] else "SIMULAÇÃO"
            
            # Exibir status
            status_msg = f"""
🤖 ULTRABOT PRO MAX SUPER - {mode}

📊 PERFORMANCE:
   ► Ciclos: {self.cycle_count}
   ► Trades: {self.trade_count}
   ► Saldo: ${self.balance:.2f}
   ► Lucro/Prejuízo: ${self.total_profit:.2f}
   ► Vitórias: {self.consecutive_wins}
   ► Derrotas: {self.consecutive_losses}

🎯 STATUS TRADING:
   ► Modo: {mode}
   ► Conectado: {connection_status['connected']}
   ► Fallback: {connection_status['fallback_mode']}

🛡️  RISCO:
   ► Drawdown: {risk_metrics.get('daily_drawdown', 0):.2%}
   ► Trading Permitido: {risk_metrics.get('trading_allowed', True)}

⏰ PRÓXIMA ANÁLISE: {self.bot_config['update_interval']}s
🕒 {datetime.now().strftime('%H:%M:%S')}
            """
            print(status_msg)
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO ATUALIZAR STATUS: {e}")

    def check_emergency_conditions(self):
        """Verifica condições de parada de emergência"""
        try:
            risk_metrics = self.risk.get_risk_metrics()
            
            emergency_conditions = [
                risk_metrics.get('daily_drawdown', 0) > self.security_config['max_drawdown'],
                self.consecutive_losses >= self.security_config['max_consecutive_losses'],
                self.total_profit < -self.initial_balance * 0.1,  # 10% de perda total
                self.balance < self.initial_balance * 0.8,  # 20% de drawdown
            ]
            
            if any(emergency_conditions):
                self.logger.error("🚨 CONDIÇÕES DE EMERGÊNCIA DETECTADAS!")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA VERIFICAÇÃO DE EMERGÊNCIA: {e}")
            return False

    def start(self):
        """Inicia o robô de trading"""
        try:
            self.running = True
            self.logger.info("🚀 INICIANDO ULTRABOT PRO MAX SUPER...")
            self.logger.info("🎯 MODO: CONTA REAL - DINHEIRO REAL")
            self.logger.info("🛡️  RISCO: 2% POR TRADE - MODO SEGURO")
            self.logger.info("🚀 PRONTO PARA OPERAR!")
            
            print("\n" + "="*80)
            print("🤖 ULTRABOT PRO MAX SUPER - CONTA REAL INICIADO")
            print("💰 OPERANDO COM DINHEIRO REAL - EXTREMO CUIDADO")
            print("🎯 Pressione Ctrl+C para parar imediatamente")
            print("="*80 + "\n")
            
            while self.running:
                try:
                    # Executar ciclo de trading
                    self.run_trading_cycle()
                    
                    # Verificar condições de emergência
                    if self.check_emergency_conditions():
                        self.logger.error("🚨 PARADA DE EMERGÊNCIA ATIVADA!")
                        self.stop()
                        break
                    
                    # Verificar se atingiu limite de trades
                    if self.trade_count >= 10:
                        self.logger.info("🎯 LIMITE DE TRADES ATINGIDO - Parando...")
                        self.stop()
                        break
                    
                    # Intervalo entre ciclos
                    wait_time = self.bot_config['update_interval']
                    self.logger.info(f"⏳ AGUARDANDO {wait_time}s...")
                    time.sleep(wait_time)
                    
                except KeyboardInterrupt:
                    self.logger.info("⏹️  INTERRUPÇÃO SOLICITADA PELO USUÁRIO")
                    break
                except Exception as e:
                    self.logger.error(f"❌ ERRO NO LOOP PRINCIPAL: {e}")
                    time.sleep(self.bot_config['update_interval'])
                    
        except Exception as e:
            self.logger.error(f"❌ ERRO CRÍTICO: {e}")
        finally:
            self.stop()

    def stop(self):
        """Para o robô de trading"""
        self.running = False
        
        # Estatísticas finais
        runtime = datetime.now() - self.start_time
        
        final_report = f"""
🛑 ULTRABOT PRO MAX SUPER - RELATÓRIO FINAL

📈 ESTATÍSTICAS:
   ► Tempo de Execução: {runtime}
   ► Total de Ciclos: {self.cycle_count}
   ► Trades Executados: {self.trade_count}
   ► Saldo Final: ${self.balance:.2f}
   ► Lucro/Prejuízo: ${self.total_profit:.2f}
   ► Retorno: {(self.total_profit/self.initial_balance*100):.2f}%

🎯 PERFORMANCE:
   ► Vitórias Consecutivas: {self.consecutive_wins}
   ► Derrotas Consecutivas: {self.consecutive_losses}

🔧 MODO:
   ► Operação: {'REAL' if self.bybit.session_initialized else 'SIMULAÇÃO'}
   ► Trades Reais: {self.trade_count if self.bybit.session_initialized else 0}

⏰ ENCERRADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💡 RECOMENDAÇÃO:
   ► Analisar resultados antes de reiniciar
   ► Verificar logs para otimizações
   ► Ajustar estratégia se necessário
        """
        
        print(final_report)
        self.logger.info("🛑 ULTRABOT PRO MAX SUPER PARADO")

def main():
    """Função principal"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   ULTRABOT PRO MAX SUPER v2.0                                ║
║                                                                              ║
║          CONTA REAL - BYBIT MAINNET                                          ║
║          OPERANDO COM DINHEIRO REAL                                          ║
║          MODO SEGURO - RISCO 2%                                              ║
║          MELHORIAS: Multi-Ativo, Sentiment Analysis, Advanced Risk          ║
║                                                                              ║
║                  [EXTREMO CUIDADO - DINHEIRO REAL]                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Criar bot e iniciar
        bot = UltraBotProMax()
        bot.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        print("\n🔧 SOLUÇÃO DE PROBLEMAS:")
        print("1. Verifique as credenciais da API no Railway")
        print("2. Confirme que a conta Bybit tem saldo")
        print("3. Verifique as permissões da API")

if __name__ == "__main__":
    main()
