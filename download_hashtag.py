#!/usr/bin/env python3
"""
Script para descargar toda la conversación en torno a un hashtag usando Twitter API

Versión: 0.2
Autor: @hex686f6c61
GitHub: https://github.com/686f6c61/Twitter-Xcom-Scraping
Twitter/X: https://x.com/hex686f6c61

Changelog v0.2:
- Añadido filtro de rango de fechas (desde-hasta)
"""

import os
import requests
import json
import time
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Variable global para control de interrupción
interrupted = False

def signal_handler(sig, frame):
    """Manejador para Ctrl+C"""
    global interrupted
    print("\n\nInterrupción detectada. Finalizando monitoreo...")
    interrupted = True

class TwitterHashtagScraper:
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = os.getenv('RAPIDAPI_HOST')

        if not self.api_key or not self.api_host:
            raise ValueError("RAPIDAPI_KEY y RAPIDAPI_HOST deben estar definidos en .env")

        self.base_url = f"https://{self.api_host}/v1"
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': self.api_host
        }

        print(f"Conectando a: {self.api_host}")
        print(f"API Key: {self.api_key[:10]}...{self.api_key[-4:]}")
        print()

    def search_tweets(self, query, mode='latest', max_tweets=None, is_hashtag=True, until_date=None, since_date=None):
        """
        Busca tweets por hashtag o texto

        Args:
            query: El término a buscar (hashtag o texto)
            mode: Modo de búsqueda ('top', 'latest', 'photos', 'videos')
            max_tweets: Número máximo de tweets a descargar (None = todos disponibles)
            is_hashtag: Si True, agrega # si no lo tiene. Si False, busca como texto
            until_date: Fecha límite superior (más reciente) - formato: YYYY-MM-DD
            since_date: Fecha límite inferior (más antigua) - formato: YYYY-MM-DD

        Returns:
            Lista de tweets
        """
        # Procesar query según el tipo de búsqueda
        if is_hashtag and not query.startswith('#'):
            search_query = f'#{query}'
        else:
            search_query = query

        all_tweets = []
        cursor = None
        tweet_count = 0
        page_count = 0
        oldest_date = None
        newest_date = None

        # Convertir fechas a timestamp si están presentes
        until_timestamp = None
        since_timestamp = None
        if until_date:
            from datetime import datetime as dt
            until_timestamp = int(dt.strptime(until_date, '%Y-%m-%d').timestamp())
        if since_date:
            from datetime import datetime as dt
            since_timestamp = int(dt.strptime(since_date, '%Y-%m-%d').timestamp())

        print(f"Buscando tweets para: {search_query}")
        print(f"Modo: {mode}")
        if since_date and until_date:
            print(f"Rango de fechas: desde {since_date} hasta {until_date}")
        elif until_date:
            print(f"Hasta fecha: {until_date}")
        elif since_date:
            print(f"Desde fecha: {since_date}")
        print("-" * 50)

        while True:
            # Preparar parámetros
            params = {
                'query': search_query,
                'mode': mode
            }

            if cursor:
                params['cursor'] = cursor

            try:
                # Hacer la petición
                response = requests.get(
                    f"{self.base_url}/search/tweets",
                    headers=self.headers,
                    params=params
                )

                response.raise_for_status()
                data = response.json()

                # Extraer tweets (la API devuelve en data.tweets)
                if 'data' in data and 'tweets' in data['data']:
                    tweets = data['data']['tweets']
                    cursor = data['data'].get('cursor')
                else:
                    tweets = data.get('tweets', [])

                if not tweets:
                    print("No se encontraron más tweets.")
                    break

                # Filtrar tweets por rango de fechas si está configurado
                filtered_tweets = []
                stop_pagination = False

                page_count += 1
                for tweet in tweets:
                    tweet_date = tweet.get('time_parsed', '')
                    tweet_timestamp = tweet.get('timestamp', 0)

                    # Actualizar fechas más antigua y más nueva
                    if not oldest_date or (tweet_date and tweet_date < oldest_date):
                        oldest_date = tweet_date
                    if not newest_date or (tweet_date and tweet_date > newest_date):
                        newest_date = tweet_date

                    # Verificar si el tweet está dentro del rango de fechas
                    if since_timestamp and tweet_timestamp < since_timestamp:
                        # Ya pasamos la fecha inferior, detener paginación
                        print(f"\nAlcanzada la fecha límite inferior: {since_date}")
                        stop_pagination = True
                        break

                    # Filtrar según el rango
                    if until_timestamp and tweet_timestamp > until_timestamp:
                        # Tweet más reciente que el límite superior, saltarlo
                        continue

                    if since_timestamp and tweet_timestamp < since_timestamp:
                        # Tweet más antiguo que el límite inferior, saltarlo
                        continue

                    # Tweet dentro del rango (o sin filtros)
                    filtered_tweets.append(tweet)

                all_tweets.extend(filtered_tweets)
                tweet_count = len(all_tweets)

                if stop_pagination:
                    print(f"Total descargado: {tweet_count} tweets en el rango especificado")
                    break

                print(f"Página {page_count}: {len(filtered_tweets)} tweets añadidos de {len(tweets)} | Total: {tweet_count} tweets | Más antiguo: {oldest_date[:10] if oldest_date else 'N/A'}")

                # Verificar si llegamos al máximo
                if max_tweets and tweet_count >= max_tweets:
                    all_tweets = all_tweets[:max_tweets]
                    print(f"\nAlcanzado el límite de {max_tweets} tweets")
                    break

                # Cursor ya se extrajo arriba junto con tweets

                if not cursor:
                    print("No hay más páginas disponibles.")
                    break

                # Pequeña pausa para no saturar la API
                time.sleep(1)

            except requests.exceptions.HTTPError as e:
                print(f"\n❌ Error HTTP: {e}")
                print(f"Respuesta: {response.text}")

                if response.status_code == 403:
                    print("\n⚠️  PROBLEMA DE SUSCRIPCIÓN:")
                    print("   Tu API key no está suscrita a esta API en RapidAPI.")
                    print("   Pasos para solucionarlo:")
                    print("   1. Ve a: https://rapidapi.com/omarmhaimdat/api/twitter-api45")
                    print("   2. Suscríbete a un plan (hay planes gratuitos)")
                    print("   3. Actualiza tu API key en .env si es necesario")

                break
            except Exception as e:
                print(f"❌ Error: {e}")
                break

        return all_tweets

    def get_tweet_replies(self, tweet_id):
        """
        Obtiene las respuestas de un tweet específico

        Args:
            tweet_id: ID del tweet

        Returns:
            Lista de respuestas
        """
        all_replies = []
        cursor = None

        while True:
            try:
                params = {}
                if cursor:
                    params['cursor'] = cursor

                response = requests.get(
                    f"{self.base_url}/tweets/{tweet_id}/replies",
                    headers=self.headers,
                    params=params
                )

                response.raise_for_status()
                data = response.json()

                replies = data.get('tweets', [])

                if not replies:
                    break

                all_replies.extend(replies)
                cursor = data.get('cursor')

                if not cursor:
                    break

                time.sleep(0.5)

            except Exception as e:
                print(f"Error obteniendo respuestas del tweet {tweet_id}: {e}")
                break

        return all_replies

    def download_full_conversation(self, query, mode='latest', max_tweets=None, include_replies=True, is_hashtag=True, until_date=None, since_date=None):
        """
        Descarga la conversación completa incluyendo respuestas

        Args:
            query: El término a buscar (hashtag o texto)
            mode: Modo de búsqueda
            max_tweets: Número máximo de tweets principales (None = todos disponibles)
            include_replies: Si incluir las respuestas de cada tweet
            is_hashtag: Si True, trata como hashtag. Si False, como texto libre
            until_date: Fecha límite superior (más reciente) - formato: YYYY-MM-DD
            since_date: Fecha límite inferior (más antigua) - formato: YYYY-MM-DD

        Returns:
            Diccionario con tweets y respuestas
        """
        # Buscar tweets principales
        main_tweets = self.search_tweets(query, mode, max_tweets, is_hashtag, until_date, since_date)

        conversation = {
            'query': query,
            'search_type': 'hashtag' if is_hashtag else 'text',
            'mode': mode,
            'downloaded_at': datetime.now().isoformat(),
            'total_main_tweets': len(main_tweets),
            'tweets': []
        }

        # Obtener respuestas si se solicita
        if include_replies:
            print("\n" + "=" * 50)
            print("Descargando respuestas...")
            print("=" * 50)

            for i, tweet in enumerate(main_tweets, 1):
                tweet_data = {
                    'tweet': tweet,
                    'replies': []
                }

                # Obtener respuestas
                tweet_id = tweet.get('id')
                if tweet_id:
                    print(f"\nTweet {i}/{len(main_tweets)} - ID: {tweet_id}")
                    replies = self.get_tweet_replies(tweet_id)
                    tweet_data['replies'] = replies
                    print(f"  Respuestas encontradas: {len(replies)}")

                conversation['tweets'].append(tweet_data)
        else:
            conversation['tweets'] = [{'tweet': tweet, 'replies': []} for tweet in main_tweets]

        # Calcular estadísticas
        total_replies = sum(len(t['replies']) for t in conversation['tweets'])
        conversation['total_replies'] = total_replies
        conversation['total_items'] = len(main_tweets) + total_replies

        return conversation

    def save_to_json(self, data, filename=None):
        """
        Guarda los datos en un archivo JSON

        Args:
            data: Datos a guardar
            filename: Nombre del archivo (opcional)
        """
        # Crear carpeta scraping si no existe
        scraping_dir = 'scraping'
        if not os.path.exists(scraping_dir):
            os.makedirs(scraping_dir)

        if not filename:
            query = data['query'].replace('#', '').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{query}_{timestamp}.json"

        # Guardar en la carpeta scraping
        filepath = os.path.join(scraping_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Datos guardados en: {filepath}")
        return filepath

    def export_to_csv(self, data, csv_filename=None):
        """
        Exporta los datos a formato CSV

        Args:
            data: Diccionario con los datos
            csv_filename: Nombre del archivo CSV (opcional)
        """
        try:
            import csv

            scraping_dir = 'scraping'
            if not csv_filename:
                query = data['query'].replace('#', '').replace(' ', '_')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                csv_filename = f"{query}_{timestamp}.csv"

            csv_filepath = os.path.join(scraping_dir, csv_filename)

            # Preparar datos para CSV
            rows = []
            for item in data['tweets']:
                tweet = item['tweet']
                rows.append({
                    'id': tweet.get('id', ''),
                    'fecha': tweet.get('time_parsed', ''),
                    'usuario': tweet.get('username', ''),
                    'nombre': tweet.get('name', ''),
                    'texto': tweet.get('text', ''),
                    'likes': tweet.get('likes', 0),
                    'retweets': tweet.get('retweets', 0),
                    'respuestas': tweet.get('replies', 0),
                    'vistas': tweet.get('views', 0),
                    'es_verificado': tweet.get('is_verified', False),
                    'url': tweet.get('permanent_url', ''),
                    'hashtags': ','.join(tweet.get('hashtags', [])) if tweet.get('hashtags') else '',
                    'num_respuestas_descargadas': len(item.get('replies', []))
                })

            # Escribir CSV
            if rows:
                with open(csv_filepath, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)

                print(f"✓ CSV exportado en: {csv_filepath}")
                return csv_filepath
            else:
                print("⚠️  No hay datos para exportar a CSV")
                return None

        except Exception as e:
            print(f"❌ Error al exportar CSV: {e}")
            return None

    def apply_filters(self, data, min_likes=None, verified_only=False):
        """
        Aplica filtros a los tweets

        Args:
            data: Diccionario con los tweets
            min_likes: Mínimo de likes requeridos
            verified_only: Solo usuarios verificados

        Returns:
            Diccionario filtrado
        """
        original_count = len(data['tweets'])
        filtered_tweets = []

        for item in data['tweets']:
            tweet = item['tweet']

            # Filtro por likes
            if min_likes is not None and tweet.get('likes', 0) < min_likes:
                continue

            # Filtro por verificados
            if verified_only:
                is_verified = tweet.get('is_verified', False) or tweet.get('is_blue_verified', False)
                if not is_verified:
                    continue

            filtered_tweets.append(item)

        data['tweets'] = filtered_tweets
        data['total_main_tweets'] = len(filtered_tweets)
        data['total_items'] = len(filtered_tweets) + sum(len(t['replies']) for t in filtered_tweets)

        filtered_count = len(filtered_tweets)
        print(f"\n✓ Filtros aplicados: {original_count} tweets → {filtered_count} tweets")

        return data


def main():
    """Función principal"""
    scraper = TwitterHashtagScraper()

    # Configuración
    print("\n" + "=" * 70)
    print("TÉRMINOS DE BÚSQUEDA")
    print("=" * 70)
    print("Puedes buscar uno o varios términos:")
    print("- Un término: Python")
    print("- Varios términos separados por comas: Python, JavaScript, AI")
    print()

    query_input = input("Ingresa el/los término(s) a buscar: ").strip()

    # Separar múltiples términos por comas
    queries = [q.strip() for q in query_input.split(',') if q.strip()]

    if len(queries) == 0:
        print("❌ Error: Debes ingresar al menos un término de búsqueda")
        return

    if len(queries) > 1:
        print(f"\n✓ Se buscarán {len(queries)} términos: {', '.join(queries)}")
    else:
        query = queries[0]

    print("\n" + "=" * 70)
    print("TIPO DE BÚSQUEDA")
    print("=" * 70)
    print("1. Hashtag - Agrega # automáticamente (ej: Python → #Python)")
    print("2. Texto libre - Busca nombre, frase o palabra (ej: Elon Musk)")

    search_type = input("\nSelecciona el tipo (1-2, default=1): ").strip()
    is_hashtag = search_type != '2'

    print("\n" + "=" * 70)
    print("MODO DE BÚSQUEDA")
    print("=" * 70)
    print("1. Latest (Más recientes)")
    print("   → Tweets ordenados por fecha, del más nuevo al más antiguo")
    print("   → Útil para ver las últimas publicaciones sobre un tema")
    print()
    print("2. Top (Más populares)")
    print("   → Tweets con más likes, retweets y engagement")
    print("   → Útil para ver el contenido más viral o relevante")
    print()
    print("3. Photos (Solo fotos)")
    print("   → Solo tweets que contienen imágenes")
    print("   → Útil para análisis visual o recopilación de imágenes")
    print()
    print("4. Videos (Solo videos)")
    print("   → Solo tweets que contienen videos")
    print("   → Útil para recopilar contenido multimedia")

    mode_choice = input("\nSelecciona el modo (1-4, default=1): ").strip()
    mode_map = {'1': 'latest', '2': 'top', '3': 'photos', '4': 'videos'}
    mode = mode_map.get(mode_choice, 'latest')

    print("\n" + "=" * 70)
    max_tweets_input = input("¿Cuántos tweets descargar? (Enter = todos disponibles): ").strip()
    max_tweets = int(max_tweets_input) if max_tweets_input else None

    # Pregunta de rango de fechas
    date_range_input = input("¿Filtrar por rango de fechas? (s/n, default=n): ").strip().lower()

    until_date = None
    since_date = None

    if date_range_input == 's':
        print("\n   Configura el rango de fechas (formato DD-MM-YYYY)")
        print("   Puedes especificar solo una fecha o ambas:")

        since_date_input = input("   - Desde (fecha más antigua): ").strip()
        until_date_input = input("   - Hasta (fecha más reciente): ").strip()

        # Convertir since_date de DD-MM-YYYY a YYYY-MM-DD
        if since_date_input:
            try:
                day, month, year = since_date_input.split('-')
                since_date = f"{year}-{month}-{day}"
            except:
                print("   ⚠️  Formato de fecha 'desde' incorrecto, se ignorará")
                since_date = None

        # Convertir until_date de DD-MM-YYYY a YYYY-MM-DD
        if until_date_input:
            try:
                day, month, year = until_date_input.split('-')
                until_date = f"{year}-{month}-{day}"
            except:
                print("   ⚠️  Formato de fecha 'hasta' incorrecto, se ignorará")
                until_date = None

    include_replies_input = input("\n¿Incluir respuestas? (s/n, default=s): ").strip().lower()
    include_replies = include_replies_input != 'n'

    # Opciones avanzadas
    print("\n" + "=" * 70)
    advanced_input = input("¿Configurar opciones avanzadas? (s/n, default=n): ").strip().lower()

    # Variables para opciones avanzadas
    export_csv = False
    min_likes = None
    verified_only = False
    monitor_mode = False
    monitor_duration = None

    if advanced_input == 's':
        print("\n" + "=" * 70)
        print("OPCIONES AVANZADAS")
        print("=" * 70)

        # Exportar a CSV
        csv_input = input("\n¿Exportar también a CSV? (s/n, default=n): ").strip().lower()
        export_csv = csv_input == 's'

        # Filtro por likes
        min_likes_input = input("Filtrar tweets con mínimo de likes (Enter = sin filtro): ").strip()
        min_likes = None
        if min_likes_input and min_likes_input.isdigit():
            min_likes = int(min_likes_input)

        # Filtro por verificados
        verified_input = input("¿Solo usuarios verificados? (s/n, default=n): ").strip().lower()
        verified_only = verified_input == 's'

        # Modo monitoreo
        monitor_input = input("\n¿Activar modo monitoreo continuo? (s/n, default=n): ").strip().lower()
        monitor_mode = monitor_input == 's'

        if monitor_mode:
            print("\nDuración del monitoreo:")
            print("1. 10 horas")
            print("2. 24 horas")
            print("3. 2 días")
            print("4. Hasta detenerlo manualmente (Ctrl+C)")

            duration_choice = input("\nSelecciona duración (1-4, default=4): ").strip()
            duration_map = {
                '1': 10 * 3600,      # 10 horas en segundos
                '2': 24 * 3600,      # 24 horas
                '3': 2 * 24 * 3600,  # 2 días
                '4': None            # Indefinido
            }
            monitor_duration = duration_map.get(duration_choice, None)

            interval_input = input("Intervalo entre búsquedas en minutos (default=5): ").strip()
            monitor_interval = int(interval_input) * 60 if interval_input else 300  # 5 minutos por defecto

    print("\n" + "=" * 50)
    print("Iniciando descarga...")
    print("=" * 50)

    # Configurar manejador de señales para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Procesar múltiples búsquedas si hay varios términos
    if len(queries) > 1:
        print("\n" + "=" * 70)
        print(f"PROCESANDO {len(queries)} BÚSQUEDAS")
        print("=" * 70)

        all_results = []

        for idx, query in enumerate(queries, 1):
            print(f"\n{'=' * 70}")
            print(f"BÚSQUEDA {idx}/{len(queries)}: {query}")
            print(f"{'=' * 70}")

            # Modo monitoreo no compatible con múltiples términos
            if monitor_mode:
                print("⚠️  Modo monitoreo no disponible con múltiples términos")
                print("   Usando modo de búsqueda única...")

            conversation = scraper.download_full_conversation(
                query=query,
                mode=mode,
                max_tweets=max_tweets,
                include_replies=include_replies,
                is_hashtag=is_hashtag,
                until_date=until_date,
                since_date=since_date
            )

            # Aplicar filtros si están configurados
            if min_likes or verified_only:
                conversation = scraper.apply_filters(conversation, min_likes, verified_only)

            # Guardar resultados
            filename = scraper.save_to_json(conversation)

            # Exportar a CSV si está activado
            if export_csv:
                scraper.export_to_csv(conversation)

            all_results.append({
                'query': query,
                'tweets': conversation['total_main_tweets'],
                'replies': conversation['total_replies'],
                'file': filename
            })

            print(f"✓ Completado: {conversation['total_main_tweets']} tweets, {conversation['total_replies']} respuestas")

        # Resumen final de todas las búsquedas
        print("\n" + "=" * 70)
        print("RESUMEN GENERAL")
        print("=" * 70)

        total_tweets = sum(r['tweets'] for r in all_results)
        total_replies = sum(r['replies'] for r in all_results)

        for idx, result in enumerate(all_results, 1):
            print(f"\n{idx}. {result['query']}")
            print(f"   Tweets: {result['tweets']}")
            print(f"   Respuestas: {result['replies']}")
            print(f"   Archivo: {result['file']}")

        print(f"\n{'=' * 70}")
        print(f"TOTAL: {total_tweets} tweets, {total_replies} respuestas")
        print(f"Archivos generados: {len(all_results)}")
        print("=" * 70)

        return

    # Procesar búsqueda única
    query = queries[0]

    # Modo monitoreo
    if monitor_mode:
        print("\n" + "=" * 70)
        print("MODO MONITOREO ACTIVADO")
        print("=" * 70)
        if monitor_duration:
            hours = monitor_duration / 3600
            print(f"Duración: {hours} horas")
        else:
            print("Duración: Hasta detenerlo manualmente (Ctrl+C)")
        print(f"Intervalo: {monitor_interval / 60} minutos")
        print("=" * 70)

        start_time = time.time()
        iteration = 0
        all_tweet_ids = set()  # Para detectar duplicados

        while not interrupted:
            iteration += 1
            current_time = time.time()

            # Verificar si se alcanzó el límite de tiempo
            if monitor_duration and (current_time - start_time) >= monitor_duration:
                print(f"\n✓ Tiempo de monitoreo completado ({monitor_duration / 3600} horas)")
                break

            print(f"\n{'=' * 70}")
            print(f"ITERACIÓN {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'=' * 70}")

            # Descargar conversación
            conversation = scraper.download_full_conversation(
                query=query,
                mode=mode,
                max_tweets=max_tweets,
                include_replies=include_replies,
                is_hashtag=is_hashtag,
                until_date=until_date,
                since_date=since_date
            )

            # Aplicar filtros si están configurados
            if min_likes or verified_only:
                conversation = scraper.apply_filters(conversation, min_likes, verified_only)

            # Detectar tweets nuevos
            new_tweets = 0
            for item in conversation['tweets']:
                tweet_id = item['tweet'].get('id')
                if tweet_id and tweet_id not in all_tweet_ids:
                    all_tweet_ids.add(tweet_id)
                    new_tweets += 1

            print(f"\n✓ Tweets nuevos en esta iteración: {new_tweets}")
            print(f"✓ Total de tweets únicos monitorizados: {len(all_tweet_ids)}")

            # Guardar resultados
            filename = scraper.save_to_json(conversation)

            # Exportar a CSV si está activado
            if export_csv:
                scraper.export_to_csv(conversation)

            # Esperar hasta la próxima iteración
            if not interrupted:
                print(f"\n⏳ Esperando {monitor_interval / 60} minutos hasta la próxima búsqueda...")
                print("   (Presiona Ctrl+C para detener)")

                # Esperar por intervalos de 1 segundo para poder interrumpir rápido
                for _ in range(monitor_interval):
                    if interrupted:
                        break
                    time.sleep(1)

        print("\n" + "=" * 70)
        print("MONITOREO FINALIZADO")
        print("=" * 70)
        print(f"Iteraciones completadas: {iteration}")
        print(f"Tweets únicos monitorizados: {len(all_tweet_ids)}")
        print("=" * 70)

    else:
        # Modo normal (una sola extracción)
        conversation = scraper.download_full_conversation(
            query=query,
            mode=mode,
            max_tweets=max_tweets,
            include_replies=include_replies,
            is_hashtag=is_hashtag,
            until_date=until_date,
            since_date=since_date
        )

        # Aplicar filtros si están configurados
        if min_likes or verified_only:
            conversation = scraper.apply_filters(conversation, min_likes, verified_only)

        # Guardar resultados
        filename = scraper.save_to_json(conversation)

        # Exportar a CSV si está activado
        if export_csv:
            scraper.export_to_csv(conversation)

        # Mostrar resumen
        print("\n" + "=" * 50)
        print("RESUMEN")
        print("=" * 50)
        print(f"Búsqueda: {conversation['query']}")
        print(f"Tipo: {conversation['search_type']}")
        print(f"Tweets principales: {conversation['total_main_tweets']}")
        print(f"Total de respuestas: {conversation['total_replies']}")
        print(f"Total de elementos: {conversation['total_items']}")
        print(f"Archivo JSON: {filename}")
        print("=" * 50)


if __name__ == '__main__':
    main()
