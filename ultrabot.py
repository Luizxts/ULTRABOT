import time
import logging
import requests
import hmac
import hashlib
import json
from datetime import datetime
from config import BYBIT_CONFIG, BOT_CONFIG, SECURITY_CONFIG, validate_config

# =============================================================================
# CLASSE PRINCIPAL ULTRABOT PRO
# =============================================================================
class UltraBotPro:
    def __init__(self):
        # Valida configuração primeiro
        validate_config()
        
        # Configurações
        self.config = BYBIT_CONFIG
        self.bot_config = BOT_CONFIG
        self.security_config = SECURITY_CONFIG
        
        # Estado do bot
        self.running = False
        self.mode = "SIMULAÇÃO BYBIT"
        self.balance = self.config["initial_balance"]
        self.total_profit = 0.0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.ia_active = True
        
        # Setup logging
        self.setup_logging()
        
        # Conectar à Bybit
        self.setup_bybit_connection()
        
        logging.info("🤖 ULTRABOT PRO INICIALIZADO - BYBIT TESTNET")

    def setup_logging(self):
        """Configura sistema de logs"""
        logging.basicConfig(
            level=logging.INFO,
            format='- [%(asctime)s] %(message)s',
            datefmt='%H+%M+%S'
        )

    def setup_bybit_connection(self):
        """Configura conexão com API Bybit"""
        try:
            self.api_key = self.config["api_key"]
            self.api_secret = self.config["api_secret"]
            self.base_url = self.config["base_url"]
            self.symbol = self.config["symbol"]
            
            logging.info("✅ CONEXÃO BYBIT TESTNET CONFIGURADA")
            logging.info(f"📈 PAR: {self.symbol} | TIMEFRAME: {self.config['timeframe']}min")
            
        except Exception as e:
            logging.error(f"❌ ERRO NA CONEXÃO BYBIT: {e}")
            raise

    def generate_signature(self, params):
        """Gera assinatura para requisições Bybit"""
        param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            bytes(self.api_secret, "utf-8"),
            bytes(param_str, "utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    def bybit_request(self, endpoint, method="GET", params=None):
        """Faz requisições para API Bybit"""
        try:
            if params is None:
                params = {}
            
            # Adiciona parâmetros padrão
            params["api_key"] = self.api_key
            params["timestamp"] = str(int(time.time() * 1000))
            params["recv_window"] = "5000"
            
            # Gera assinatura
            params["sign"] = self.generate_signature(params)
            
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, params=params)
            else:
                response = requests.post(url, data=params)
            
            data = response.json()
            
            if data["ret_code"] == 0:
                return data["result"]
            else:
                logging.error(f"❌ ERRO BYBIT: {data['ret_msg']}")
                return None
                
        except Exception as e:
            logging.error(f"❌ ERRO NA REQUISIÇÃO: {e}")
            return None

    def get_account_balance(self):
        """Obtém saldo da conta Bybit"""
        try:
            result = self.bybit_request("/v2/private/wallet/balance", params={"coin": "USDT"})
            if result and "USDT" in result:
                available_balance = float(result["USDT"]["available_balance"])
                self.balance = available_balance
                return available_balance
            return self.balance
        except Exception as e:
            logging.error(f"❌ ERRO AO OBTER SALDO: {e}")
            return self.balance

    def get_market_data(self):
        """Obtém dados de mercado em tempo real"""
        try:
            endpoint = "/v2/public/tickers"
            params = {"symbol": self.symbol}
            
            result = self.bybit_request(endpoint, params=params)
            if result and len(result) > 0:
                ticker = result[0]
                return {
                    "last_price": float(ticker["last_price"]),
                    "bid_price": float(ticker["bid_price"]),
                    "ask_price": float(ticker["ask_price"]),
                    "volume": float(ticker["volume_24h"]),
                    "high": float(ticker["high_price_24h"]),
                    "low": float(ticker["low_price_24h"])
                }
            return None
        except Exception as e:
            logging.error(f"❌ ERRO AO OBTER DADOS DE MERCADO: {e}")
            return None

    def ia_analysis(self, market_data):
        """Análise de IA para decisão de trading"""
        if not self.ia_active:
            return "HOLD"
        
        try:
            # Simulação de análise IA (substituir por modelo real)
            price = market_data["last_price"]
            volume = market_data["volume"]
            
            # Estratégia simples baseada em tendência
            if price > market_data["high"] * 0.98:
                return "BUY"
            elif price < market_data["low"] * 1.02:
                return "SELL"
            else:
                return "HOLD"
                
        except Exception as e:
            logging.error(f"❌ ERRO NA ANÁLISE DA IA: {e}")
            return "HOLD"

    def calculate_position_size(self):
        """Calcula tamanho da posição baseado no risco"""
        risk_amount = self.balance * self.config["risk_per_trade"]
        market_data = self.get_market_data()
        
        if market_data:
            price = market_data["last_price"]
            position_size = risk_amount / price
            max_size = self.config["max_position_size"]
            return min(position_size, max_size)
        
        return 0.001  # Tamanho padrão

    def place_test_order(self, side, signal_type):
        """Simula colocação de ordem (para testes)"""
        try:
            position_size = self.calculate_position_size()
            market_data = self.get_market_data()
            
            if not market_data:
                return False
            
            price = market_data["last_price"]
            order_value = position_size * price
            
            # Simulação de resultado (substituir por ordem real)
            import random
            is_win = random.random() > 0.4  # 60% de win rate para teste
            
            if is_win:
                profit = order_value * 0.015  # 1.5% de lucro
                self.total_profit += profit
                self.consecutive_wins += 1
                self.consecutive_losses = 0
                logging.info(f"✅ ORDEM {side} FECHADA | LUCRO: ${profit:.2f}")
            else:
                loss = order_value * 0.01  # 1% de perda
                self.total_profit -= loss
                self.consecutive_losses += 1
                self.consecutive_wins = 0
                logging.info(f"❌ ORDEM {side} FECHADA | PERDA: ${loss:.2f}")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ ERRO NA ORDEM: {e}")
            return False

    def place_real_order(self, side, signal_type):
        """Coloca ordem real na Bybit (IMPLEMENTAR COM CUIDADO)"""
        try:
            position_size = self.calculate_position_size()
            
            params = {
                "side": side,
                "symbol": self.symbol,
                "order_type": "Market",
                "qty": str(position_size),
                "time_in_force": "GoodTillCancel",
                "reduce_only": False,
                "close_on_trigger": False
            }
            
            result = self.bybit_request("/v2/private/order/create", "POST", params)
            
            if result:
                logging.info(f"✅ ORDEM REAL {side} EXECUTADA | TAMANHO: {position_size}")
                return True
            else:
                logging.error("❌ FALHA NA ORDEM REAL")
                return False
                
        except Exception as e:
            logging.error(f"❌ ERRO NA ORDEM REAL: {e}")
            return False

    def trading_cycle(self):
        """Ciclo principal de trading"""
        try:
            # Obter dados de mercado
            market_data = self.get_market_data()
            if not market_data:
                logging.warning("⚠️ DADOS DE MERCADO INDISPONÍVEIS")
                return

            # Análise IA
            signal = self.ia_analysis(market_data)
            
            # Executar ordem baseada no sinal
            if signal in ["BUY", "SELL"]:
                logging.info(f"🎯 SINAL DA IA: {signal}")
                
                if self.mode == "SIMULAÇÃO BYBIT":
                    self.place_test_order(signal, "IA_SIGNAL")
                else:
                    self.place_real_order(signal, "IA_SIGNAL")
            
            # Atualizar saldo
            self.get_account_balance()
            
            # Log de status
            self.log_status(market_data, signal)
            
        except Exception as e:
            logging.error(f"❌ ERRO NO CICLO DE TRADING: {e}")

    def log_status(self, market_data, signal):
        """Log do status atual do sistema"""
        status_msg = f"""
🤖 ULTRABOT PRO - BYBIT TESTNET

📊 STATUS DO MERCADO:
   Par: {self.symbol} | Preço: ${market_data['last_price']:.2f}
   Volume 24h: {market_data['volume']:.0f}

💼 STATUS DA CONTA:
   Saldo: ${self.balance:.2f} | Lucro Total: ${self.total_profit:.2f}
   Vitórias Consecutivas: {self.consecutive_wins}
   Derrotas Consecutivas: {self.consecutive_losses}

🎯 SINAL ATUAL: {signal}
🔄 PRÓXIMA ANÁLISE: {self.bot_config['update_interval']}s
⏰ ÚLTIMA ATUALIZAÇÃO: {datetime.now().strftime('%H:%M:%S')}
        """
        print(status_msg)

    def start_bot(self):
        """Inicia o bot"""
        try:
            self.running = True
            logging.info("🚀 ULTRABOT PRO INICIADO - BYBIT TESTNET")
            logging.info("📈 MODO: SIMULAÇÃO BYBIT TEMPO REAL")
            logging.info("🤖 IA ATIVADA E APRENDENDO")
            
            cycle_count = 0
            
            while self.running:
                self.trading_cycle()
                cycle_count += 1
                
                # Atualizar a cada X segundos
                time.sleep(self.bot_config["update_interval"])
                
                # Parada de emergência
                if (self.consecutive_losses >= 5 or 
                    self.total_profit < -self.balance * self.security_config["max_drawdown"]):
                    logging.error("🚨 PARADA DE EMERGÊNCIA ATIVADA!")
                    self.stop_bot()
                    break
                    
        except KeyboardInterrupt:
            logging.info("⏹️ BOT INTERROMPIDO PELO USUÁRIO")
        except Exception as e:
            logging.error(f"❌ ERRO NO BOT: {e}")
        finally:
            self.stop_bot()

    def stop_bot(self):
        """Para o bot"""
        self.running = False
        logging.info("🛑 ULTRABOT PRO PARADO")
        logging.info(f"📊 RESUMO FINAL:")
        logging.info(f"   Lucro Total: ${self.total_profit:.2f}")
        logging.info(f"   Saldo Final: ${self.balance:.2f}")

# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════╗
║           ULTRABOT PRO v2.0           ║
║         BYBIT TESTNET MODE            ║
║      TRADING AUTÔNOMO COM IA          ║
╚═══════════════════════════════════════╝
    """)
    
    try:
        bot = UltraBotPro()
        bot.start_bot()
    except Exception as e:
        print(f"❌ ERRO NA INICIALIZAÇÃO: {e}")
