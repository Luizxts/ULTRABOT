# railway_check.py - Verifica se tudo está configurado corretamente
import os
import sys

def check_railway_environment():
    print("🔍 VERIFICANDO AMBIENTE RAILWAY...")
    
    required_vars = ['BYBIT_API_KEY', 'BYBIT_API_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ VARIÁVEIS FALTANDO: {missing_vars}")
        print("💡 Configure no Railway: Settings > Variables")
        return False
    
    print("✅ TODAS AS VARIÁVEIS CONFIGURADAS")
    print(f"🌐 TESTNET: {os.getenv('BYBIT_TESTNET', 'true')}")
    print(f"🤖 MODO: {os.getenv('BOT_MODE', 'BYBIT_TESTNET')}")
    
    return True

if __name__ == "__main__":
    if check_railway_environment():
        print("🚀 AMBIENTE PRONTO PARA DEPLOY!")
        sys.exit(0)
    else:
        print("❌ CONFIGURAÇÃO INCOMPLETA")
        sys.exit(1)
