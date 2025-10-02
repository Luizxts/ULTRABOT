# test_bot.py
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from trader.core import UltraBotCore
    print("✅ UltraBotCore - OK")
    
    # Testar inicialização
    bot = UltraBotCore()
    print("✅ Bot inicializado - OK")
    
    # Testar status
    status = bot.get_status()
    print(f"✅ Status: {status}")
    
    print("\n🎉 Tudo funcionando! O ULTRABOT está pronto!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
