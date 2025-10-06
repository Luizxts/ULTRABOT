#!/usr/bin/env python3
"""
TAVARES A EVOLUÇÃO - BYBIT REAL
Sistema Neural Autônomo de Trading COM DINHEIRO REAL
"""

import asyncio
import logging
import sys
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger('TavaresMain')

async def main():
    """Função principal"""
    try:
        logger.info("🚀 INICIANDO TAVARES BYBIT REAL...")
        
        from core.tavares_telegram_bot import TavaresTelegramBot
        
        # Inicializar bot REAL
        tavares = TavaresTelegramBot()
        
        logger.info("✅ TAVARES BYBIT REAL INICIALIZADO")
        
        # Executar sistema REAL
        await tavares.executar_continuamente()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Parada solicitada pelo usuário")
    except Exception as e:
        logger.error(f"💥 ERRO NA INICIALIZAÇÃO REAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
