import requests
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger('AnaliseSentimentos')

class AnalisadorSentimentos:
    """Analisador de sentimentos para TAVARES"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.sentiment_history = []
        logger.info("📰 ANALISADOR DE SENTIMENTOS INICIALIZADO")
    
    def analisar_sentimento_mercado(self):
        """Analisar sentimento geral do mercado"""
        try:
            noticias = self._coletar_noticias_sincrono()
            
            if not noticias:
                return self._analise_simulada()
            
            sentimentos = []
            for noticia in noticias:
                analise = self.analisar_sentimento_texto(
                    f"{noticia['titulo']} {noticia['texto']}"
                )
                sentimentos.append(analise)
            
            scores = [s['score'] for s in sentimentos]
            score_medio = sum(scores) / len(scores) if scores else 0
            
            # Determinar sentimento geral
            if score_medio >= 0.1:
                sentimento_geral = "MUITO_POSITIVO"
            elif score_medio >= 0.03:
                sentimento_geral = "POSITIVO"
            elif score_medio <= -0.1:
                sentimento_geral = "MUITO_NEGATIVO"
            elif score_medio <= -0.03:
                sentimento_geral = "NEGATIVO"
            else:
                sentimento_geral = "NEUTRO"
            
            resultado = {
                'sentimento_geral': sentimento_geral,
                'score_medio': score_medio,
                'intensidade': abs(score_medio),
                'total_noticias': len(noticias),
                'timestamp': datetime.now().isoformat()
            }
            
            self.sentiment_history.append(resultado)
            if len(self.sentiment_history) > 50:
                self.sentiment_history.pop(0)
            
            logger.info(f"📊 Sentimento: {sentimento_geral} (Score: {score_medio:.3f})")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de sentimento: {e}")
            return self._analise_simulada()
    
    def _coletar_noticias_sincrono(self):
        """Coletar notícias de forma síncrona"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get('https://cointelegraph.com/rss', headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')[:3]
                
                noticias = []
                for item in items:
                    titulo = item.find('title')
                    if titulo:
                        noticias.append({
                            'titulo': titulo.get_text(),
                            'texto': item.find('description').get_text() if item.find('description') else '',
                            'fonte': 'cointelegraph'
                        })
                return noticias
        except Exception as e:
            logger.debug(f"❌ Erro ao coletar notícias: {e}")
        
        return []
    
    def _analise_simulada(self):
        """Análise simulada baseada no horário"""
        from datetime import datetime
        import random
        
        hora = datetime.now().hour
        
        # Simular padrões de mercado baseados no horário
        if 9 <= hora <= 17:
            score = random.uniform(-0.02, 0.08)
        else:
            score = random.uniform(-0.05, 0.05)
        
        if score >= 0.05:
            sentimento_geral = "POSITIVO"
        elif score <= -0.05:
            sentimento_geral = "NEGATIVO"
        else:
            sentimento_geral = "NEUTRO"
        
        return {
            'sentimento_geral': sentimento_geral,
            'score_medio': score,
            'intensidade': abs(score),
            'total_noticias': 0,
            'timestamp': datetime.now().isoformat(),
            'simulado': True
        }
    
    def analisar_sentimento_texto(self, texto):
        """Analisar sentimento do texto"""
        try:
            texto = texto[:500]
            
            # Análise com VADER
            vader_score = self.analyzer.polarity_scores(texto)
            
            # Análise com TextBlob
            blob = TextBlob(texto)
            blob_score = blob.sentiment.polarity
            
            # Análise crypto
            crypto_score = self._analisar_sentimento_crypto(texto)
            
            # Score combinado
            score_final = (
                vader_score['compound'] * 0.6 +
                blob_score * 0.3 +
                crypto_score * 0.1
            )
            
            if score_final >= 0.05:
                sentimento = "POSITIVO"
            elif score_final <= -0.05:
                sentimento = "NEGATIVO"
            else:
                sentimento = "NEUTRO"
            
            return {
                'sentimento': sentimento,
                'score': score_final,
                'intensidade': abs(score_final)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de sentimento: {e}")
            return {'sentimento': 'NEUTRO', 'score': 0, 'intensidade': 0}
    
    def _analisar_sentimento_crypto(self, texto):
        """Análise de sentimento para criptomoedas"""
        texto_lower = texto.lower()
        score = 0
        keyword_count = 0
        
        positive_words = ['bullish', 'moon', 'rally', 'surge', 'green', 'growth', 'adoption', 'breakout', 'profit']
        negative_words = ['bearish', 'crash', 'dump', 'red', 'fud', 'regulation', 'ban', 'warning', 'loss']
        
        for word in positive_words:
            if word in texto_lower:
                score += 0.1
                keyword_count += 1
        
        for word in negative_words:
            if word in texto_lower:
                score -= 0.1
                keyword_count += 1
        
        if keyword_count > 0:
            score = score / keyword_count
        
        return max(min(score, 1), -1)
