# install_dependencies.py - Instala dependências manualmente
import subprocess
import sys

def install_dependencies():
    packages = [
        "requests==2.31.0",
        "ccxt==4.1.77", 
        "pandas==2.2.0",
        "numpy==1.26.0",
        "python-dotenv==1.0.0",
        "scikit-learn==1.4.0",
        "joblib==1.3.2",
        "pandas-ta",  # Sem versão específica
        "aiohttp==3.9.1",
        "websocket-client==1.6.3",
        "colorama==0.4.6"
    ]
    
    for package in packages:
        try:
            print(f"📦 Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} instalado com sucesso")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar {package}: {e}")
            # Tenta instalar sem versão específica
            if "==" in package:
                base_package = package.split("==")[0]
                print(f"🔄 Tentando instalar {base_package} sem versão específica...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", base_package])
                    print(f"✅ {base_package} instalado")
                except:
                    print(f"❌ Falha crítica com {base_package}")

if __name__ == "__main__":
    install_dependencies()
    print("🚀 Todas as dependências instaladas!")
