import threading
from datetime import datetime
from typing import Dict, Any

class GlobalState:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GlobalState, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        self._lock = threading.RLock()
        self._data = {
            'bot_status': '🔧 INICIANDO',
            'modalidade': 'REAL',
            'conexao_exchange': False,
            'ultima_atualizacao': datetime.now().strftime('%H:%M:%S'),
            'performance': {
                'ciclos': 0,
                'trades': 0,
                'saldo': 0.0,
                'lucro': 0.0,
                'vitorias': 0,
                'derrotas': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0
            },
            'ultimos_sinais': [],
            'risk_metrics': {},
            'ai_metrics': {},
            'strategy_metrics': {},
            'trades_ativos': []
        }
    
    def update(self, updates: Dict[str, Any]):
        """Atualizar múltiplos valores de forma thread-safe"""
        with self._lock:
            for key, value in updates.items():
                if '.' in key:
                    main_key, sub_key = key.split('.', 1)
                    if main_key in self._data and isinstance(self._data[main_key], dict):
                        self._data[main_key][sub_key] = value
                else:
                    self._data[key] = value
            
            self._data['ultima_atualizacao'] = datetime.now().strftime('%H:%M:%S')
    
    def adicionar_sinal(self, sinal: str):
        """Adicionar sinal ao histórico"""
        with self._lock:
            self._data['ultimos_sinais'].append(
                f"[{datetime.now().strftime('%H:%M:%S')}] {sinal}"
            )
            if len(self._data['ultimos_sinais']) > 20:
                self._data['ultimos_sinais'].pop(0)
    
    @property
    def bot_status(self):
        with self._lock:
            return self._data['bot_status']
    
    @property
    def performance(self):
        with self._lock:
            return self._data['performance'].copy()
    
    @property
    def conexao_exchange(self):
        with self._lock:
            return self._data['conexao_exchange']
    
    @property
    def modalidade(self):
        with self._lock:
            return self._data['modalidade']
    
    @property
    def ultimos_sinais(self):
        with self._lock:
            return self._data['ultimos_sinais'].copy()
    
    @property
    def ultima_atualizacao(self):
        with self._lock:
            return self._data['ultima_atualizacao']
    
    def to_dict(self):
        """Retornar estado completo como dict"""
        with self._lock:
            return self._data.copy()
