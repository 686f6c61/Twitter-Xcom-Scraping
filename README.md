# Twitter/X Conversation Scraper 🐦

Este proyecto permite extraer y almacenar conversaciones completas de Twitter/X, incluyendo tweets principales y sus respuestas, con paginación automática hacia atrás en el tiempo. Los datos se guardan en formato JSON estructurado para análisis posterior.

## 📋 Características

- ✅ Extracción de tweets principales y todas sus respuestas
- ✅ Paginación automática hacia atrás en el tiempo mediante scrolling
- ✅ Almacenamiento en formato JSON estructurado
- ✅ Soporte para múltiples conversaciones en batch
- ✅ Extracción de metadatos (username, timestamp, likes, retweets, replies)
- ✅ Logging detallado del progreso
- ✅ Manejo de rate limiting con delays configurables

## 🚀 Instalación

### Prerrequisitos

- Python 3.7 o superior
- Chrome o Chromium instalado
- ChromeDriver (se puede instalar automáticamente con selenium)

### Pasos de instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/686f6c61/Twitter-Xcom-Scraping.git
cd Twitter-Xcom-Scraping
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. (Opcional) Configurar archivo de configuración:
```bash
cp config_example.py config.py
# Editar config.py con tus preferencias
```

## 💻 Uso

### Uso básico

```python
from twitter_scraper import TwitterScraper

# Crear instancia del scraper
scraper = TwitterScraper(headless=True, data_dir="data")

try:
    # Extraer una conversación
    tweet_url = "https://twitter.com/username/status/1234567890"
    conversation = scraper.scrape_conversation(tweet_url, max_scrolls=5)
    
    # Guardar datos
    scraper.save_to_json(conversation, "conversation_output")
    
    # Mostrar resumen
    print(f"Respuestas encontradas: {len(conversation['replies'])}")
    
finally:
    scraper.close()
```

### Extracción de múltiples conversaciones

```python
from twitter_scraper import TwitterScraper

scraper = TwitterScraper(headless=True, data_dir="data")

try:
    tweet_urls = [
        "https://twitter.com/user1/status/111111",
        "https://twitter.com/user2/status/222222",
        "https://twitter.com/user3/status/333333",
    ]
    
    # Extraer múltiples conversaciones con delay entre requests
    conversations = scraper.scrape_multiple_conversations(tweet_urls, delay=5)
    
    # Guardar todas las conversaciones
    scraper.save_to_json(conversations, "multiple_conversations")
    
finally:
    scraper.close()
```

### Paginación extendida

Para cargar más respuestas históricas, aumenta el parámetro `max_scrolls`:

```python
# Cargar más respuestas con más scrolls
conversation = scraper.scrape_conversation(tweet_url, max_scrolls=10)
```

## 📁 Estructura del proyecto

```
Twitter-Xcom-Scraping/
├── twitter_scraper.py      # Módulo principal del scraper
├── example_usage.py        # Ejemplos de uso
├── config_example.py       # Configuración de ejemplo
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Documentación
├── .gitignore             # Archivos ignorados por Git
└── data/                  # Directorio de salida (creado automáticamente)
    └── *.json            # Archivos JSON con conversaciones extraídas
```

## 📊 Formato de datos de salida

Los datos se guardan en formato JSON con la siguiente estructura:

```json
{
  "tweet_url": "https://twitter.com/username/status/1234567890",
  "scrape_date": "2024-01-01T12:00:00",
  "main_tweet": {
    "text": "Contenido del tweet principal...",
    "username": "Usuario",
    "timestamp": "2024-01-01T10:00:00",
    "reply_count": "10",
    "retweet_count": "5",
    "like_count": "20",
    "extracted_at": "2024-01-01T12:00:00"
  },
  "replies": [
    {
      "text": "Primera respuesta...",
      "username": "Usuario2",
      "timestamp": "2024-01-01T10:05:00",
      "reply_count": "2",
      "retweet_count": "0",
      "like_count": "3",
      "extracted_at": "2024-01-01T12:00:00"
    }
  ]
}
```

## ⚙️ Configuración

### Parámetros del scraper

- `headless`: Ejecutar navegador sin interfaz gráfica (True/False)
- `data_dir`: Directorio donde guardar los archivos JSON
- `max_scrolls`: Número de scrolls para cargar más contenido histórico
- `delay`: Tiempo de espera entre requests (en segundos)

### Variables de configuración (config.py)

```python
MAX_TWEETS_PER_REQUEST = 100
MAX_REPLIES_PER_TWEET = 200
PAGINATION_DELAY = 2
DATA_DIR = "data"
OUTPUT_FORMAT = "json"
HEADLESS_BROWSER = True
```

## 🔍 Ejemplos

El archivo `example_usage.py` incluye tres ejemplos completos:

1. **Scraping de una conversación única**: Extrae un tweet y sus respuestas
2. **Scraping de múltiples conversaciones**: Procesa varias URLs en batch
3. **Scraping con paginación extendida**: Carga más respuestas históricas

Para ejecutar los ejemplos:

```bash
python example_usage.py
```

## ⚠️ Consideraciones importantes

1. **Rate Limiting**: Twitter/X tiene límites de tasa. Usa delays apropiados entre requests.
2. **Robots.txt**: Respeta las políticas de robots.txt de Twitter.
3. **Términos de Servicio**: Asegúrate de cumplir con los TOS de Twitter/X.
4. **Uso responsable**: No sobrecargues los servidores de Twitter con requests masivos.
5. **Datos personales**: Ten cuidado con los datos personales extraídos.

## 🛠️ Solución de problemas

### El scraper no encuentra elementos

- Verifica que la URL del tweet sea válida
- Twitter puede haber cambiado sus selectores CSS
- Intenta ejecutar sin `headless=True` para ver qué pasa

### TimeoutException

- Aumenta los tiempos de espera en el código
- Verifica tu conexión a internet
- Twitter puede estar bloqueando el acceso

### ChromeDriver issues

```bash
# Instalar webdriver-manager para gestión automática
pip install webdriver-manager
```

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⚖️ Disclaimer

Este proyecto es solo para fines educativos y de investigación. Los usuarios son responsables de cumplir con los términos de servicio de Twitter/X y las leyes aplicables sobre scraping y privacidad de datos.