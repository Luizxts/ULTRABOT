#!/usr/bin/env python3
import time
import logging
import threading
import sys
import os
from datetime import datetime

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging avançado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/ultrabot.log')
    ]
)

logger = logging.getLogger('UltraBotMain')

# Importar módulos principais
try:
    from core.config_manager import config
    from core.state_manager import GlobalState
    from exchanges.bybit_client import BybitClient
    from notifications.telegram_bot import TelegramNotifier
    from risk.risk_manager import AdvancedRiskManager
    from strategies.multi_strategy import MultiStrategyEngine
    from intelligence.evolutionary_ai import EvolutionaryAI
except ImportError as e:
    logger.critical(f"❌ ERRO DE IMPORTAÇÃO: {e}")
    sys.exit(1)

class UltraBotProMax:
    def __init__(self):
        logger.info("🚀 INICIANDO ULTRABOT PRO MAX SUPER - MODO REAL")
        
        # Criar diretórios necessários
        os.makedirs('logs', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        # Inicializar componentes principais
        self.state = GlobalState()
        self.bybit = BybitClient()
        self.telegram = TelegramNotifier()
        self.risk_manager = AdvancedRiskManager()
        self.strategy_engine = MultiStrategyEngine()
        self.evolutionary_ai = EvolutionaryAI()
        
        # Estado do bot
        self.ciclo_count = 0
        self.running = True
        self.erros_consecutivos = 0
        self.max_erros_consecutivos = 5
        
        # Inicializar estado global
        self.state.update({
            'bot_status': '🟢 INICIANDO',
            'modalidade': 'REAL',
            'conexao_exchange': self.bybit.conectado,
            'ultima_atualizacao': datetime.now().strftime('%H:%M:%S')
        })
        
        logger.info("✅ ULTRABOT PRO MAX INICIALIZADO COM SUCESSO")
        self.telegram.enviar_mensagem("🚀 ULTRABOT PRO MAX INICIADO - MODO REAL ATIVO")
    
    def verificar_saude_sistema(self):
        """Verificar saúde completa do sistema"""
        try:
            # Verificar conexão
            conexao_ativa = self.bybit.verificar_conexao()
            self.state.update({'conexao_exchange': conexao_ativa})
            
            if not conexao_ativa:
                logger.error("❌ SEM CONEXÃO COM EXCHANGE")
                self.telegram.enviar_alerta_risco(
                    "CONEXÃO PERDIDA", 
                    "Sem conexão com Bybit - Verificar imediatamente"
                )
                return False
            
            # Verificar saldo
            saldo = self.bybit.obter_saldo()
            if saldo <= 0:
                logger.error("❌ SALDO INSUFICIENTE")
                return False
            
            # Verificar riscos globais
            estatisticas_risco = self.risk_manager.obter_estatisticas_risco()
            if estatisticas_risco['drawdown_atual'] >= config.TRADING_CONFIG['max_drawdown']:
                logger.error("🚨 DRAWDOWN MÁXIMO ATINGIDO")
                self.telegram.enviar_alerta_risco(
                    "DRAWDOWN MÁXIMO", 
                    f"Drawdown atual: {estatisticas_risco['drawdown_atual']:.2f}%"
                )
                return False
            
            self.erros_consecutivos = 0
            return True
            
        except Exception as e:
            self.erros_consecutivos += 1
            logger.error(f"❌ ERRO NA VERIFICAÇÃO DE SAÚDE: {e}")
            
            if self.erros_consecutivos >= self.max_erros_consecutivos:
                logger.critical("🚨 MÁXIMO DE ERROS CONSECUTIVOS - REINICIANDO")
                self.telegram.enviar_erro_critico(e, "Verificação de Saúde")
                time.sleep(60)  # Esperar antes de retry
            
            return False
    
    def executar_ciclo_principal(self):
        """Executar ciclo principal de trading"""
        try:
            self.ciclo_count += 1
            logger.info(f"🔄 CICLO #{self.ciclo_count} - INICIANDO")
            
            # Atualizar estado
            self.state.update({
                'bot_status': f'🔄 CICLO #{self.ciclo_count}',
                'performance.ciclos': self.ciclo_count
            })
            
            # 1. Verificar saúde do sistema
            if not self.verificar_saude_sistema():
                self.state.update({'bot_status': '🔴 PROBLEMAS DE SAÚDE'})
                time.sleep(30)
                return
            
            # 2. Obter dados de mercado
            dados_mercado = self.bybit.obter_dados_multitimeframe(
                config.TRADING_CONFIG['pares_monitorados']
            )
            
            if not dados_mercado:
                logger.error("❌ FALHA AO OBTER DADOS DE MERCADO")
                self.state.update({'bot_status': '⚠️ SEM DADOS'})
                return
            
            # 3. Análise multi-estratégia
            sinais = self.strategy_engine.analyze_with_all_strategies(dados_mercado)
            
            # 4. Gerenciamento de risco
            saldo_atual = self.bybit.obter_saldo()
            sinais_aprovados = []
            
            for sinal in sinais:
                if self.risk_manager.avaliar_sinal(sinal, saldo_atual):
                    sinais_aprovados.append(sinal)
            
            # 5. Executar trades aprovados
            if sinais_aprovados:
                self.executar_trades(sinais_aprovados)
            else:
                logger.info("⏹️ NENHUM TRADE APROVADO NESTE CICLO")
                self.state.adicionar_sinal("Análise concluída - Nenhum trade aprovado")
            
            # 6. Verificar fechamento de trades existentes
            self.verificar_fechamento_trades(dados_mercado)
            
            # 7. Atualizar dashboard e métricas
            self.atualizar_dashboard()
            
            # 8. Log de conclusão
            self.state.update({'bot_status': '🟢 OPERACIONAL'})
            logger.info(f"✅ CICLO #{self.ciclo_count} CONCLUÍDO - {len(sinais_aprovados)} trades")
            
        except Exception as e:
            logger.error(f"❌ ERRO NO CICLO #{self.ciclo_count}: {e}")
            self.telegram.enviar_erro_critico(e, f"Ciclo #{self.ciclo_count}")
            self.state.update({'bot_status': '🔴 ERRO NO CICLO'})
    
    def executar_trades(self, sinais_aprovados):
        """Executar trades aprovados"""
        for sinal in sinais_aprovados:
            try:
                logger.info(f"🎯 EXECUTANDO TRADE: {sinal['par']} {sinal['direcao']}")
                
                # Enviar notificação
                self.telegram.enviar_sinal_trading(sinal)
                
                # Executar ordem
                ordem = self.bybit.executar_ordem(
                    simbolo=sinal['par'],
                    lado=sinal['direcao'].lower(),
                    quantidade=sinal['tamanho_posicao'],
                    tipo_ordem='market'
                )
                
                if ordem and ordem.get('id'):
                    # Registrar trade
                    trade_info = {
                        'id': ordem['id'],
                        'par': sinal['par'],
                        'direcao': sinal['direcao'],
                        'preco_entrada': sinal['preco'],
                        'tamanho_posicao': sinal['tamanho_posicao'],
                        'stop_loss': sinal['stop_loss'],
                        'take_profit': sinal['take_profit'],
                        'timestamp_abertura': datetime.now().isoformat(),
                        'estrategia': sinal.get('estrategia', 'MULTI_STRATEGY')
                    }
                    
                    self.risk_manager.registrar_trade_aberto(trade_info)
                    self.state.adicionar_sinal(
                        f"TRADE: {sinal['par']} {sinal['direcao']} (Conf: {sinal['confianca']:.1f}%)"
                    )
                    
                    # Notificar execução
                    self.telegram.enviar_execucao_trade(sinal, ordem)
                    
                    # Atualizar métricas
                    self.state.update({'performance.trades': self.state.performance['trades'] + 1})
                    
                else:
                    logger.error(f"❌ FALHA NA EXECUÇÃO: {sinal['par']}")
                    self.state.adicionar_sinal(f"FALHA: {sinal['par']} {sinal['direcao']}")
                    
            except Exception as e:
                logger.error(f"❌ ERRO NO TRADE {sinal['par']}: {e}")
                self.telegram.enviar_erro_critico(e, f"Execução Trade {sinal['par']}")
    
    def verificar_fechamento_trades(self, dados_mercado):
        """Verificar e processar fechamento de trades"""
        try:
            # Obter preços atuais
            precos_atuais = {}
            for par in config.TRADING_CONFIG['pares_monitorados']:
                ticker = self.bybit.obter_ticker(par)
                if ticker:
                    precos_atuais[par] = ticker['last']
            
            # Verificar stops globais
            trades_para_fechar = self.risk_manager.verificar_stops_globais(precos_atuais)
            
            for trade_info in trades_para_fechar:
                self.fechar_trade(trade_info)
                
        except Exception as e:
            logger.error(f"❌ ERRO NA VERIFICAÇÃO DE FECHAMENTO: {e}")
    
    def fechar_trade(self, trade_info):
        """Fechar trade específico"""
        try:
            trade = trade_info['trade']
            preco_saida = trade_info['preco_saida']
            motivo = trade_info['motivo']
            
            # Calcular resultado
            if trade['direcao'] == 'BUY':
                lucro_percent = (preco_saida / trade['preco_entrada'] - 1) * 100
            else:  # SELL
                lucro_percent = (trade['preco_entrada'] / preco_saida - 1) * 100
            
            lucro_absoluto = trade['tamanho_posicao'] * (lucro_percent / 100)
            
            resultado = {
                'lucro_percent': lucro_percent,
                'lucro_absoluto': lucro_absoluto,
                'preco_saida': preco_saida,
                'motivo': motivo,
                'timestamp_fechamento': datetime.now().isoformat()
            }
            
            # Registrar fechamento
            self.risk_manager.registrar_trade_fechado(trade, resultado)
            
            # Atualizar IA evolucionária
            if 'estrategia' in trade:
                self.strategy_engine.update_strategy_performance(resultado, trade['estrategia'])
                self.evolutionary_ai.learn_from_trade(trade, resultado)
            
            # Notificar fechamento
            self.telegram.enviar_fechamento_trade(trade, resultado)
            
            # Atualizar métricas
            if lucro_percent > 0:
                self.state.update({'performance.vitorias': self.state.performance['vitorias'] + 1})
            else:
                self.state.update({'performance.derrotas': self.state.performance['derrotas'] + 1})
            
            self.state.update({
                'performance.lucro': self.state.performance['lucro'] + lucro_absoluto
            })
            
            logger.info(f"📊 TRADE FECHADO: {trade['par']} - {lucro_percent:.2f}%")
            
        except Exception as e:
            logger.error(f"❌ ERRO AO FECHAR TRADE: {e}")
    
    def atualizar_dashboard(self):
        """Atualizar dados do dashboard"""
        try:
            # Obter saldo atual
            saldo = self.bybit.obter_saldo()
            if saldo:
                self.state.update({'performance.saldo': saldo})
            
            # Obter estatísticas de risco
            estatisticas = self.risk_manager.obter_estatisticas_risco()
            
            # Obter métricas da IA
            metrics_ia = self.evolutionary_ai.get_performance_metrics()
            metrics_estrategias = self.strategy_engine.get_strategy_metrics()
            
            # Atualizar estado global
            self.state.update({
                'ultima_atualizacao': datetime.now().strftime('%H:%M:%S'),
                'risk_metrics': estatisticas,
                'ai_metrics': metrics_ia,
                'strategy_metrics': metrics_estrategias
            })
            
        except Exception as e:
            logger.error(f"❌ ERRO AO ATUALIZAR DASHBOARD: {e}")
    
    def run(self):
        """Loop principal de execução"""
        logger.info("🟢 INICIANDO LOOP PRINCIPAL DO ULTRABOT")
        
        while self.running:
            try:
                self.executar_ciclo_principal()
                
                # Aguardar próximo ciclo
                wait_time = config.TRADING_CONFIG['intervalo_analise']
                logger.info(f"⏳ AGUARDANDO {wait_time} SEGUNDOS...")
                
                # Contagem regressiva com atualizações de status
                for i in range(wait_time, 0, -1):
                    if not self.running:
                        break
                    self.state.update({'bot_status': f'🟢 PRÓXIMO CICLO EM {i}s'})
                    time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("⏹️ PARADA SOLICITADA VIA KEYBOARD INTERRUPT")
                self.shutdown()
                break
            except Exception as e:
                logger.error(f"❌ ERRO NO LOOP PRINCIPAL: {e}")
                time.sleep(30)  # Backoff em caso de erro
    
    def shutdown(self):
        """Desligamento graceful do bot"""
        logger.info("🛑 INICIANDO DESLIGAMENTO DO ULTRABOT")
        self.running = False
        
        # Enviar status final
        self.telegram.enviar_status_sistema(
            "🛑 PARADO", 
            self.state.performance,
            self.bybit.conectado
        )
        
        logger.info("👋 ULTRABOT PRO MAX FINALIZADO")

def main():
    """Função principal de inicialização"""
    try:
        # Iniciar bot
        bot = UltraBotProMax()
        
        # Registrar handler para graceful shutdown
        import signal
        def signal_handler(sig, frame):
            logger.info("📞 SINAL DE INTERRUPÇÃO RECEBIDO")
            bot.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Executar bot
        bot.run()
        
    except Exception as e:
        logger.critical(f"💥 ERRO CRÍTICO NA INICIALIZAÇÃO: {e}")
        
        # Tentar notificar via Telegram mesmo em erro crítico
        try:
            telegram = TelegramNotifier()
            telegram.enviar_erro_critico(e, "Inicialização do Sistema")
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    # Iniciar aplicação web em thread separada
    try:
        from web.app import run_flask
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("🌐 DASHBOARD WEB INICIADO")
    except Exception as e:
        logger.error(f"❌ ERRO AO INICIAR WEB DASHBOARD: {e}")
    
    # Executar bot principal
    main()
