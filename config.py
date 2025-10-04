# config.py - CONFIGURAÇÃO RAILWAY + CONTA REAL
import os

BYBIT_CONFIG = {
    # 🔐 CREDENCIAIS API REAL (Railway Variables)
    "api_key": os.getenv('BYBIT_API_KEY_REAL', 'g9NOzMIa9Ye7lJ6QCI'),
    "api_secret": os.getenv('BYBIT_API_SECRET_REAL', 'c9TdmpaeB0mxSmJQxa00BDevU6eT3Yze48X2'),
    
    # 🌐 CONFIGURAÇÕES DE REDE - CONTA REAL!
    "testnet": False,  # CONTA REAL!
    "base_url": "https://api.bybit.com",
    
    # 📈 CONFIGURAÇÕES DE TRADING
    "symbol": "BTCUSDT",
    "timeframe": "5",
    "category": "linear",
    
    # 💰 CONFIGURAÇÕES DE RISCO - CONSERVADORAS!
    "initial_balance": 500.00,
    "risk_per_trade": 0.01,     # 1% por trade
    "max_position_size": 0.02,  # Máximo 2%
    "leverage": 1,              # Sem alavancagem
}

BOT_CONFIG = {
    "bot_name": "ULTRABOT PRO REAL",
    "version": "1.0", 
    "update_interval": 60,      # 60 segundos
    "mode": "BYBIT_MAINNET",
    
    "ia_enabled": True,
    "min_confidence": 0.70,
}

SECURITY_CONFIG = {
    "max_drawdown": 0.05,
    "daily_loss_limit": 0.03,
    "max_consecutive_losses": 3,
    "auto_stop_loss": True,
    "emergency_stop": True,
}

LOG_CONFIG = {
    "log_level": "INFO",
    "log_to_file": False,       # No Railway, usar logs da plataforma
    "log_colors": False,
}
# config.py - ADICIONAR ESTA FUNÇÃO NO FINAL

def validate_config():
    """Valida se as configurações estão corretas"""
    required_fields = ["api_key", "api_secret"]
    
    for field in required_fields:
        if BYBIT_CONFIG[field].startswith("SUA_") or BYBIT_CONFIG[field].startswith("SEU_"):
            raise ValueError(f"❌ CONFIGURE O CAMPO: {field} - Configure as variáveis no Railway")
    
    # Validar valores de risco
    if BYBIT_CONFIG["risk_per_trade"] > 0.05:
        raise ValueError("❌ RISCO POR TRADE MUITO ALTO! Máximo recomendado: 0.05 (5%)")
    
    if SECURITY_CONFIG["max_drawdown"] > 0.20:
        raise ValueError("❌ DRAWDOWN MÁXIMO MUITO ALTO! Máximo recomendado: 0.20 (20%)")
    
    print("✅ CONFIGURAÇÃO VALIDADA COM SUCESSO!")
    print(f"🤖 BOT: {BOT_CONFIG['bot_name']} v{BOT_CONFIG['version']}")
    print(f"🌐 MODO: {BOT_CONFIG['mode']}")
    print(f"💰 SALDO INICIAL: ${BYBIT_CONFIG['initial_balance']:.2f}")
    print(f"🎯 RISCO POR TRADE: {BYBIT_CONFIG['risk_per_trade']*100}%")
    
    return True

# Testa a configuração quando o arquivo é executado
if __name__ == "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"❌ ERRO NA CONFIGURAÇÃO: {e}")
