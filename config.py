# config.py - CONFIGURAÇÕES AVANÇADAS COM SUPORTE A VARIÁVEIS DE AMBIENTE
import os
from datetime import datetime

# =============================================================================
# CONFIGURAÇÕES BYBIT API (COM VARIÁVEIS DE AMBIENTE)
# =============================================================================
BYBIT_CONFIG = {
    # 🔐 CREDENCIAIS API (obtidas de variáveis de ambiente)
    "api_key": os.getenv('BYBIT_API_KEY', 'Kdm4ezSuMHltXPVUmV'),  # 👈 Railway vai injetar
    "api_secret": os.getenv('BYBIT_API_SECRET', 'lElWwbpWFyElnxoCo1Py8gpAh0aFuYQhCXPq'),  # 👈 Railway vai injetar
    
    # 🌐 CONFIGURAÇÕES DE REDE
    "testnet": os.getenv('BYBIT_TESTNET', 'true').lower() == 'true',  # Sempre testnet no Railway
    "base_url": "https://api-testnet.bybit.com",
    
    # 📈 CONFIGURAÇÕES DE TRADING
    "symbol": "BTCUSDT",
    "timeframe": "5",
    "category": "linear",
    
    # 💰 CONFIGURAÇÕES DE RISCO E CAPITAL
    "initial_balance": 1000.00,
    "risk_per_trade": 0.02,      # 2% por trade
    "max_position_size": 0.1,    # Tamanho máximo da posição em BTC
    "leverage": 1,               # Alavancagem (1 = sem alavancagem)
}

# =============================================================================
# CONFIGURAÇÕES DO BOT
# =============================================================================
BOT_CONFIG = {
    # ⚙️ CONFIGURAÇÕES GERAIS
    "bot_name": "ULTRABOT PRO MAX",
    "version": "3.0",
    "update_interval": 30,        # Segundos entre análises
    "mode": os.getenv('BOT_MODE', 'BYBIT_TESTNET'),  # Modo do Railway
    
    # 🤖 CONFIGURAÇÕES IA
    "ia_enabled": True,
    "min_confidence": 0.65,       # Confiança mínima para executar trades
    "learning_rate": 0.001,
    
    # 📊 CONFIGURAÇÕES DE ANÁLISE
    "multi_timeframe": True,
    "timeframes": ["1m", "5m", "15m", "1h", "4h"],
    "rsi_period": 14,
    "bb_period": 20,
    "ema_fast": 12,
    "ema_slow": 26,
}

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================
SECURITY_CONFIG = {
    "max_drawdown": 0.10,         # Drawdown máximo permitido (10%)
    "daily_loss_limit": 0.05,     # Limite de perda diária (5%)
    "max_consecutive_losses": 5,  # Máximo de perdas consecutivas
    "auto_stop_loss": True,       # Stop-loss automático
    "emergency_stop": True,       # Parada de emergência
    "volatility_check": True,     # Verificação de volatilidade
    "time_restrictions": True,    # Restrições de horário
}

# =============================================================================
# CONFIGURAÇÕES DE LOG E MONITORAMENTO
# =============================================================================
LOG_CONFIG = {
    "log_level": os.getenv('LOG_LEVEL', 'INFO'),  # Do Railway
    "log_to_file": False,         # No Railway, não salvar em arquivo
    "log_filename": "ultrabot_pro_max.log",
    "max_log_size": 50,           # MB
    "log_colors": False,          # No Railway, sem cores
}

# =============================================================================
# CONFIGURAÇÕES DE ESTRATÉGIA
# =============================================================================
STRATEGY_CONFIG = {
    "use_rsi": True,
    "use_macd": True,
    "use_bollinger": True,
    "use_volume": True,
    "use_support_resistance": True,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "trailing_stop": False,
    "breakout_trading": True,
}

# =============================================================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# =============================================================================
def validate_config():
    """Valida se todas as configurações estão corretas"""
    required_fields = ["api_key", "api_secret"]
    
    for field in required_fields:
        if BYBIT_CONFIG[field].startswith("SUA_") or BYBIT_CONFIG[field].startswith("SEU_"):
            raise ValueError(f"❌ CONFIGURE O CAMPO: {field} - Configure as variáveis BYBIT_API_KEY e BYBIT_API_SECRET no Railway")
    
    # Validar valores de risco
    if BYBIT_CONFIG["risk_per_trade"] > 0.05:
        raise ValueError("❌ RISCO POR TRADE MUITO ALTO! Máximo recomendado: 0.05 (5%)")
    
    if SECURITY_CONFIG["max_drawdown"] > 0.20:
        raise ValueError("❌ DRAWDOWN MÁXIMO MUITO ALTO! Máximo recomendado: 0.20 (20%)")
    
    print("✅ CONFIGURAÇÃO AVANÇADA VALIDADA COM SUCESSO!")
    print(f"🤖 BOT: {BOT_CONFIG['bot_name']} v{BOT_CONFIG['version']}")
    print(f"🌐 MODO: {BOT_CONFIG['mode']}")
    print(f"💰 SALDO INICIAL: ${BYBIT_CONFIG['initial_balance']:.2f}")
    print(f"🎯 RISCO POR TRADE: {BYBIT_CONFIG['risk_per_trade']*100}%")
    print(f"🔐 TESTNET: {BYBIT_CONFIG['testnet']}")
    
    return True

# Testa a configuração quando o arquivo é executado
if __name__ == "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"❌ ERRO NA CONFIGURAÇÃO: {e}")
        print("\n🔧 CONFIGURAÇÃO NO RAILWAY:")
        print("1. Vá em Variables no seu projeto Railway")
        print("2. Adicione BYBIT_API_KEY com sua API Key")
        print("3. Adicione BYBIT_API_SECRET com seu Secret")
        print("4. Adicione BYBIT_TESTNET = true")
        print("5. Adicione BOT_MODE = BYBIT_TESTNET")
