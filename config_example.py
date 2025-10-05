# Ejemplo de archivo de configuración
# Copiar este archivo a config.py y actualizar con tus credenciales

# Credenciales de Twitter/X (si usas API oficial)
TWITTER_API_KEY = "your_api_key_here"
TWITTER_API_SECRET = "your_api_secret_here"
TWITTER_ACCESS_TOKEN = "your_access_token_here"
TWITTER_ACCESS_TOKEN_SECRET = "your_access_token_secret_here"
TWITTER_BEARER_TOKEN = "your_bearer_token_here"

# Configuración de scraping
MAX_TWEETS_PER_REQUEST = 100
MAX_REPLIES_PER_TWEET = 200
PAGINATION_DELAY = 2  # segundos entre requests para evitar rate limiting

# Configuración de almacenamiento
DATA_DIR = "data"
OUTPUT_FORMAT = "json"

# Configuración de Selenium (si se usa)
HEADLESS_BROWSER = True
CHROME_DRIVER_PATH = None  # None para autodetección
