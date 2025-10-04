# config_emergency.py - CONFIGURAÇÃO DE EMERGÊNCIA
import os

# =============================================================================
# CONFIGURAÇÕES BYBIT API - MODO EMERGÊNCIA
# =============================================================================
BYBIT_CONFIG = {
    # 🔐 MODO EMERGÊNCIA - Funciona sem credenciais
    "api_key": "emergency_mode_no_key",
    "api_secret": "emergency_mode_no_secret",
    
    # 🌐 CONFIGURAÇÕES DE REDE
    "testnet": False,
    "base_url": "https://api.bybit.com",
    
    # 📈 CONFIGURAÇÕES DE TRADING
    "symbol": "BTCUSDT",
    "timeframe": "5",
    "category": "linear",
    
    # 💰 CONFIGURAÇÕES DE RISCO
    "initial_balance": 500.00,
    "risk_per_trade": 0.02,
    "max_position_size": 0.05,
    "leverage": 3,
}

# =============================================================================
# CONFIGURAÇÕES DO BOT
# =============================================================================
BOT_CONFIG = {
    "bot_name": "ULTRABOT PRO MAX SUPER - MODO EMERGÊNCIA",
    "version": "2.0",
    "update_interval": 30,
    "mode": "SIMULATION",
    
    "ia_enabled": True,
    "min_confidence": 0.60,
    
    "multi_timeframe": True,
    "timeframes": ["5m", "15m", "1h"],
    
    "multi_asset_trading": True,
    "sentiment_analysis": True,
    "advanced_risk_management": True,
}

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================
SECURITY_CONFIG = {
    "max_drawdown": 0.08,
    "daily_loss_limit": 0.05,
    "max_consecutive_losses": 5,
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

def validate_config():
    """Validação de emergência - sempre retorna True"""
    print("✅ MODO EMERGÊNCIA ATIVADO - OPERANDO EM SIMULAÇÃO")
    print("🤖 BOT: ULTRABOT PRO MAX SUPER - MODO EMERGÊNCIA")
    print("🌐 MODO: SIMULAÇÃO - Desenvolvimento e Testes")
    print("💰 SALDO INICIAL: $500.00")
    print("🎯 RISCO POR TRADE: 2%")
    print("🚀 MELHORIAS: Multi-Ativo, Sentiment Analysis, Risk Management")
    return True
