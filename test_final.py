# test_final.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete():
    print("🧪 TESTE COMPLETO DO ULTRABOT")
    print("=" * 50)
    
    try:
        # Testar módulos principais
        from trader.core import UltraBotCore
        from trader.bybit_analyser import BybitAnalyser
        from trader.cognitive_engine import CognitiveEngine
        
        print("✅ Módulos principais importados com sucesso!")
        
        # Testar inicialização
        bot = UltraBotCore()
        print("✅ UltraBotCore inicializado!")
        
        # Testar análise de mercado
        analyser = BybitAnalyser()
        market_data = analyser.get_market_data()
        print(f"✅ Dados de mercado: {len(market_data['close'])} candles")
        
        # Testar análise cognitiva
        cognitive = CognitiveEngine()
        sentiment = cognitive.get_news_sentiment()
        print(f"✅ Análise de sentimentos: {sentiment['reason']}")
        
        # Testar estratégias
        signals = cognitive.analyze(market_data, sentiment)
        print(f"✅ Sinais gerados: {len(signals)}")
        
        # Testar status do bot
        status = bot.get_status()
        print(f"✅ Status do bot: {status['status']}")
        
        # Testar Telegram (se disponível)
        try:
            from telegram_bot.bot import TelegramBot
            print("✅ Módulo Telegram importado!")
        except ImportError as e:
            print(f"⚠️ Telegram não disponível: {e}")
        
        print("\n🎉 🎉 🎉 ULTRABOT PRONTO PARA OPERAR! 🎉 🎉 🎉")
        print("\n🚀 Para iniciar: python app.py")
        print("📱 Telegram: Envie /start para o bot")
        print("🌐 Web: Acesse http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete()
