"""
Script de ejemplo para usar el Twitter/X Scraper
Demuestra cómo extraer conversaciones completas
"""

from twitter_scraper import TwitterScraper
from datetime import datetime


def example_single_conversation():
    """Ejemplo: Scraping de una sola conversación"""
    print("=" * 60)
    print("Ejemplo 1: Scraping de una conversación única")
    print("=" * 60)
    
    scraper = TwitterScraper(headless=True, data_dir="data")
    
    try:
        # Reemplazar con una URL real de Twitter/X
        tweet_url = "https://twitter.com/username/status/1234567890"
        
        print(f"\nExtrayendo conversación de: {tweet_url}")
        conversation = scraper.scrape_conversation(tweet_url, max_scrolls=5)
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}"
        scraper.save_to_json(conversation, filename)
        
        # Mostrar resumen
        print(f"\n✓ Conversación extraída exitosamente")
        print(f"  - Tweet principal: {conversation['main_tweet'].get('username', 'N/A')}")
        print(f"  - Texto: {conversation['main_tweet'].get('text', 'N/A')[:100]}...")
        print(f"  - Respuestas encontradas: {len(conversation['replies'])}")
        print(f"  - Archivo guardado: data/{filename}.json")
        
    finally:
        scraper.close()


def example_multiple_conversations():
    """Ejemplo: Scraping de múltiples conversaciones"""
    print("\n" + "=" * 60)
    print("Ejemplo 2: Scraping de múltiples conversaciones")
    print("=" * 60)
    
    scraper = TwitterScraper(headless=True, data_dir="data")
    
    try:
        # Lista de URLs de tweets (reemplazar con URLs reales)
        tweet_urls = [
            "https://twitter.com/username/status/1234567890",
            "https://twitter.com/username/status/0987654321",
            "https://twitter.com/username/status/1111111111",
        ]
        
        print(f"\nExtrayendo {len(tweet_urls)} conversaciones...")
        conversations = scraper.scrape_multiple_conversations(
            tweet_urls, 
            delay=5  # Espera 5 segundos entre cada request
        )
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversations_batch_{timestamp}"
        scraper.save_to_json(conversations, filename)
        
        # Mostrar resumen
        print(f"\n✓ {len(conversations)} conversaciones extraídas exitosamente")
        for i, conv in enumerate(conversations, 1):
            print(f"\n  Conversación {i}:")
            print(f"    - Usuario: {conv['main_tweet'].get('username', 'N/A')}")
            print(f"    - Respuestas: {len(conv['replies'])}")
        print(f"\n  - Archivo guardado: data/{filename}.json")
        
    finally:
        scraper.close()


def example_with_pagination():
    """Ejemplo: Scraping con paginación extendida"""
    print("\n" + "=" * 60)
    print("Ejemplo 3: Scraping con paginación hacia atrás en el tiempo")
    print("=" * 60)
    
    scraper = TwitterScraper(headless=True, data_dir="data")
    
    try:
        tweet_url = "https://twitter.com/username/status/1234567890"
        
        print(f"\nExtrayendo conversación con paginación extendida...")
        print("Esto cargará más respuestas históricas mediante scrolling")
        
        # Usar más scrolls para cargar más contenido histórico
        conversation = scraper.scrape_conversation(tweet_url, max_scrolls=10)
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_extended_{timestamp}"
        scraper.save_to_json(conversation, filename)
        
        print(f"\n✓ Conversación extraída con paginación extendida")
        print(f"  - Respuestas totales: {len(conversation['replies'])}")
        print(f"  - Archivo guardado: data/{filename}.json")
        
    finally:
        scraper.close()


def main():
    """Ejecuta todos los ejemplos"""
    print("\n🐦 Twitter/X Conversation Scraper - Ejemplos de Uso\n")
    
    # Descomentar el ejemplo que quieras ejecutar:
    
    # example_single_conversation()
    # example_multiple_conversations()
    # example_with_pagination()
    
    print("\n" + "=" * 60)
    print("NOTA: Para usar estos ejemplos:")
    print("1. Reemplaza las URLs de ejemplo con URLs reales de Twitter/X")
    print("2. Descomenta el ejemplo que quieras ejecutar en la función main()")
    print("3. Ejecuta: python example_usage.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
