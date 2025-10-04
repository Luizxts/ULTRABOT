# config.py - CONFIGURAÇÃO CONTA REAL RAILWAY
import os

# =============================================================================
# CONFIGURAÇÕES BYBIT API - CONTA REAL
# =============================================================================
BYBIT_CONFIG = {
    # 🔐 CREDENCIAIS API REAL (Railway Variables)
    "api_key": os.getenv('BYBIT_API_KEY_REAL'),
    "api_secret": os.getenv('BYBIT_API_SECRET_REAL'),
    
    # 🌐 CONFIGURAÇÕES DE REDE - CONTA REAL!
    "testnet": False,  # CONTA REAL!
    "base_url": "https://api.bybit.com",
    
    # 📈 CONFIGURAÇÕES DE TRADING
    "symbol": "BTCUSDT",
    "timeframe": "5",
    "category": "linear",
    
    # 💰 CONFIGURAÇÕES DE RISCO - MAIS AGRESSIVAS!
    "initial_balance": 500.00,
    "risk_per_trade": 0.02,     # 2% por trade (ERA 1%)
    "max_position_size": 0.05,  # Máximo 5% do capital (ERA 2%)
    "leverage": 3,              # Alavancagem moderada (ERA 1)
}

# =============================================================================
# CONFIGURAÇÕES DO BOT - MAIS AGRESSIVAS!
# =============================================================================
BOT_CONFIG = {
    # ⚙️ CONFIGURAÇÕES GERAIS
    "bot_name": "ULTRABOT PRO MAX SUPER",
    "version": "2.0",
    "update_interval": 30,      # 30 segundos (ERA 60)
    "mode": "BYBIT_MAINNET",
    
    # 🤖 CONFIGURAÇÕES IA - MENOS CONSERVADOR!
    "ia_enabled": True,
    "min_confidence": 0.60,     # Confiança mínima 60% (ERA 70%)
    
    # 📊 CONFIGURAÇÕES DE ANÁLISE
    "multi_timeframe": True,
    "timeframes": ["5m", "15m", "1h"],
    
    # 🚀 MELHORIAS AVANÇADAS
    "multi_asset_trading": True,
    "sentiment_analysis": True,
    "advanced_risk_management": True,
}

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================
SECURITY_CONFIG = {
    "max_drawdown": 0.08,       # Drawdown máximo 8% (ERA 5%)
    "daily_loss_limit": 0.05,   # Perda diária máxima 5% (ERA 3%)
    "max_consecutive_losses": 5, # Máximo 5 perdas consecutivas (ERA 3)
    "auto_stop_loss": True,
    "emergency_stop": True,
    "volatility_check": True,
}

# =============================================================================
# CONFIGURAÇÕES DE LOG
# =============================================================================
LOG_CONFIG = {
    "log_level": "INFO",
    "log_to_file": False,
    "log_colors": False,
}

# =============================================================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# =============================================================================
def validate_config():
    """Valida se todas as configurações estão corretas"""
    required_env_vars = ['BYBIT_API_KEY_REAL', 'BYBIT_API_SECRET_REAL']
    
    for var in required_env_vars:
        if not os.getenv(var):
            print(f"❌ VARIÁVEL DE AMBIENTE NÃO CONFIGURADA: {var}")
            print("🔧 Configure no Railway:")
            print("1. BYBIT_API_KEY_REAL = sua API key real")
            print("2. BYBIT_API_SECRET_REAL = seu secret real")
            return False
    
    print("✅ CONFIGURAÇÃO AVANÇADA VALIDADA COM SUCESSO!")
    print(f"🤖 BOT: {BOT_CONFIG['bot_name']} v{BOT_CONFIG['version']}")
    print(f"🌐 MODO: {BOT_CONFIG['mode']} - CONTA REAL")
    print(f"💰 SALDO INICIAL: ${BYBIT_CONFIG['initial_balance']:.2f}")
    print(f"🎯 RISCO POR TRADE: {BYBIT_CONFIG['risk_per_trade']*100}%")
    print(f"🛡️  DRAWDOWN MÁXIMO: {SECURITY_CONFIG['max_drawdown']*100}%")
    print("🚀 MELHORIAS: Multi-Ativo, Sentiment Analysis, Risk Management Avançado")
    
    return True

if __name__ == "__main__":
    validate_config()
