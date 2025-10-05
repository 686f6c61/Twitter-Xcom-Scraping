"""
Twitter/X Scraper - Módulo principal para extraer conversaciones completas
Incluye tweets principales y sus respuestas con paginación automática
"""

import json
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TwitterScraper:
    """
    Clase para scraping de conversaciones de Twitter/X
    """
    
    def __init__(self, headless: bool = True, data_dir: str = "data"):
        """
        Inicializa el scraper
        
        Args:
            headless: Si el navegador debe ejecutarse sin interfaz gráfica
            data_dir: Directorio donde guardar los datos
        """
        self.headless = headless
        self.data_dir = data_dir
        self.driver = None
        
        # Crear directorio de datos si no existe
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Directorio de datos creado: {self.data_dir}")
    
    def _setup_driver(self):
        """Configura el driver de Selenium"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("Driver de Chrome configurado")
    
    def _close_driver(self):
        """Cierra el driver de Selenium"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver cerrado")
    
    def extract_tweet_data(self, tweet_element) -> Dict:
        """
        Extrae datos de un elemento de tweet
        
        Args:
            tweet_element: Elemento web del tweet
            
        Returns:
            Diccionario con los datos del tweet
        """
        try:
            # Extraer texto del tweet
            try:
                text_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                text = text_element.text
            except NoSuchElementException:
                text = ""
            
            # Extraer nombre de usuario
            try:
                username_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                username = username_element.text
            except NoSuchElementException:
                username = "Unknown"
            
            # Extraer timestamp
            try:
                time_element = tweet_element.find_element(By.TAG_NAME, "time")
                timestamp = time_element.get_attribute("datetime")
            except NoSuchElementException:
                timestamp = None
            
            # Extraer estadísticas
            try:
                reply_count = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="reply"]').text
            except:
                reply_count = "0"
            
            try:
                retweet_count = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]').text
            except:
                retweet_count = "0"
            
            try:
                like_count = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="like"]').text
            except:
                like_count = "0"
            
            return {
                "text": text,
                "username": username,
                "timestamp": timestamp,
                "reply_count": reply_count,
                "retweet_count": retweet_count,
                "like_count": like_count,
                "extracted_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error extrayendo datos del tweet: {e}")
            return {}
    
    def scrape_conversation(self, tweet_url: str, max_scrolls: int = 5) -> Dict:
        """
        Scrape una conversación completa desde una URL de tweet
        
        Args:
            tweet_url: URL del tweet principal
            max_scrolls: Número máximo de scrolls para cargar más respuestas
            
        Returns:
            Diccionario con el tweet principal y sus respuestas
        """
        if not self.driver:
            self._setup_driver()
        
        logger.info(f"Accediendo a: {tweet_url}")
        self.driver.get(tweet_url)
        
        # Esperar a que se cargue el contenido
        time.sleep(3)
        
        conversation = {
            "tweet_url": tweet_url,
            "main_tweet": {},
            "replies": [],
            "scrape_date": datetime.now().isoformat()
        }
        
        try:
            # Extraer tweet principal
            wait = WebDriverWait(self.driver, 10)
            articles = wait.until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "article"))
            )
            
            if articles:
                logger.info("Tweet principal encontrado")
                conversation["main_tweet"] = self.extract_tweet_data(articles[0])
            
            # Scroll para cargar más respuestas
            logger.info(f"Cargando respuestas con {max_scrolls} scrolls...")
            for i in range(max_scrolls):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                logger.info(f"Scroll {i+1}/{max_scrolls} completado")
            
            # Extraer todas las respuestas
            all_articles = self.driver.find_elements(By.TAG_NAME, "article")
            logger.info(f"Total de elementos encontrados: {len(all_articles)}")
            
            # El primer artículo es el tweet principal, el resto son respuestas
            for article in all_articles[1:]:
                reply_data = self.extract_tweet_data(article)
                if reply_data:
                    conversation["replies"].append(reply_data)
            
            logger.info(f"Conversación extraída: {len(conversation['replies'])} respuestas")
            
        except TimeoutException:
            logger.error("Timeout esperando a que carguen los elementos")
        except Exception as e:
            logger.error(f"Error durante el scraping: {e}")
        
        return conversation
    
    def scrape_multiple_conversations(self, tweet_urls: List[str], delay: int = 5) -> List[Dict]:
        """
        Scrape múltiples conversaciones
        
        Args:
            tweet_urls: Lista de URLs de tweets
            delay: Tiempo de espera entre requests (segundos)
            
        Returns:
            Lista de conversaciones extraídas
        """
        conversations = []
        
        for i, url in enumerate(tweet_urls):
            logger.info(f"Procesando tweet {i+1}/{len(tweet_urls)}")
            conversation = self.scrape_conversation(url)
            conversations.append(conversation)
            
            # Delay entre requests
            if i < len(tweet_urls) - 1:
                logger.info(f"Esperando {delay} segundos antes del siguiente request...")
                time.sleep(delay)
        
        return conversations
    
    def save_to_json(self, data: Dict or List[Dict], filename: str):
        """
        Guarda los datos en formato JSON
        
        Args:
            data: Datos a guardar
            filename: Nombre del archivo (sin extensión)
        """
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Datos guardados en: {filepath}")
    
    def close(self):
        """Cierra el scraper y limpia recursos"""
        self._close_driver()


def main():
    """Función principal de ejemplo"""
    # Ejemplo de uso
    scraper = TwitterScraper(headless=True, data_dir="data")
    
    try:
        # URL de ejemplo (reemplazar con URL real)
        tweet_url = "https://twitter.com/username/status/1234567890"
        
        # Scrape una conversación
        conversation = scraper.scrape_conversation(tweet_url, max_scrolls=5)
        
        # Guardar datos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scraper.save_to_json(conversation, f"conversation_{timestamp}")
        
        print(f"\nResumen:")
        print(f"Tweet principal: {conversation['main_tweet'].get('text', 'N/A')[:50]}...")
        print(f"Número de respuestas: {len(conversation['replies'])}")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
