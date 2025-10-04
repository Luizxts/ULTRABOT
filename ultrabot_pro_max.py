# ultrabot_pro_max.py - ROBÔ PRINCIPAL CONTA REAL
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from config import BYBIT_CONFIG, BOT_CONFIG, SECURITY_CONFIG, LOG_CONFIG, validate_config
from bybit_integration import bybit_advanced
from ai_brain_advanced import ai_brain
from risk_manager import risk_manager

class UltraBotProMax:
    """
    Robô de Trading Avançado ULTRABOT PRO MAX - CONTA REAL
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
            self.logger.info("🚀 INICIALIZANDO ULTRABOT PRO MAX - CONTA REAL...")
            
            # Verificação de segurança extra
            self.safety_checks()
            
            # Testar conexão Bybit REAL
            balance_info = self.bybit.get_account_balance_detailed()
            if balance_info:
                self.balance = balance_info['total']['USDT']
                self.logger.info(f"💰 SALDO REAL: ${self.balance:.2f}")
            else:
                self.logger.error("❌ FALHA AO OBTER SALDO REAL")
                raise ConnectionError("Não foi possível conectar à Bybit REAL")
            
            # Status final
            self.logger.info("🎯 ULTRABOT PRO MAX INICIALIZADO - CONTA REAL!")
            self.logger.info(f"⏰ INICIADO EM: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
            self.logger.info("🛡️  MODO CONSERVADOR ATIVO - RISCO 1% POR TRADE")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA INICIALIZAÇÃO: {e}")
            raise

    def safety_checks(self):
        """Verificações de segurança para conta real"""
        self.logger.info("🔒 EXECUTANDO VERIFICAÇÕES DE SEGURANÇA...")
        
        # Verificar se não está em testnet
        if self.config['testnet']:
            self.logger.error("🚨 PERIGO: Configurado para TESTNET mas usando CONTA REAL!")
            raise ValueError("Modo testnet ativo com conta real")
            
        # Verificar credenciais
        if 'SUA_API' in self.config['api_key'] or 'SEU_SECRET' in self.config['api_secret']:
            self.logger.error("🚨 ERRO: Credenciais não configuradas!")
            raise ValueError("Configure BYBIT_API_KEY_REAL e BYBIT_API_SECRET_REAL no Railway")
            
        self.logger.info("✅ VERIFICAÇÕES DE SEGURANÇA: OK")

    def get_market_analysis_advanced(self):
        """Executa análise avançada de mercado"""
        try:
            # Obter dados multi-timeframe
            multi_tf_data = self.bybit.get_multiple_timeframes_data()
            if not multi_tf_data:
                self.logger.warning("⚠️ DADOS DE MERCADO INDISPONÍVEIS")
                return "HOLD", 0.5, "UNKNOWN"
            
            # Análise multi-timeframe com IA
            signal, confidence = self.ai.multi_timeframe_analysis(multi_tf_data)
            
            # Verificar saúde do mercado
            market_health = self.bybit.get_market_health()
            
            self.logger.info(f"🎯 ANÁLISE: {signal} | Conf: {confidence:.1%} | Saúde: {market_health}")
            return signal, confidence, market_health
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA ANÁLISE: {e}")
            return "HOLD", 0.5, "UNKNOWN"

    def execute_advanced_trade(self, signal, confidence, market_health):
        """Executa trade avançado com gerenciamento de risco CONTA REAL"""
        try:
            # Obter condições de mercado para risk manager
            ticker = self.bybit.get_advanced_ticker()
            market_conditions = {
                'spread': ticker['spread'] if ticker else 0.1,
                'volume_health': market_health,
                'volume': ticker['volume'] if ticker else 0
            }
            
            # Calcular tamanho da posição CONSERVADOR
            position_size = self.bybit.calculate_position_size(
                balance=self.balance,
                risk_per_trade=self.config['risk_per_trade'],  # 1%
                stop_loss_pct=0.02  # Stop-loss de 2%
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
            
            # Preparar ordem CONTA REAL
            symbol = f"{self.config['symbol'].replace('USDT', '')}/USDT:USDT"
            current_price = ticker['last']
            
            # Calcular stop loss e take profit CONSERVADORES
            if signal == "BUY":
                stop_loss = current_price * 0.98  # 2% stop loss
                take_profit = current_price * 1.03  # 3% take profit
            else:  # SELL
                stop_loss = current_price * 1.02  # 2% stop loss
                take_profit = current_price * 0.97  # 3% take profit
            
            # Executar ordem REAL
            self.logger.info(f"🎯 EXECUTANDO ORDEM REAL: {signal} {position_size:.6f} {symbol}")
            
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
                
                self.logger.info(f"✅ TRADE REAL EXECUTADO: {signal} | Size: {position_size:.6f}")
                self.logger.info(f"💰 Stop Loss: ${stop_loss:.2f} | Take Profit: ${take_profit:.2f}")
                return True
            else:
                self.logger.error("❌ FALHA NA EXECUÇÃO DA ORDEM REAL")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NA EXECUÇÃO DO TRADE REAL: {e}")
            return False

    def update_trade_metrics(self, signal):
        """Atualiza métricas após trade"""
        if signal == "BUY":
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif signal == "SELL":
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Atualizar saldo REAL
        balance_info = self.bybit.get_account_balance_detailed()
        if balance_info:
            new_balance = balance_info['total']['USDT']
            profit_loss = new_balance - self.balance
            self.total_profit += profit_loss
            self.balance = new_balance
            
            if profit_loss > 0:
                self.logger.info(f"📈 LUCRO: ${profit_loss:.2f}")
            elif profit_loss < 0:
                self.logger.warning(f"📉 PERDA: ${abs(profit_loss):.2f}")

    def run_trading_cycle(self):
        """Executa um ciclo completo de trading CONTA REAL"""
        try:
            self.cycle_count += 1
            self.logger.info(f"🔄 CICLO #{self.cycle_count} - CONTA REAL")
            
            # 1. Análise de Mercado
            signal, confidence, market_health = self.get_market_analysis_advanced()
            
            # 2. Verificar se deve executar trade (critérios mais rigorosos)
            should_trade = (
                signal != "HOLD" and 
                confidence >= self.bot_config['min_confidence'] and
                market_health == "HEALTHY" and
                self.cycle_count > 2  # Esperar alguns ciclos antes do primeiro trade
            )
            
            if should_trade:
                self.logger.info(f"🎯 CONDIÇÕES ATENDIDAS - EXECUTANDO TRADE REAL: {signal}")
                trade_executed = self.execute_advanced_trade(signal, confidence, market_health)
                
                if trade_executed:
                    self.logger.info("✅ TRADE REAL EXECUTADO COM SUCESSO")
                else:
                    self.logger.warning("⚠️ TRADE REAL NÃO EXECUTADO")
            else:
                if signal == "HOLD":
                    self.logger.info("⏭️  Sinal: HOLD - Aguardando oportunidade")
                elif confidence < self.bot_config['min_confidence']:
                    self.logger.info(f"⏭️  Confiança insuficiente: {confidence:.1%} < {self.bot_config['min_confidence']:.1%}")
                elif market_health != "HEALTHY":
                    self.logger.info(f"⏭️  Saúde do mercado: {market_health}")
                elif self.cycle_count <= 2:
                    self.logger.info("⏭️  Aquecimento inicial - Aguardando estabilização")
            
            # 3. Atualizar status e métricas
            self.update_system_status()
            
            self.logger.info(f"✅ CICLO #{self.cycle_count} CONCLUÍDO")
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CICLO DE TRADING: {e}")

    def update_system_status(self):
        """Atualiza e exibe status do sistema CONTA REAL"""
        try:
            # Obter métricas atualizadas
            risk_metrics = self.risk.get_risk_metrics()
            
            # Exibir status
            status_msg = f"""
🤖 ULTRABOT PRO MAX - CONTA REAL

📊 PERFORMANCE REAL:
   ► Ciclos: {self.cycle_count}
   ► Saldo REAL: ${self.balance:.2f}
   ► Lucro/Prejuízo REAL: ${self.total_profit:.2f}
   ► Vitórias Consecutivas: {self.consecutive_wins}
   ► Derrotas Consecutivas: {self.consecutive_losses}

🎯 TRADING:
   ► Trades Hoje: {risk_metrics.get('daily_trades', 0)}
   ► P/L Diário: ${risk_metrics.get('daily_pl', 0):.2f}
   ► Win Rate: {risk_metrics.get('win_rate', 0):.1%}

🛡️  RISCO:
   ► Drawdown: {risk_metrics.get('daily_drawdown', 0):.2%}
   ► Streak Atual: {risk_metrics.get('current_streak', 0)}
   ► Trading Permitido: {risk_metrics.get('trading_allowed', False)}

⏰ PRÓXIMA ANÁLISE: {self.bot_config['update_interval']}s
🕒 {datetime.now().strftime('%H:%M:%S')}
            """
            print(status_msg)
            
        except Exception as e:
            self.logger.error(f"❌ ERRO AO ATUALIZAR STATUS: {e}")

    def check_emergency_conditions(self):
        """Verifica condições de parada de emergência CONTA REAL"""
        try:
            risk_metrics = self.risk.get_risk_metrics()
            
            emergency_conditions = [
                # Drawdown excessivo
                risk_metrics.get('daily_drawdown', 0) > self.security_config['max_drawdown'],
                
                # Muitas perdas consecutivas
                self.consecutive_losses >= self.security_config['max_consecutive_losses'],
                
                # Perda diária excessiva
                risk_metrics.get('daily_pl', 0) < -self.balance * 0.03,  # 3% de perda diária
                
                # Muitos trades em pouco tempo
                risk_metrics.get('daily_trades', 0) > 10,  # Máximo 10 trades/dia
            ]
            
            if any(emergency_conditions):
                self.logger.error("🚨 CONDIÇÕES DE EMERGÊNCIA DETECTADAS - CONTA REAL!")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"❌ ERRO NA VERIFICAÇÃO DE EMERGÊNCIA: {e}")
            return False

    def start(self):
        """Inicia o robô de trading CONTA REAL"""
        try:
            self.running = True
            self.logger.info("🚀 INICIANDO ULTRABOT PRO MAX - CONTA REAL...")
            self.logger.info("🎯 MODO: BYBIT MAINNET - DINHEIRO REAL")
            self.logger.info("🛡️  RISCO: 1% POR TRADE - MODO CONSERVADOR")
            self.logger.info("📊 MONITORAMENTO EM TEMPO REAL ATIVO")
            
            print("\n" + "="*60)
            print("🤖 ULTRABOT PRO MAX - CONTA REAL INICIADO")
            print("💰 OPERANDO COM DINHEIRO REAL - EXTREMO CUIDADO")
            print("🎯 Pressione Ctrl+C para parar imediatamente")
            print("="*60 + "\n")
            
            while self.running:
                try:
                    # Executar ciclo de trading
                    self.run_trading_cycle()
                    
                    # Verificar condições de emergência
                    if self.check_emergency_conditions():
                        self.logger.error("🚨 PARADA DE EMERGÊNCIA ATIVADA - CONTA REAL!")
                        self.stop()
                        break
                    
                    # Intervalo entre ciclos
                    self.logger.info(f"⏳ AGUARDANDO {self.bot_config['update_interval']}s...")
                    time.sleep(self.bot_config['update_interval'])
                    
                except KeyboardInterrupt:
                    self.logger.info("⏹️  INTERRUPÇÃO SOLICITADA PELO USUÁRIO - CONTA REAL")
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
        """Para o robô de trading CONTA REAL"""
        self.running = False
        
        # Estatísticas finais
        runtime = datetime.now() - self.start_time
        risk_metrics = self.risk.get_risk_metrics()
        
        final_report = f"""
🛑 ULTRABOT PRO MAX - RELATÓRIO FINAL CONTA REAL

📈 ESTATÍSTICAS REAIS:
   ► Tempo de Execução: {runtime}
   ► Total de Ciclos: {self.cycle_count}
   ► Saldo Final REAL: ${self.balance:.2f}
   ► Lucro/Prejuízo REAL: ${self.total_profit:.2f}
   ► Trades Realizados: {risk_metrics.get('total_trades', 0)}
   ► Win Rate: {risk_metrics.get('win_rate', 0):.1%}

🎯 PERFORMANCE REAL:
   ► Maior Ganho: ${risk_metrics.get('largest_win', 0):.2f}
   ► Maior Perda: ${risk_metrics.get('largest_loss', 0):.2f}
   ► Streak Máximo (Wins): {risk_metrics.get('max_consecutive_wins', 0)}
   ► Streak Máximo (Losses): {risk_metrics.get('max_consecutive_losses', 0)}

⏰ ENCERRADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💡 RECOMENDAÇÃO:
   ► Analisar performance antes de reiniciar
   ► Verificar logs para possíveis melhorias
   ► Considerar ajustes na estratégia se necessário
        """
        
        print(final_report)
        self.logger.info("🛑 ULTRABOT PRO MAX PARADO - CONTA REAL")

def main():
    """Função principal CONTA REAL"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   ULTRABOT PRO MAX v1.0                      ║
║                                                              ║
║          CONTA REAL - BYBIT MAINNET                          ║
║          OPERANDO COM DINHEIRO REAL                          ║
║          MODO CONSERVADOR - RISCO 1%                         ║
║                                                              ║
║                  [EXTREMO CUIDADO]                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Criar bot e iniciar
        bot = UltraBotProMax()
        bot.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida pelo usuário - CONTA REAL")
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        print("\n🔧 SOLUÇÃO DE PROBLEMAS:")
        print("1. Verifique BYBIT_API_KEY_REAL e BYBIT_API_SECRET_REAL no Railway")
        print("2. Confirme que as permissões da API estão corretas")
        print("3. Verifique se há saldo na conta Bybit")
        print("4. Confirme que não está em modo testnet")

if __name__ == "__main__":
    main()
