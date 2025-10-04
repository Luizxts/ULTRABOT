# config.py - CONFIGURAÇÃO CONTA REAL RAILWAY
import os

# =============================================================================
# CONFIGURAÇÕES BYBIT API - CONTA REAL
# =============================================================================
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
    "initial_balance": 500.00,  # Comece com $500
    "risk_per_trade": 0.01,     # 1% por trade
    "max_position_size": 0.02,  # Máximo 2% do capital
    "leverage": 1,              # SEM ALAVANCAGEM
}

# =============================================================================
# CONFIGURAÇÕES DO BOT
# =============================================================================
BOT_CONFIG = {
    # ⚙️ CONFIGURAÇÕES GERAIS
    "bot_name": "ULTRABOT PRO MAX SUPER",
    "version": "2.0",
    "update_interval": 60,      # 60 segundos (conservador)
    "mode": "BYBIT_MAINNET",    # MODO REAL
    
    # 🤖 CONFIGURAÇÕES IA
    "ia_enabled": True,
    "min_confidence": 0.70,     # Confiança mínima 70%
    
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
    "max_drawdown": 0.05,       # Drawdown máximo 5%
    "daily_loss_limit": 0.03,   # Perda diária máxima 3%
    "max_consecutive_losses": 3, # Máximo 3 perdas consecutivas
    "auto_stop_loss": True,     # Stop-loss automático
    "emergency_stop": True,     # Parada de emergência
    "volatility_check": True,   # Verificação de volatilidade
}

# =============================================================================
# CONFIGURAÇÕES DE LOG
# =============================================================================
LOG_CONFIG = {
    "log_level": "INFO",        # DEBUG, INFO, WARNING, ERROR
    "log_to_file": False,       # No Railway, usar logs da plataforma
    "log_colors": False,        # No Railway, sem cores
}

# =============================================================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# =============================================================================
def validate_config():
    """Valida se todas as configurações estão corretas"""
    required_fields = ["api_key", "api_secret"]
    
    for field in required_fields:
        if BYBIT_CONFIG[field].startswith("SUA_") or BYBIT_CONFIG[field].startswith("SEU_"):
            raise ValueError(f"❌ CONFIGURE O CAMPO: {field} - Configure BYBIT_API_KEY_REAL e BYBIT_API_SECRET_REAL no Railway")
    
    # Validar valores de risco
    if BYBIT_CONFIG["risk_per_trade"] > 0.05:
        raise ValueError("❌ RISCO POR TRADE MUITO ALTO! Máximo recomendado: 0.05 (5%)")
    
    if SECURITY_CONFIG["max_drawdown"] > 0.20:
        raise ValueError("❌ DRAWDOWN MÁXIMO MUITO ALTO! Máximo recomendado: 0.20 (20%)")
    
    print("✅ CONFIGURAÇÃO AVANÇADA VALIDADA COM SUCESSO!")
    print(f"🤖 BOT: {BOT_CONFIG['bot_name']} v{BOT_CONFIG['version']}")
    print(f"🌐 MODO: {BOT_CONFIG['mode']} - CONTA REAL")
    print(f"💰 SALDO INICIAL: ${BYBIT_CONFIG['initial_balance']:.2f}")
    print(f"🎯 RISCO POR TRADE: {BYBIT_CONFIG['risk_per_trade']*100}%")
    print(f"🛡️  DRAWDOWN MÁXIMO: {SECURITY_CONFIG['max_drawdown']*100}%")
    print(f"🚀 MELHORIAS: Multi-Ativo, Sentiment Analysis, Risk Management Avançado")
    
    return True

# Testa a configuração quando o arquivo é executado
if __name__ == "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"❌ ERRO NA CONFIGURAÇÃO: {e}")
        print("\n🔧 CONFIGURAÇÃO NO RAILWAY:")
        print("1. Vá em Variables no seu projeto Railway")
        print("2. Adicione BYBIT_API_KEY_REAL com sua API Key REAL")
        print("3. Adicione BYBIT_API_SECRET_REAL com seu Secret REAL")
        print("4. Verifique se BYBIT_TESTNET está como false")
