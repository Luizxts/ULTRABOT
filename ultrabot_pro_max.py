import time
import logging
import threading
from datetime import datetime
import sys
import os

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from bybit_integration import BybitConnector
    from telegram_bot import TelegramNotifier
    from shared_state import shared_state
    from ai_brain_advanced import AIBrainAdvanced
    from risk_manager import AdvancedRiskManager
    import config
except ImportError as e:
    print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
    print("📁 Diretório atual:", os.path.dirname(os.path.abspath(__file__)))
    print("📁 Arquivos no diretório:", os.listdir(os.path.dirname(os.path.abspath(__file__))))
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ultrabot.log')
    ]
)

logger = logging.getLogger('UltraBotProMax')

class UltraBotProMax:
    def __init__(self):
        logger.info("🚀 INICIANDO ULTRABOT PRO MAX SUPER - MODO REAL")
        
        # Inicializar componentes
        self.bybit = BybitConnector()
        self.telegram = TelegramNotifier()
        self.ai_brain = AIBrainAdvanced()
        self.risk_manager = AdvancedRiskManager()
        
        # Estado do bot
        self.ciclo_count = 0
        self.running = True
        self.modalidade = "REAL"
        
        # Atualizar estado global
        shared_state.atualizar_status("🟢 RODANDO - MODO REAL")
        shared_state.conexao_exchange = self.bybit.conectado
        
        logger.info("✅ ULTRABOT PRO MAX INICIALIZADO - PRONTO PARA TRADING REAL")
    
    def verificar_conexao(self):
        """Verificar conexão com Bybit"""
        try:
            conexao_ativa = self.bybit.verificar_conexao()
            shared_state.conexao_exchange = conexao_ativa
            
            if conexao_ativa:
                logger.info("✅ CONEXÃO BYBIT ATIVA")
                return True
            else:
                logger.warning("⚠️ SEM CONEXÃO COM BYBIT")
                self.telegram.enviar_mensagem("⚠️ BOT OFFLINE - Sem conexão com Bybit")
                return False
                
        except Exception as e:
            logger.error(f"❌ ERRO NA CONEXÃO: {e}")
            shared_state.conexao_exchange = False
            return False
    
    def executar_ciclo_trading(self):
        """Executar um ciclo completo de trading"""
        try:
            self.ciclo_count += 1
            logger.info(f"🔄 CICLO #{self.ciclo_count} - CONTA REAL")
            shared_state.performance['ciclos'] = self.ciclo_count
            
            # 1. Verificar conexão
            if not self.verificar_conexao():
                shared_state.atualizar_status("🔴 OFFLINE - Sem conexão")
                time.sleep(10)
                return
            
            # 2. Obter dados de mercado
            dados_mercado = self.bybit.obter_dados_multitimeframe(config.TRADING_CONFIG['pares_monitorados'])
            if not dados_mercado:
                logger.error("❌ FALHA AO OBTER DADOS DE MERCADO")
                shared_state.atualizar_status("⚠️ SEM DADOS DE MERCADO")
                return
            
            # 3. Análise IA
            sinais = self.ai_brain.analisar_mercado(dados_mercado)
            
            # 4. Gestão de Risco
            trades_aprovados = self.risk_manager.avaliar_sinais(sinais)
            
            # 5. Executar trades (MODO REAL)
            if trades_aprovados:
                self.executar_trades_reais(trades_aprovados)
            else:
                logger.info("⏹️ NENHUM TRADE APROVADO PARA EXECUÇÃO")
                shared_state.adicionar_sinal("Análise concluída - Nenhum trade aprovado")
            
            # 6. Atualizar dashboard
            self.atualizar_dashboard()
            
            shared_state.atualizar_status("🟢 TRADING ATIVO")
            logger.info(f"✅ CICLO #{self.ciclo_count} CONCLUÍDO")
            
        except Exception as e:
            logger.error(f"❌ ERRO NO CICLO {self.ciclo_count}: {e}")
            self.telegram.enviar_mensagem(f"🚨 ERRO NO CICLO {self.ciclo_count}: {str(e)}")
            shared_state.atualizar_status("🔴 ERRO NO CICLO")
    
    def executar_trades_reais(self, trades_aprovados):
        """Executar trades na conta real Bybit"""
        for trade in trades_aprovados:
            try:
                par = trade['par']
                direcao = trade['direcao']  # BUY ou SELL
                confianca = trade['confianca']
                preco = trade['preco']
                
                logger.info(f"🎯 EXECUTANDO TRADE REAL: {par} {direcao} (Conf: {confianca}%)")
                
                # Enviar sinal para Telegram
                self.telegram.enviar_sinal_trading(par, direcao, confianca, preco)
                
                # Executar ordem real
                resultado = self.bybit.executar_ordem(
                    simbolo=par,
                    lado='buy' if direcao == 'BUY' else 'sell',
                    quantidade=config.TRADING_CONFIG['valor_por_trade'],
                    tipo_ordem='market'
                )
                
                if resultado and 'id' in resultado:
                    mensagem = f"✅ TRADE REAL EXECUTADO\nPar: {par}\nDireção: {direcao}\nConfiança: {confianca}%\nID: {resultado['id']}"
                    
                    logger.info(mensagem)
                    self.telegram.enviar_mensagem(mensagem)
                    shared_state.adicionar_sinal(f"TRADE REAL: {par} {direcao} (Conf: {confianca}%)")
                    
                    # Atualizar performance
                    shared_state.performance['trades'] += 1
                    self.risk_manager.registrar_trade(trade)
                    
                else:
                    logger.error(f"❌ FALHA NA EXECUÇÃO DO TRADE: {par}")
                    shared_state.adicionar_sinal(f"FALHA TRADE: {par} {direcao}")
                    
            except Exception as e:
                logger.error(f"❌ ERRO NO TRADE {trade}: {e}")
                self.telegram.enviar_mensagem(f"🚨 ERRO NO TRADE {par}: {str(e)}")
    
    def atualizar_dashboard(self):
        """Atualizar dados do dashboard web"""
        try:
            # Obter saldo atual da conta
            saldo = self.bybit.obter_saldo_conta()
            if saldo:
                shared_state.performance['saldo'] = saldo
            
            # Atualizar última atualização
            shared_state.ultima_atualizacao = datetime.now().strftime("%H:%M:%S")
            
        except Exception as e:
            logger.error(f"❌ ERRO AO ATUALIZAR DASHBOARD: {e}")
    
    def run(self):
        """Loop principal do bot"""
        logger.info("🟢 INICIANDO LOOP PRINCIPAL - MODO REAL")
        self.telegram.enviar_mensagem("🚀 ULTRABOT PRO MAX INICIADO - MODO REAL ATIVO")
        
        while self.running:
            try:
                self.executar_ciclo_trading()
                
                # Aguardar próximo ciclo
                wait_time = config.TRADING_CONFIG['intervalo_analise']
                logger.info(f"⏳ AGUARDANDO {wait_time}s...")
                
                # Contagem regressiva
                for i in range(wait_time, 0, -1):
                    shared_state.atualizar_status(f"🟢 AGUARDANDO {i}s")
                    time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("⏹️ PARANDO BOT VIA KEYBOARD INTERRUPT")
                self.telegram.enviar_mensagem("🛑 ULTRABOT PARADO MANUALMENTE")
                break
            except Exception as e:
                logger.error(f"❌ ERRO NO LOOP PRINCIPAL: {e}")
                time.sleep(30)  # Esperar antes de retry

def main():
    """Função principal"""
    try:
        bot = UltraBotProMax()
        bot.run()
    except Exception as e:
        logger.critical(f"❌ ERRO CRÍTICO: {e}")
        # Tentar notificar via Telegram mesmo em erro crítico
        try:
            telegram = TelegramNotifier()
            telegram.enviar_mensagem(f"🚨 ERRO CRÍTICO NO BOT: {str(e)}")
        except:
            pass

if __name__ == "__main__":
    # Iniciar Flask em thread separada
    try:
        from app import run_flask
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("🌐 FLASK INICIADO EM THREAD SEPARADA")
    except Exception as e:
        logger.error(f"❌ ERRO AO INICIAR FLASK: {e}")
    
    # Iniciar bot principal
    main()
