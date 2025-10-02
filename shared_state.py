# shared_state.py - Estado global compartilhado
import json
import os
from datetime import datetime

class SharedState:
    def __init__(self):
        self.state_file = 'bot_state.json'
    
    def get_state(self):
        """Obtém o estado atual do bot"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Estado padrão
        return {
            'running': False,
            'started_at': None,
            'trades_today': 0,
            'profit_today': 0.0,
            'last_update': datetime.now().isoformat()
        }
    
    def set_state(self, running, trades=0, profit=0.0):
        """Define o estado do bot"""
        state = {
            'running': running,
            'started_at': datetime.now().isoformat() if running else None,
            'trades_today': trades,
            'profit_today': profit,
            'last_update': datetime.now().isoformat()
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar estado: {e}")
            return False

# Instância global
shared_state = SharedState()
