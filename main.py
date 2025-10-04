#!/usr/bin/env python3
import time
import logging
import sys
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('UltraBotMain')

try:
    from core.config_manager import config
    from core.state_manager import GlobalState
    from exchanges.bybit_client import BybitClient
    from notifications.telegram_bot import TelegramNotifier
    from risk.risk_manager import AdvancedRiskManager
    from strategies.multi_strategy import MultiStrategyEngine
    
    logger.info("✅ Módulos carregados com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro de importação: {e}")
    sys.exit(1)

class UltraBotProMax:
    def __init__(self):
        logger.info("🚀 INICIANDO ULTRABOT PRO MAX SUPER")
        
        # Inicializar componentes
        self.state = GlobalState()
        self.bybit = BybitClient()
        self.telegram = TelegramNotifier()
        self.risk_manager = AdvancedRiskManager()
        self.strategy_engine = MultiStrategyEngine()
        
        # Estado do bot
        self.ciclo_count = 0
        
        # Inicializar estado
        self.state.update({
            'bot_status': '🟢 INICIANDO',
            'modalidade': 'REAL',
            'conexao_exchange': self.bybit.conectado
        })
        
        logger.info("✅ ULTRABOT INICIALIZADO")
        self.telegram.enviar_status_sistema(
            "INICIADO", 
            self.state.performance,
            self.bybit.conectado
        )
    
    def verificar_saude_sistema(self):
        """Verificar saúde do sistema"""
        try:
            conexao_ativa = self.bybit.verificar_conexao()
            self.state.update({'conexao_exchange': conexao_ativa})
            
            if not conexao_ativa:
                logger.error("❌ SEM CONEXÃO COM EXCHANGE")
                return False
            
            saldo = self.bybit.obter_saldo()
            if saldo > 0:
                self.state.update({'performance.saldo': saldo})
            
            return True
            
        except Exception as e:
            logger.error(f"❌ ERRO NA VERIFICAÇÃO DE SAÚDE: {e}")
            return False
    
    def executar_ciclo_principal(self):
        """Executar ciclo principal"""
        try:
            self.ciclo_count += 1
            logger.info(f"🔄 CICLO #{self.ciclo_count} - INICIANDO")
            
            self.state.update({
                'bot_status': f'🔄 CICLO #{self.ciclo_count}',
                'performance.ciclos': self.ciclo_count
            })
            
            # 1. Verificar saúde
            if not self.verificar_saude_sistema():
                self.state.update({'bot_status': '🔴 PROBLEMAS DE SAÚDE'})
                time.sleep(30)
                return
            
            # 2. Obter dados
            dados_mercado = self.bybit.obter_dados_multitimeframe(
                config.TRADING_CONFIG['pares_monitorados']
            )
            
            if not dados_mercado:
                logger.error("❌ FALHA AO OBTER DADOS")
                return
            
            # 3. Análise
            sinais = self.strategy_engine.analyze_with_all_strategies(dados_mercado)
            
            # 4. Gestão de risco
            saldo_atual = self.bybit.obter_saldo()
            sinais_aprovados = []
            
            for sinal in sinais:
                if self.risk_manager.avaliar_sinal(sinal, saldo_atual):
                    sinais_aprovados.append(sinal)
            
            # 5. Executar trades (SIMULAÇÃO - comentado por segurança)
            if sinais_aprovados:
                logger.info(f"🎯 {len(sinais_aprovados)} TRADES APROVADOS (SIMULAÇÃO)")
                for sinal in sinais_aprovados:
                    self.state.adicionar_sinal(
                        f"TRADE SIMULADO: {sinal['par']} {sinal['direcao']}"
                    )
                    # self.executar_trade_real(sinal)  # DESCOMENTAR PARA TRADING REAL
            else:
                logger.info("⏹️ NENHUM TRADE APROVADO")
                self.state.adicionar_sinal("Análise concluída - Nenhum trade aprovado")
            
            # 6. Atualizar dashboard
            self.state.update({'bot_status': '🟢 OPERACIONAL'})
            logger.info(f"✅ CICLO #{self.ciclo_count} CONCLUÍDO")
            
        except Exception as e:
            logger.error(f"❌ ERRO NO CICLO #{self.ciclo_count}: {e}")
            self.state.update({'bot_status': '🔴 ERRO NO CICLO'})
    
    def executar_trade_real(self, sinal):
        """Executar trade real (MODO REAL)"""
        try:
            logger.info(f"🎯 EXECUTANDO TRADE REAL: {sinal['par']} {sinal['direcao']}")
            
            # Enviar notificação
            self.telegram.enviar_sinal_trading(sinal)
            
            # Executar ordem (DESCOMENTAR PARA TRADING REAL)
            # ordem = self.bybit.executar_ordem(
            #     simbolo=sinal['par'],
            #     lado=sinal['direcao'].lower(),
            #     quantidade=sinal['tamanho_posicao'],
            #     tipo_ordem='market'
            # )
            
            # if ordem and ordem.get('id'):
            #     trade_info = {
            #         'id': ordem['id'],
            #         'par': sinal['par'],
            #         'direcao': sinal['direcao'],
            #         'preco_entrada': sinal['preco'],
            #         'timestamp_abertura': datetime.now().isoformat()
            #     }
            #     
            #     self.risk_manager.registrar_trade_aberto(trade_info)
            #     self.telegram.enviar_execucao_trade(sinal, ordem)
            #     self.state.update({'performance.trades': self.state.performance['trades'] + 1})
            
            # SIMULAÇÃO
            trade_info = {
                'id': f"SIM_{int(time.time())}",
                'par': sinal['par'],
                'direcao': sinal['direcao'],
                'preco_entrada': sinal['preco'],
                'timestamp_abertura': datetime.now().isoformat()
            }
            
            self.risk_manager.registrar_trade_aberto(trade_info)
            self.state.update({'performance.trades': self.state.performance['trades'] + 1})
            self.state.adicionar_sinal(f"TRADE SIM: {sinal['par']} {sinal['direcao']}")
                
        except Exception as e:
            logger.error(f"❌ ERRO NO TRADE {sinal['par']}: {e}")
    
    def run(self):
        """Loop principal"""
        logger.info("🟢 INICIANDO LOOP PRINCIPAL")
        
        while True:
            try:
                self.executar_ciclo_principal()
                time.sleep(config.TRADING_CONFIG['intervalo_analise'])
                
            except KeyboardInterrupt:
                logger.info("⏹️ Parada solicitada")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop: {e}")
                time.sleep(60)

def main():
    """Função principal"""
    try:
        bot = UltraBotProMax()
        bot.run()
    except Exception as e:
        logger.critical(f"💥 ERRO CRÍTICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
