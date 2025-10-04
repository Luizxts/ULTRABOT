# ultrabot_pro_max.py - ROBÔ PRINCIPAL SUPER PODEROSO
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
from enhancements_manager import enhancements_manager
from multi_asset_trader import multi_asset_trader
from advanced_risk_manager import advanced_risk_manager

class UltraBotProMax:
    """
    Robô de Trading Avançado ULTRABOT PRO MAX SUPER - CONTA REAL
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
        self.enhancements = enhancements_manager
        self.multi_asset = multi_asset_trader
        self.advanced_risk = advanced_risk_manager
        
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
            self.logger.info("🎯 ULTRABOT PRO MAX SUPER INICIALIZADO - CONTA REAL!")
            self.logger.info(f"⏰ INICIADO EM: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
            self.logger.info("🛡️  MODO CONSERVADOR ATIVO - RISCO 1% POR TRADE")
            self.logger.info("🚀 MELHORIAS ATIVAS: Multi-Ativo, Sentiment Analysis, Risk Management Avançado")
            
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
            
            # Análise de correlação
            correlations = self.enhancements.correlation_analyzer.analyze_correlations(ohlcv_data)
            
            enhanced_signal = {
                'base_signal': signal,
                'confidence': confidence,
                'sentiment': sentiment,
                'market_regime': regime,
                'correlations': correlations,
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
            
            # Aplicar penalidades de correlação
            penalized_signals = self.multi_asset.calculate_correlation_penalties(diversified_signals)
            
            # Calcular alocação de portfólio
            portfolio_allocation = self.multi_asset.calculate_portfolio_allocation(
                self.balance, penalized_signals
            )
            
            # Executar trades
            for asset, allocation in portfolio_allocation.items():
                if allocation['capital'] > self.balance * 0.01:  # Mínimo 1%
                    signal_data = penalized_signals[asset]
                    if self.should_execute_trade(signal_data):
                        self.execute_enhanced_trade(asset, signal_data, allocation)
                
        except Exception as e:
            self.logger.error(f"❌ ERRO NO CICLO MULTI-ATIVOS: {e}")

    def should_execute_trade(self, signal_data):
        """Verifica se deve executar trade baseado em múltiplos fatores"""
        confidence = signal_data.get('final_confidence', 0)
        base_signal = signal_data.get('base_signal', 'HOLD')
        sentiment = signal_data.get('sentiment', {}).get('classification', 'NEUTRAL')
        regime = signal_data.get('market_regime', 'UNKNOWN')
        
        # Critérios rigorosos
        conditions = [
            base_signal != "HOLD",
            confidence >= self.bot_config['min_confidence'],
            self.cycle_count > 2,  # Esperar ciclos iniciais
            sentiment in ['BULLISH', 'BEARISH'],  # Sentimento definido
            regime in ['TRENDING_BULL', 'TRENDING_BEAR']  # Mercado em tendência
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
            
            market_conditions = {
                'spread': ticker['spread'],
                'volume_health': market_health,
                'volume': ticker['volume'],
                'sentiment': signal_data['sentiment'],
                'regime': signal_data['market_regime']
            }
            
            # Calcular tamanho da posição com risk management avançado
            position_size = self.advanced_risk.adaptive_position_sizing(
                market_volatility=ticker['spread'] / 100,  # Estimativa de volatilidade
                account_balance=self.balance,
                win_rate=self.risk.get_risk_metrics().get('win_rate', 0.5)
            )
            
            # Verificar com risk manager avançado
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
            symbol = f"{asset.replace('USDT', '')}/USDT:USDT"
            current_price = ticker['last']
            
            # Calcular stop loss e take profit inteligentes
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
                    'risk_checks': checks,
                    'asset': asset,
                    'enhanced_data': signal_data
                }
                
                self.risk.record_trade(trade_data)
                self.last_trade_time = datetime.now()
                
                # Atualizar métricas
                self.update_trade_metrics(signal)
                
                self.logger.info(f"✅ TRADE REAL EXECUTADO: {signal} {position_size:.6f} {asset}")
                self.logger.info(f"💰 Stop Loss: ${stop_loss:.2f} | Take Profit: ${take_profit:.2f}")
                self.logger.info(f"🎯 Confiança: {confidence:.1%} | Sentimento: {signal_data['sentiment']['classification']}")
                
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
            
            if self.bot_config['multi_asset_trading']:
                self.multi_asset_trading_cycle()
            else:
                # Ciclo tradicional single asset
                signal_data = self.enhanced_market_analysis()
                if self.should_execute_trade(signal_data):
                    allocation = {'capital': self.balance * 0.5}  # 50% para single asset
                    self.execute_enhanced_trade('BTCUSDT', signal_data, allocation)
            
            # Atualizar status e métricas
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
🤖 ULTRABOT PRO MAX SUPER - CONTA REAL

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

🚀 MELHORIAS:
   ► Multi-Ativo: {'✅' if self.bot_config['multi_asset_trading'] else '❌'}
   ► Análise Sentimento: {'✅' if self.bot_config['sentiment_analysis'] else '❌'}
   ► Risk Management Avançado: {'✅' if self.bot_config['advanced_risk_management'] else '❌'}

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
                risk_metrics.get('daily_drawdown', 0) > self.security_config['max_drawdown'],
                self.consecutive_losses >= self.security_config['max_consecutive_losses'],
                risk_metrics.get('daily_pl', 0) < -self.balance * 0.03,
                risk_metrics.get('daily_trades', 0) > 10,
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
            self.logger.info("🚀 INICIANDO ULTRABOT PRO MAX SUPER - CONTA REAL...")
            self.logger.info("🎯 MODO: BYBIT MAINNET - DINHEIRO REAL")
            self.logger.info("🛡️  RISCO: 1% POR TRADE - MODO CONSERVADOR")
            self.logger.info("🚀 MELHORIAS: Multi-Ativo, Sentiment Analysis, Advanced Risk Management")
            self.logger.info("📊 MONITORAMENTO EM TEMPO REAL ATIVO")
            
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
🛑 ULTRABOT PRO MAX SUPER - RELATÓRIO FINAL CONTA REAL

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

🚀 MELHORIAS UTILIZADAS:
   ► Multi-Ativo Trading: {self.bot_config['multi_asset_trading']}
   ► Sentiment Analysis: {self.bot_config['sentiment_analysis']}
   ► Advanced Risk Management: {self.bot_config['advanced_risk_management']}

⏰ ENCERRADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💡 RECOMENDAÇÃO:
   ► Analisar performance antes de reiniciar
   ► Verificar logs para possíveis melhorias
   ► Considerar ajustes na estratégia se necessário
        """
        
        print(final_report)
        self.logger.info("🛑 ULTRABOT PRO MAX SUPER PARADO - CONTA REAL")

def main():
    """Função principal CONTA REAL"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   ULTRABOT PRO MAX SUPER v2.0                                ║
║                                                                              ║
║          CONTA REAL - BYBIT MAINNET                                          ║
║          OPERANDO COM DINHEIRO REAL                                          ║
║          MODO CONSERVADOR - RISCO 1%                                         ║
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
