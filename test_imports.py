# test_imports.py
try:
    import telegram
    print("✅ telegram - OK")
except ImportError as e:
    print(f"❌ telegram - Erro: {e}")

try:
    import flask
    print("✅ flask - OK")
except ImportError as e:
    print(f"❌ flask - Erro: {e}")

try:
    import requests
    print("✅ requests - OK")
except ImportError as e:
    print(f"❌ requests - Erro: {e}")

try:
    import numpy
    print("✅ numpy - OK")
except ImportError as e:
    print(f"❌ numpy - Erro: {e}")

try:
    import pandas
    print("✅ pandas - OK")
except ImportError as e:
    print(f"❌ pandas - Erro: {e}")

try:
    import pybit
    print("✅ pybit - OK")
except ImportError as e:
    print(f"❌ pybit - Erro: {e}")

try:
    import sklearn
    print("✅ scikit-learn - OK")
except ImportError as e:
    print(f"❌ scikit-learn - Erro: {e}")

try:
    from textblob import TextBlob
    print("✅ textblob - OK")
except ImportError as e:
    print(f"❌ textblob - Erro: {e}")

try:
    import newspaper
    print("✅ newspaper3k - OK")
except ImportError as e:
    print(f"❌ newspaper3k - Erro: {e}")

try:
    import gunicorn
    print("✅ gunicorn - OK")
except ImportError as e:
    print(f"❌ gunicorn - Erro: {e}")

print("\n🎯 Teste de importações concluído!")
