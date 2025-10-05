"""
Tests de integración REALES con la API de Twitter
Estos tests hacen peticiones reales a la API y requieren credenciales válidas
"""

import unittest
import os
import json
import csv
import shutil
import tempfile
import sys
from datetime import datetime

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from download_hashtag import TwitterHashtagScraper


@unittest.skipIf(
    not os.getenv('RAPIDAPI_KEY') or not os.getenv('RAPIDAPI_HOST'),
    "Credenciales de API no configuradas. Define RAPIDAPI_KEY y RAPIDAPI_HOST"
)
class TestRealAPIIntegration(unittest.TestCase):
    """
    Tests de integración con API real

    IMPORTANTE: Estos tests consumen requests de la API.
    Se recomienda ejecutarlos con moderación.
    """

    @classmethod
    def setUpClass(cls):
        """Configuración una sola vez para toda la clase"""
        print("\n" + "=" * 70)
        print("INICIANDO TESTS DE INTEGRACIÓN CON API REAL")
        print("=" * 70)
        print(f"API Host: {os.getenv('RAPIDAPI_HOST')}")
        print(f"API Key configurada: {'Sí' if os.getenv('RAPIDAPI_KEY') else 'No'}")
        print("=" * 70 + "\n")

    def setUp(self):
        """Configuración antes de cada test"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Crear carpeta scraping en el directorio temporal
        os.makedirs('scraping', exist_ok=True)

        self.scraper = TwitterHashtagScraper()

    def tearDown(self):
        """Limpieza después de cada test"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_search_tweets_hashtag_real(self):
        """Test REAL: Buscar tweets por hashtag (#Python) - 1 búsqueda"""
        print("\n[TEST] Buscando tweets reales con hashtag #Python...")

        tweets = self.scraper.search_tweets(
            query='Python',
            mode='latest',
            max_tweets=3,
            is_hashtag=True
        )

        print(f"✓ Tweets encontrados: {len(tweets)}")

        # Verificaciones
        self.assertIsInstance(tweets, list)
        self.assertGreater(len(tweets), 0, "Debería encontrar al menos 1 tweet sobre #Python")

        # Verificar estructura del primer tweet
        if tweets:
            first_tweet = tweets[0]
            self.assertIn('id', first_tweet)
            self.assertIn('text', first_tweet)
            self.assertIn('username', first_tweet)
            print(f"✓ Primer tweet: @{first_tweet.get('username')}: {first_tweet.get('text')[:50]}...")

    def test_02_search_tweets_text_real(self):
        """Test REAL: Buscar tweets por texto libre"""
        print("\n[TEST] Buscando tweets reales con texto 'AI'...")

        tweets = self.scraper.search_tweets(
            query='AI',
            mode='top',
            max_tweets=3,
            is_hashtag=False
        )

        print(f"✓ Tweets encontrados: {len(tweets)}")

        self.assertIsInstance(tweets, list)
        self.assertGreater(len(tweets), 0, "Debería encontrar tweets sobre AI")

    def test_03_search_all_modes_real(self):
        """Test REAL: Probar todos los modos de búsqueda"""
        modes = ['latest', 'top', 'photos', 'videos']

        for mode in modes:
            with self.subTest(mode=mode):
                print(f"\n[TEST] Probando modo: {mode}")

                tweets = self.scraper.search_tweets(
                    query='technology',
                    mode=mode,
                    max_tweets=2,
                    is_hashtag=False
                )

                print(f"✓ Modo {mode}: {len(tweets)} tweets")

                self.assertIsInstance(tweets, list)
                # Puede retornar 0 tweets en algunos modos (ej: photos si no hay tweets con fotos)
                self.assertGreaterEqual(len(tweets), 0)

    def test_04_get_tweet_replies_real(self):
        """Test REAL: Obtener respuestas de un tweet real"""
        print("\n[TEST] Obteniendo respuestas de tweets reales...")

        # Primero buscar un tweet
        tweets = self.scraper.search_tweets(
            query='Python',
            mode='latest',
            max_tweets=3,
            is_hashtag=True
        )

        self.assertGreater(len(tweets), 0, "Necesitamos al menos 1 tweet para probar")

        # Intentar obtener respuestas del primer tweet
        tweet_id = tweets[0].get('id')
        print(f"✓ Obteniendo respuestas del tweet ID: {tweet_id}")

        replies = self.scraper.get_tweet_replies(tweet_id)

        print(f"✓ Respuestas encontradas: {len(replies)}")

        # Las respuestas pueden ser 0, pero debe retornar una lista
        self.assertIsInstance(replies, list)
        self.assertGreaterEqual(len(replies), 0)

    def test_05_download_full_conversation_real(self):
        """Test REAL: Descargar conversación completa sin respuestas"""
        print("\n[TEST] Descargando conversación completa (sin respuestas)...")

        conversation = self.scraper.download_full_conversation(
            query='AI',
            mode='latest',
            max_tweets=3,
            include_replies=False,
            is_hashtag=True
        )

        print(f"✓ Tweets principales: {conversation['total_main_tweets']}")

        # Verificaciones
        self.assertIn('query', conversation)
        self.assertEqual(conversation['query'], 'AI')
        self.assertEqual(conversation['search_type'], 'hashtag')
        self.assertGreater(conversation['total_main_tweets'], 0)
        self.assertIsInstance(conversation['tweets'], list)
        self.assertEqual(conversation['total_replies'], 0)

    def test_06_download_with_replies_real(self):
        """Test REAL: Descargar conversación con respuestas"""
        print("\n[TEST] Descargando conversación completa (con respuestas)...")

        conversation = self.scraper.download_full_conversation(
            query='Python',
            mode='latest',
            max_tweets=2,
            include_replies=True,
            is_hashtag=True
        )

        print(f"✓ Tweets principales: {conversation['total_main_tweets']}")
        print(f"✓ Total de respuestas: {conversation['total_replies']}")

        # Verificaciones
        self.assertGreater(conversation['total_main_tweets'], 0)
        self.assertGreaterEqual(conversation['total_replies'], 0)
        self.assertIsInstance(conversation['tweets'], list)

        # Verificar estructura de tweets con respuestas
        for item in conversation['tweets']:
            self.assertIn('tweet', item)
            self.assertIn('replies', item)
            self.assertIsInstance(item['replies'], list)

    def test_07_save_to_json_real(self):
        """Test REAL: Guardar datos en JSON"""
        print("\n[TEST] Guardando datos en JSON...")

        # Obtener datos reales
        conversation = self.scraper.download_full_conversation(
            query='test',
            mode='latest',
            max_tweets=2,
            include_replies=False,
            is_hashtag=True
        )

        # Guardar
        filepath = self.scraper.save_to_json(conversation)

        print(f"✓ Archivo guardado: {filepath}")

        # Verificar
        self.assertTrue(os.path.exists(filepath))

        # Leer y verificar contenido
        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        self.assertEqual(loaded_data['query'], 'test')
        self.assertIn('tweets', loaded_data)
        print(f"✓ JSON válido con {len(loaded_data['tweets'])} tweets")

    def test_08_export_to_csv_real(self):
        """Test REAL: Exportar a CSV"""
        print("\n[TEST] Exportando datos a CSV...")

        # Obtener datos reales
        conversation = self.scraper.download_full_conversation(
            query='Python',
            mode='latest',
            max_tweets=3,
            include_replies=False,
            is_hashtag=True
        )

        # Exportar a CSV
        csv_filepath = self.scraper.export_to_csv(conversation)

        print(f"✓ CSV guardado: {csv_filepath}")

        # Verificar
        self.assertIsNotNone(csv_filepath)
        self.assertTrue(os.path.exists(csv_filepath))

        # Leer y verificar contenido
        with open(csv_filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertGreater(len(rows), 0)
        self.assertIn('id', rows[0])
        self.assertIn('usuario', rows[0])
        self.assertIn('texto', rows[0])
        self.assertIn('likes', rows[0])

        print(f"✓ CSV válido con {len(rows)} filas")

    def test_09_apply_filters_min_likes_real(self):
        """Test REAL: Aplicar filtro de likes mínimos"""
        print("\n[TEST] Aplicando filtro de likes mínimos...")

        # Obtener datos
        conversation = self.scraper.download_full_conversation(
            query='Python',
            mode='top',  # Top para tener tweets con más likes
            max_tweets=10,
            include_replies=False,
            is_hashtag=True
        )

        original_count = conversation['total_main_tweets']
        print(f"✓ Tweets originales: {original_count}")

        # Aplicar filtro (5 likes mínimo)
        filtered = self.scraper.apply_filters(conversation, min_likes=5)

        filtered_count = filtered['total_main_tweets']
        print(f"✓ Tweets después del filtro (min 5 likes): {filtered_count}")

        # Verificar que el filtro funcionó
        self.assertLessEqual(filtered_count, original_count)

        # Verificar que todos los tweets tienen >= 5 likes
        for item in filtered['tweets']:
            self.assertGreaterEqual(item['tweet'].get('likes', 0), 5)

    def test_10_apply_filters_verified_real(self):
        """Test REAL: Aplicar filtro de solo verificados"""
        print("\n[TEST] Aplicando filtro de solo verificados...")

        # Obtener datos
        conversation = self.scraper.download_full_conversation(
            query='technology',
            mode='top',
            max_tweets=10,
            include_replies=False,
            is_hashtag=False
        )

        original_count = conversation['total_main_tweets']
        print(f"✓ Tweets originales: {original_count}")

        # Aplicar filtro
        filtered = self.scraper.apply_filters(conversation, verified_only=True)

        filtered_count = filtered['total_main_tweets']
        print(f"✓ Tweets de verificados: {filtered_count}")

        # Verificar
        self.assertLessEqual(filtered_count, original_count)

        # Verificar que todos son verificados
        for item in filtered['tweets']:
            tweet = item['tweet']
            is_verified = tweet.get('is_verified', False) or tweet.get('is_blue_verified', False)
            self.assertTrue(is_verified)

    def test_11_pagination_real(self):
        """Test REAL: Verificar paginación - 2 búsquedas (paginación)"""
        print("\n[TEST] Probando paginación (extrayendo 25 tweets)...")

        tweets = self.scraper.search_tweets(
            query='AI',
            mode='latest',
            max_tweets=25,  # Más de 20 para forzar paginación (2 páginas)
            is_hashtag=True
        )

        print(f"✓ Tweets extraídos: {len(tweets)}")

        # Verificar que se paginó correctamente
        self.assertGreaterEqual(len(tweets), 20, "Debería paginar y obtener más de 20 tweets")

        # Verificar que no hay duplicados por ID
        tweet_ids = [t.get('id') for t in tweets if t.get('id')]
        unique_ids = set(tweet_ids)
        self.assertEqual(len(tweet_ids), len(unique_ids), "No debe haber IDs duplicados")

    def test_12_complete_workflow_real(self):
        """Test REAL: Flujo completo end-to-end - 1 búsqueda"""
        print("\n[TEST] Flujo completo: búsqueda → JSON → CSV...")

        # 1. Búsqueda
        conversation = self.scraper.download_full_conversation(
            query='Python',
            mode='latest',
            max_tweets=3,
            include_replies=False,
            is_hashtag=True
        )

        print(f"✓ 1. Búsqueda: {conversation['total_main_tweets']} tweets")
        self.assertGreater(conversation['total_main_tweets'], 0)

        # 2. Guardar JSON
        json_file = self.scraper.save_to_json(conversation)
        self.assertTrue(os.path.exists(json_file))
        print(f"✓ 2. JSON guardado: {json_file}")

        # 3. Exportar CSV
        csv_file = self.scraper.export_to_csv(conversation)
        self.assertIsNotNone(csv_file)
        self.assertTrue(os.path.exists(csv_file))
        print(f"✓ 3. CSV exportado: {csv_file}")

        print("✓ Flujo completo ejecutado correctamente")


if __name__ == '__main__':
    # Ejecutar con verbosidad
    unittest.main(verbosity=2)
