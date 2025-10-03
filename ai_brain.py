import logging
import random
import numpy as np
from datetime import datetime, timedelta
import json
import os

class AIBrain:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory = self.load_memory()
        self.learning_rate = 0.1
        self.market_knowledge = self.initialize_market_knowledge()
        
    def initialize_market_knowledge(self):
        """Conhecimento inicial sobre pares de trading"""
        return {
            "BTCUSDT": {"volatility": "high", "trend_strength": "strong", "best_hours": [14, 22]},
            "ETHUSDT": {"volatility": "high", "trend_strength": "strong", "best_hours": [15, 23]},
            "ADAUSDT": {"volatility": "very_high", "trend_strength": "medium", "best_hours": [16, 2]},
            "DOTUSDT": {"volatility": "high", "trend_strength": "medium", "best_hours": [17, 1]},
            "LINKUSDT": {"volatility": "medium", "trend_strength": "strong", "best_hours": [18, 2]},
            "MATICUSDT": {"volatility": "high", "trend_strength": "medium", "best_hours": [19, 3]},
            "SOLUSDT": {"volatility": "very_high", "trend_strength": "strong", "best_hours": [20, 4]},
        }
    
    def load_memory(self):
        """Carrega memória da IA"""
        try:
            if os.path.exists("ai_memory.json"):
                with open("ai_memory.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return {"successful_trades": [], "failed_trades": [], "learned_patterns": {}}
    
    def save_memory(self):
        """Salva memória da IA"""
        try:
            with open("ai_memory.json", "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar memória: {e}")
    
    def analyze_market(self, pair, market_data):
        """Analisa o mercado com IA"""
        thoughts = []
        
        # Análise de tendência
        trend_analysis = self._analyze_trend(market_data)
        thoughts.append(f"📈 {trend_analysis}")
        
        # Análise de volatilidade
        vol_analysis = self._analyze_volatility(market_data)
        thoughts.append(f"🌊 {vol_analysis}")
        
        # Análise temporal
        time_analysis = self._analyze_time(pair)
        thoughts.append(f"⏰ {time_analysis}")
        
        # Recomendação baseada em aprendizado
        recommendation = self._generate_recommendation(pair, market_data)
        thoughts.append(f"💡 {recommendation}")
        
        return thoughts
    
    def _analyze_trend(self, market_data):
        """Analisa tendência do mercado"""
        price_change = float(market_data.get('price_24h_pcnt', 0)) * 100
        
        if price_change > 5:
            return "Tendência de ALTA forte detectada"
        elif price_change > 2:
            return "Tendência de alta moderada"
        elif price_change < -5:
            return "Tendência de BAIXA forte - Cuidado!"
        elif price_change < -2:
            return "Tendência de baixa moderada"
        else:
            return "Mercado lateralizado - Esperar oportunidades"
    
    def _analyze_volatility(self, market_data):
        """Analisa volatilidade"""
        # Simulação de análise de volatilidade
        volatility_level = random.choice(["baixa", "moderada", "alta"])
        
        if volatility_level == "alta":
            return "Volatilidade ALTA - Ótimo para scalping"
        elif volatility_level == "moderada":
            return "Volatilidade moderada - Boas condições"
        else:
            return "Volatilidade baixa - Mercado tranquilo"
    
    def _analyze_time(self, pair):
        """Analisa melhor horário para trading"""
        current_hour = datetime.now().hour
        best_hours = self.market_knowledge.get(pair, {}).get("best_hours", [12, 20])
        
        if current_hour in best_hours:
            return "Horário IDEAL para trading deste par!"
        elif abs(current_hour - best_hours[0]) <= 2:
            return "Horário bom - Mercado começando a movimentar"
        else:
            return "Horário regular - Monitorando oportunidades"
    
    def _generate_recommendation(self, pair, market_data):
        """Gera recomendação baseada em aprendizado"""
        # Aprendizado com trades anteriores
        successful_patterns = [t for t in self.memory["successful_trades"] if t["pair"] == pair]
        
        if len(successful_patterns) > 5:
            return f"Padrão RECORRENTE detectado em {pair} - Alta confiança"
        else:
            strategies = [
                "Estratégia conservadora recomendada",
                "Aguardar confirmação de tendência",
                "Posicionar pequeno tamanho inicial",
                "Ótima oportunidade para diversificação"
            ]
            return random.choice(strategies)
    
    def learn_from_trade(self, trade_result):
        """Aprende com resultado do trade"""
        if trade_result["profit"] > 0:
            self.memory["successful_trades"].append({
                "timestamp": datetime.now().isoformat(),
                "pair": trade_result["pair"],
                "strategy": trade_result["strategy"],
                "profit": trade_result["profit"]
            })
        else:
            self.memory["failed_trades"].append({
                "timestamp": datetime.now().isoformat(),
                "pair": trade_result["pair"],
                "strategy": trade_result["strategy"],
                "loss": trade_result["profit"]
            })
        
        # Limitar memória
        self.memory["successful_trades"] = self.memory["successful_trades"][-100:]
        self.memory["failed_trades"] = self.memory["failed_trades"][-50:]
        
        self.save_memory()
    
    def get_ai_thoughts(self, pair, market_data):
        """Retorna pensamentos da IA em tempo real"""
        return self.analyze_market(pair, market_data)
