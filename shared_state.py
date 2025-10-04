import threading
from datetime import datetime

class SharedState:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SharedState, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        self.bot_status = "🔧 INICIANDO"
        self.performance = {
            'ciclos': 0,
            'trades': 0,
            'saldo': 0.0,
            'lucro': 0.0,
            'vitorias': 0,
            'derrotas': 0
        }
        self.conexao_exchange = False
        self.modalidade = "REAL"
        self.ultimos_sinais = []
        self.ultima_atualizacao = datetime.now().strftime("%H:%M:%S")
        self._lock = threading.RLock()
    
    def atualizar_status(self, status):
        with self._lock:
            self.bot_status = status
            self.ultima_atualizacao = datetime.now().strftime("%H:%M:%S")
    
    def adicionar_sinal(self, sinal):
        with self._lock:
            self.ultimos_sinais.append(f"[{datetime.now().strftime('%H:%M:%S')}] {sinal}")
            if len(self.ultimos_sinais) > 20:
                self.ultimos_sinais.pop(0)
    
    def atualizar_performance(self, **kwargs):
        with self._lock:
            for key, value in kwargs.items():
                if key in self.performance:
                    self.performance[key] = value

shared_state = SharedState()
