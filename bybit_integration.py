# bybit_integration.py - LINHA 53-60 (setup_exchange method)
def setup_exchange(self):
    """Configuração completa da exchange Bybit"""
    try:
        self.exchange = ccxt.bybit({
            'apiKey': self.config['api_key'],
            'secret': self.config['api_secret'],
            'sandbox': True,  # 👈 FORÇAR TESTNET
            'enableRateLimit': True,
            'rateLimit': 100,
            'options': {
                'defaultType': 'linear',
                'adjustForTimeDifference': True,
                'recvWindow': 10000,
            },
        })
        
        # 👇 REMOVER ESTA LINHA QUE CAUSA O ERRO
        # server_time = self.exchange.fetch_time()
        
        # Em vez disso, testar conexão de forma segura
        try:
            markets = self.exchange.load_markets()
            self.logger.info(f"✅ BYBIT TESTNET CONECTADO - {len(markets)} mercados")
        except Exception as e:
            self.logger.warning(f"⚠️ AVISO: {e}")
            self.logger.info("🔄 Continuando com conexão básica...")
