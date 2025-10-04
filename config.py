# config.py - CONFIGURAÇÃO FORÇADA MODO REAL
import os

BYBIT_CONFIG = {
    "api_key": os.getenv('BYBIT_API_KEY_REAL', ''),
    "api_secret": os.getenv('BYBIT_API_SECRET_REAL', ''),
    "testnet": False,
    "base_url": "https://api.bybit.com",
    "symbol": "BTCUSDT",
    "timeframe": "5",
    "category": "linear",
    "initial_balance": 500.00,
    "risk_per_trade": 0.02,
    "max_position_size": 0.05,
    "leverage": 3,
}

BOT_CONFIG = {
    "bot_name": "ULTRABOT PRO MAX SUPER - CONTA REAL",
    "version": "2.0", 
    "update_interval": 30,
    "mode": "BYBIT_MAINNET",
    "ia_enabled": True,
    "min_confidence": 0.60,
    "multi_timeframe": True,
    "timeframes": ["5m", "15m", "1h"],
    "multi_asset_trading": True,
    "sentiment_analysis": True,
    "advanced_risk_management": True,
}

SECURITY_CONFIG = {
    "max_drawdown": 0.08,
    "daily_loss_limit": 0.05,
    "max_consecutive_losses": 5,
    "auto_stop_loss": True,
    "emergency_stop": True,
    "volatility_check": True,
}

LOG_CONFIG = {
    "log_level": "INFO",
    "log_to_file": False,
    "log_colors": False,
}

def validate_config():
    print("✅ CONFIGURAÇÃO CONTA REAL CARREGADA")
    print("🤖 ULTRABOT PRO MAX SUPER - CONTA REAL")
    print("🌐 MODO: BYBIT MAINNET - DINHEIRO REAL")
    
    # Verificar credenciais
    api_key = BYBIT_CONFIG['api_key']
    api_secret = BYBIT_CONFIG['api_secret']
    
    if not api_key or not api_secret:
        print("⚠️  CREDENCIAIS NÃO CONFIGURADAS - Configure no Railway:")
        print("   BYBIT_API_KEY_REAL = sua_chave_real")
        print("   BYBIT_API_SECRET_REAL = seu_secret_real")
        return False
    
    print("💰 PRONTO PARA OPERAR COM SALDO REAL")
    return True
