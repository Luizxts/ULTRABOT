# ultrabot_pro_max.py - ROBÔ PRINCIPAL ULTRABOT PRO MAX
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from config import BYBIT_CONFIG, BOT_CONFIG, SECURITY_CONFIG, LOG_CONFIG, validate_config
from bybit_integration import bybit_advanced
from ai_brain_advanced import ai_brain
from risk_manager import risk_manager

class UltraBotProMax:
    """
    Robô de Trading Avançado ULTRABOT PRO MAX
    Integra IA, Gerenciamento de Risco e Bybit API
    """
    
    def __init__(self):
        # Validar configuração primeiro
        try:
            validate_config()
        except ValueError as e:
            print(f"❌ ERRO DE CONFIGURAÇÃO: {e}")
            sys.exit(1)
        
        # Configurações
        self.config = BYBIT_CONFIG
        self.bot_config = BOT_CONFIG
        self.security_config = SECURITY_CONFIG
        
        # Módulos
        self.bybit = bybit_advanced
        self.ai = ai_brain
        self.risk = risk_manager
        
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
        
        # Setup avançado
        self.setup_advanced_logging()
        self.initialize_system()
        
    def setup_advanced_logging(self):
        """Configura sistema de logging avançado"""
        try:
            if LOG_CONFIG['log_colors']:
                formatter = logging.Formatter(
                    '\033[94m[%(asctime)s]\033[0m \033[96m%(name)s\033[0m \033[92m%(levelname)s\033[0m %(message)s',
                    datefmt='%H:%M:%S'
                )
            else:
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
            
            # Log para arquivo se configurado
            if LOG_CONFIG['log_to_file']:
                file_handler = logging.FileHandler(LOG_CONFIG['log_filename'])
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"❌ ERRO NO LOGGING: {e}")

    def initialize_system(self):
        """Inicialização completa do sistema"""
        try:
            self.logger.info("🚀 INICIALIZANDO ULTRABOT PRO MAX...")
            
            # Testar conexão Bybit
            balance_info = self.bybit.get_account_balance_detailed()
            if balance_info:
                self.balance = balance_info['total']['USDT']
                self.logger.info(f"💰 SALDO INICIAL: ${self.balance:.2f}")
            else:
                self.logger.error("❌ FALHA AO OBTER SALDO")
                raise ConnectionError("Não foi possível conectar à Bybit")
            
            # Verificar saúde dos módulos
            self.logger.info("🔍 VERIFICANDO MÓDULOS...")
            self.logger.info(f"✅ BYBIT: {'CONECTADO' if self.bybit.exchange else 'ERRO'}")
            self.logger.info(f"✅ IA: {'ATIVA' if self.ai.model_trained else 'TREINAMENTO INICIAL'}")
            self.logger.info(f"✅ RISK MANAGER: {'ATIVO' if self.risk else 'ERRO'}")
            
            # Status final
            self.logger.info("🎯 ULTRABOT PRO MAX INICIALIZADO COM SUCESSO!")
            self.logger.info(f"📊 MODO: {self.mode}")
            self.logger.info(f"⏰ INICIADO EM: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA INICIALIZAÇÃO: {e}")
            raise

    def get_market_analysis_advanced(self):
        """Executa análise avançada de mercado"""
        try:
            self.logger.info("🔍 INICIANDO ANÁLISE DE MERCADO...")
            
            # Obter dados multi-timeframe
            multi_tf_data = self.bybit.get_multiple_timeframes_data()
            if not multi_tf_data:
                self.logger.warning("⚠️ DADOS DE MERCADO INDISPONÍVEIS")
                return "HOLD", 0.5, "UNKNOWN"
            
            # Análise multi-timeframe com IA
            if self.bot_config['multi_timeframe']:
                signal, confidence = self.ai.multi_timeframe_analysis(multi_tf_data)
            else:
                # Análise apenas no timeframe principal
                main_tf_data = multi_tf_data.get('5m')
                if main_tf_data is not None:
                    signal, confidence = self.ai.analyze_market_sentiment(main_tf_data)
                else:
                    signal, confidence = "HOLD", 0.5
            
            # Verificar saúde do mercado
            market_health = self.bybit.get_market_health()
            
            self.logger.info(f"🎯 ANÁLISE CONCLUÍDA: {signal} | Conf: {confidence:.1%} | Saúde: {market_health}")
            return signal, confidence, market_health
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE DE MERCADO: {e}")
            return "HOLD", 0.5, "UNKNOWN"

    def execute_advanced_trade(self, signal, confidence, market_health):
        """Executa trade avançado com gerenciamento de risco"""
        try:
            # Obter condições de mercado para risk manager
            ticker = self.bybit.get_advanced_ticker()
            market_conditions = {
                'spread': ticker['spread'] if ticker else 0.1,
                'volume_health': market_health,
                'volume': ticker['volume'] if ticker else 0
            }
            
            # Calcular tamanho da posição
            position_size = self.bybit.calculate_position_size(
                balance=self.balance,
                risk_per_trade=self.config['risk_per_trade'],
                stop_loss_pct=0.02
            )
            
            # Verificar com risk manager
            can_trade, checks, risk_state = self.risk.can_execute_trade(
                current_balance=self.balance,
                signal_strength=confidence,
                market_conditions=market_conditions,
                trade_size=position_size
            )
            
            if not can_trade:
                self.logger.warning(f"🚫 TRADE BLOQUEADO: {risk_state['reason']}")
                return False
            
            # Preparar ordem
            symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            current_price = ticker['last']
            
            # Calcular stop loss e take profit
            if signal == "BUY":
                stop_loss = current_price * 0.98  # 2% stop loss
                take_profit = current_price * 1.04  # 4% take profit
            else:  # SELL
                stop_loss = current_price * 1.02  # 2% stop loss
                take_profit = current_price * 0.96  # 4% take profit
            
            # Executar ordem
            self.logger.info(f"🎯 EXECUTANDO ORDEM: {signal} {position_size:.6f} {symbol}")
            
            order = self.bybit.create_advanced_order(
                symbol=symbol,
                side=signal.lower(),
                amount=position_size,
                order_type='market',
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if order:
                # Registrar trade
                trade_data = {
                    'signal': signal,
                    'size': position_size,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'confidence': confidence,
                    'balance_before': self.balance,
                    'order_id': order['id'],
                    'market_health': market_health,
                    'risk_checks': checks
                }
                
                self.risk.record_trade(trade_data)
                self.last_trade_time = datetime.now()
                
                # Atualizar métricas
                self.update_trade_metrics(signal)
                
                self.logger.info(f"✅ TRADE EXECUTADO COM SUCESSO: {signal} | Size: {position_size:.6f}")
                return True
            else:
                self.logger.error("❌ FALHA NA EXECUÇÃO DA ORDEM")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NA EXECUÇÃO DO TRADE: {e}")
            return False

    def update_trade_metrics(self, signal):
        """Atualiza métricas após trade"""
        if signal == "BUY":
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif signal == "SELL":
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Atualizar saldo
        balance_info = self.bybit.get_account_balance_detailed()
        if balance_info:
            new_balance = balance_info['total']['USDT']
            self.total_profit = new_balance - self.config['initial_balance']
            self.balance = new_balance

    def run_trading_cycle(self):
        """Executa um ciclo completo de trading"""
        try:
            self.cycle_count += 1
            self.logger.info(f"🔄 INICIANDO CICLO #{self.cycle_count}")
            
            # 1. Análise de Mercado
            signal, confidence, market_health = self.get_market_analysis_advanced()
            
            # 2. Verificar se deve executar trade
            should_trade = (
                signal != "HOLD" and 
                confidence >= self.bot_config['min_confidence'] and
                market_health == "HEALTHY"
            )
            
            if should_trade:
                self.logger.info(f"🎯 CONDIÇÕES ATENDIDAS - EXECUTANDO TRADE: {signal}")
                trade_executed = self.execute_advanced_trade(signal, confidence, market_health)
                
                if trade_executed:
                    self.logger.info("✅ TRADE EXECUTADO COM SUCESSO")
                else:
                    self.logger.warning("⚠️ TRADE NÃO EXECUTADO")
            else:
                self.logger.info("⏭️  NENHUMA OPORTUNIDADE IDENTIFICADA")
                if signal == "HOLD":
                    self.logger.info("   ↳ Sinal: HOLD")
                if confidence < self.bot_config['min_confidence']:
                    self.logger.info(f"   ↳ Confiança insuficiente: {confidence:.1%} < {self.bot_config['min_confidence']:.1%}")
                if market_health != "HEALTHY":
                    self.logger.info(f"   ↳ Saúde do mercado: {market_health}")
            
            # 3. Atualizar status e métricas
            self.update_system_status()
            
            # 4. Log de performance
            self.log_performance_metrics()
            
            self.logger.info(f"✅ CICLO #{self.cycle_count} CONCLUÍDO")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CICLO DE TRADING: {e}")

    def update_system_status(self):
        """Atualiza e exibe status do sistema"""
        try:
            # Obter métricas atualizadas
            risk_metrics = self.risk.get_risk_metrics()
            balance_info = self.bybit.get_account_balance_detailed()
            
            if balance_info:
                self.balance = balance_info['total']['USDT']
            
            # Exibir status
            status_msg = f"""
🤖 ULTRABOT PRO MAX - STATUS DO SISTEMA

📊 PERFORMANCE:
   ► Ciclos: {self.cycle_count}
   ► Saldo: ${self.balance:.2f}
   ► Lucro Total: ${self.total_profit:.2f}
   ► Vitórias Consecutivas: {self.consecutive_wins}
   ► Derrotas Consecutivas: {self.consecutive_losses}

🎯 TRADING:
   ► Trades Hoje: {risk_metrics.get('daily_trades', 0)}
   ► P/L Diário: ${risk_metrics.get('daily_pl', 0):.2f}
   ► Win Rate: {risk_metrics.get('win_rate', 0):.1%}
   ► Trading Permitido: {risk_metrics.get('trading_allowed', False)}

🛡️  RISCO:
   ► Drawdown: {risk_metrics.get('daily_drawdown', 0):.2%}
   ► Streak Atual: {risk_metrics.get('current_streak', 0)}
   ► Status: {risk_metrics.get('risk_reason', 'UNKNOWN')}

⏰ PRÓXIMA ANÁLISE: {self.bot_config['update_interval']}s
🕒 ÚLTIMA ATUALIZAÇÃO: {datetime.now().strftime('%H:%M:%S')}
            """
            print(status_msg)
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO ATUALIZAR STATUS: {e}")

    def log_performance_metrics(self):
        """Registra métricas de performance"""
        try:
            risk_metrics = self.risk.get_risk_metrics()
            
            performance_data = {
                'timestamp': datetime.now(),
                'cycle_count': self.cycle_count,
                'balance': self.balance,
                'total_profit': self.total_profit,
                'consecutive_wins': self.consecutive_wins,
                'consecutive_losses': self.consecutive_losses,
                'daily_trades': risk_metrics.get('daily_trades', 0),
                'daily_pl': risk_metrics.get('daily_pl', 0),
                'win_rate': risk_metrics.get('win_rate', 0),
                'drawdown': risk_metrics.get('daily_drawdown', 0),
            }
            
            self.performance_history.append(performance_data)
            
            # Manter apenas últimas 1000 entradas
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NO LOG DE PERFORMANCE: {e}")

    def check_emergency_conditions(self):
        """Verifica condições de parada de emergência"""
        try:
            risk_metrics = self.risk.get_risk_metrics()
            
            emergency_conditions = [
                # Drawdown excessivo
                risk_metrics.get('daily_drawdown', 0) > self.security_config['max_drawdown'],
                
                # Muitas perdas consecutivas
                self.consecutive_losses >= self.security_config['max_consecutive_losses'],
                
                # Perda diária excessiva
                risk_metrics.get('daily_pl', 0) < -self.balance * 0.08,
                
                # Muitos trades em pouco tempo (overtrading)
                risk_metrics.get('daily_trades', 0) > 50,
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
            self.logger.info("🚀 INICIANDO ULTRABOT PRO MAX...")
            self.logger.info("🎯 MODO: BYBIT TESTNET AVANÇADO")
            self.logger.info("🧠 IA + RISK MANAGEMENT ATIVOS")
            self.logger.info("📊 MONITORAMENTO EM TEMPO REAL")
            
            print("\n" + "="*60)
            print("🤖 ULTRABOT PRO MAX - TRADING AUTÔNOMO INICIADO")
            print("🎯 Pressione Ctrl+C para parar o bot")
            print("="*60 + "\n")
            
            while self.running:
                try:
                    # Executar ciclo de trading
                    self.run_trading_cycle()
                    
                    # Verificar condições de emergência
                    if self.check_emergency_conditions():
                        self.logger.error("🚨 PARADA DE EMERGÊNCIA ATIVADA!")
                        self.stop()
                        break
                    
                    # Intervalo entre ciclos
                    self.logger.info(f"⏳ AGUARDANDO {self.bot_config['update_interval']}s PARA PRÓXIMO CICLO...")
                    time.sleep(self.bot_config['update_interval'])
                    
                except KeyboardInterrupt:
                    self.logger.info("⏹️  INTERRUPÇÃO SOLICITADA PELO USUÁRIO")
                    break
                except Exception as e:
                    self.logger.error(f"❌ ERRO NO LOOP PRINCIPAL: {e}")
                    # Continuar executando mesmo com erro
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
        risk_metrics = self.risk.get_risk_metrics()
        
        final_report = f"""
🛑 ULTRABOT PRO MAX - RELATÓRIO FINAL

📈 ESTATÍSTICAS:
   ► Tempo de Execução: {runtime}
   ► Total de Ciclos: {self.cycle_count}
   ► Saldo Final: ${self.balance:.2f}
   ► Lucro/Prejuízo: ${self.total_profit:.2f}
   ► Trades Realizados: {risk_metrics.get('total_trades', 0)}
   ► Win Rate: {risk_metrics.get('win_rate', 0):.1%}

🎯 PERFORMANCE:
   ► Maior Ganho: ${risk_metrics.get('largest_win', 0):.2f}
   ► Maior Perda: ${risk_metrics.get('largest_loss', 0):.2f}
   ► Streak Máximo (Wins): {risk_metrics.get('max_consecutive_wins', 0)}
   ► Streak Máximo (Losses): {risk_metrics.get('max_consecutive_losses', 0)}

⏰ ENCERRADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        
        print(final_report)
        self.logger.info("🛑 ULTRABOT PRO MAX PARADO")

    def get_performance_report(self):
        """Gera relatório de performance detalhado"""
        try:
            if not self.performance_history:
                return "Nenhum dado de performance disponível"
            
            df = pd.DataFrame(self.performance_history)
            
            report = f"""
📊 RELATÓRIO DE PERFORMANCE DETALHADO

📈 ESTATÍSTICAS GERAIS:
   ► Total de Ciclos: {len(df)}
   ► Saldo Inicial: ${self.config['initial_balance']:.2f}
   ► Saldo Final: ${self.balance:.2f}
   ► Lucro Total: ${self.total_profit:.2f}
   ► ROI: {(self.total_profit / self.config['initial_balance'] * 100):.2f}%

📋 DISTRIBUIÇÃO:
   ► Maior Saldo: ${df['balance'].max():.2f}
   ► Menor Saldo: ${df['balance'].min():.2f}
   ► Média de Saldo: ${df['balance'].mean():.2f}
   
🎯 EFICIÊNCIA:
   ► Ciclos com Lucro: {len(df[df['total_profit'] > 0])}
   ► Ciclos com Prejuízo: {len(df[df['total_profit'] < 0])}
   ► Melhor Streak: {df['consecutive_wins'].max()}
   ► Pior Streak: {df['consecutive_losses'].max()}
            """
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO RELATÓRIO: {e}")
            return f"Erro ao gerar relatório: {e}"

def main():
    """Função principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   ULTRABOT PRO MAX v3.0                      ║
║                                                              ║
║          SISTEMA AVANÇADO DE TRADING AUTÔNOMO                ║
║          IA + RISK MANAGEMENT + BYBIT INTEGRATION            ║
║                                                              ║
║                  [APENAS PARA TESTNET]                       ║
╚══════════════════════════════════════════════════════════════╝
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
        print("1. Verifique suas credenciais Bybit no config.py")
        print("2. Certifique-se de estar usando a TESTNET")
        print("3. Verifique sua conexão com a internet")
        print("4. Execute: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
