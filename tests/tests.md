# Tests de Integración - Twitter/X Scraper

## Descripción

Tests de integración **reales** que validan todas las funcionalidades del scraper usando la API de Twitter/X.

**⚠️ IMPORTANTE**: Estos tests consumen requests de tu cuenta de RapidAPI. Ejecutar con moderación.

## Configuración

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales en .env
RAPIDAPI_KEY=tu_api_key
RAPIDAPI_HOST=easy-x-com-twitter-api.p.rapidapi.com

# Ejecutar tests
python -m pytest tests/test_integration_real.py -v --cov=download_hashtag --cov-report=term-missing
```

## Tests Implementados (14 tests)

### 1. `test_01_search_tweets_hashtag_real`
**Funcionalidad**: Búsqueda básica por hashtag  
**Requests**: 1  
**Verifica**:
- Búsqueda de #Python en modo latest
- Retorna al menos 1 tweet
- Cada tweet tiene campos requeridos (id, text, username, time_parsed)

### 2. `test_02_search_tweets_text_real`
**Funcionalidad**: Búsqueda por texto libre  
**Requests**: 1  
**Verifica**:
- Búsqueda de "Elon Musk" como texto
- Retorna tweets relacionados
- No agrega # al query

### 3. `test_03_search_modes_real`
**Funcionalidad**: Múltiples modos de búsqueda  
**Requests**: 4 (latest, top, photos, videos)  
**Verifica**:
- Modo latest: tweets cronológicos
- Modo top: tweets populares
- Modo photos: solo con imágenes
- Modo videos: solo con videos
- Cada modo retorna datos válidos

### 4. `test_04_get_replies_real`
**Funcionalidad**: Extracción de respuestas  
**Requests**: 2 (buscar tweet + obtener respuestas)  
**Verifica**:
- Encuentra tweet con ID válido
- Obtiene sus respuestas (si existen)
- Respuestas tienen estructura correcta

### 5. `test_05_download_full_conversation_real`
**Funcionalidad**: Descarga completa (tweets + respuestas)  
**Requests**: Variable (~3-5)  
**Verifica**:
- Descarga tweets principales
- Incluye respuestas de cada tweet
- Genera estructura JSON completa
- Calcula estadísticas correctas

### 6. `test_06_max_tweets_limit_real`
**Funcionalidad**: Límite de tweets  
**Requests**: 1  
**Verifica**:
- Respeta max_tweets=5
- No descarga más del límite
- Retorna exactamente la cantidad solicitada

### 7. `test_07_save_to_json_real`
**Funcionalidad**: Guardado en JSON  
**Requests**: 1  
**Verifica**:
- Crea archivo JSON válido
- Guarda en carpeta scraping/
- Contenido es válido y parseable
- Estructura de datos correcta

### 8. `test_08_export_to_csv_real`
**Funcionalidad**: Exportación a CSV  
**Requests**: 1  
**Verifica**:
- Genera archivo CSV con UTF-8-BOM
- Columnas correctas (id, fecha, usuario, texto, etc.)
- Compatible con Excel
- Número de filas = número de tweets

### 9. `test_09_filter_by_likes_real`
**Funcionalidad**: Filtro por likes mínimos  
**Requests**: 1  
**Verifica**:
- Filtra tweets con min_likes=5
- Solo retorna tweets que cumplen el mínimo
- No altera tweets originales

### 10. `test_10_filter_verified_real`
**Funcionalidad**: Filtro por usuarios verificados  
**Requests**: 1  
**Verifica**:
- Filtra solo usuarios verificados
- Verifica insignia azul o legacy verified
- Cantidad filtrada ≤ cantidad original

### 11. `test_11_pagination_real`
**Funcionalidad**: Paginación automática  
**Requests**: 2 (25 tweets requiere 2 páginas)  
**Verifica**:
- Obtiene más de 20 tweets (fuerza paginación)
- No hay IDs duplicados
- Cursor funciona correctamente

### 12. `test_12_complete_workflow_real`
**Funcionalidad**: Flujo completo end-to-end  
**Requests**: 1  
**Verifica**:
- Búsqueda → JSON → CSV
- Cada paso se ejecuta correctamente
- Archivos generados existen y son válidos

### 13. `test_13_incremental_save_real` (NUEVO en v0.3)
**Funcionalidad**: Guardado incremental  
**Requests**: 1  
**Verifica**:
- Guarda progresivamente durante descarga
- Marca `incremental_saved: true`
- Status es `completed` al finalizar
- Incluye `_saved_filename`

### 14. `test_14_date_range_filter_real` (NUEVO en v0.2)
**Funcionalidad**: Filtro por rango de fechas  
**Requests**: 1  
**Verifica**:
- Filtra tweets entre since_date y until_date
- Tweets están dentro del rango especificado
- Formato YYYY-MM-DD funciona correctamente

## Resumen de Consumo de API

| Test | Requests | Descripción |
|------|----------|-------------|
| test_01 | 1 | Búsqueda hashtag |
| test_02 | 1 | Búsqueda texto |
| test_03 | 4 | 4 modos diferentes |
| test_04 | 2 | Tweet + respuestas |
| test_05 | ~5 | Full conversation |
| test_06 | 1 | Límite tweets |
| test_07 | 1 | Guardar JSON |
| test_08 | 1 | Exportar CSV |
| test_09 | 1 | Filtro likes |
| test_10 | 1 | Filtro verificados |
| test_11 | 2 | Paginación |
| test_12 | 1 | Workflow completo |
| test_13 | 1 | Guardado incremental |
| test_14 | 1 | Filtro fechas |
| **TOTAL** | **~23** | **requests aprox.** |

## Cobertura

- ✅ **100% cobertura** de funcionalidades principales
- ✅ Todas las features de v0.1 a v0.4
- ✅ Tests con datos reales de la API
- ✅ Sin mocks ni simulaciones

## Ejecución

### Todos los tests
```bash
python -m pytest tests/test_integration_real.py -v
```

### Test específico
```bash
python -m pytest tests/test_integration_real.py::TestRealAPIIntegration::test_13_incremental_save_real -v
```

### Con cobertura
```bash
python -m pytest tests/test_integration_real.py -v --cov=download_hashtag --cov-report=term-missing
```

## Resultados Esperados

```
=============== test session starts ================
tests/test_integration_real.py::TestRealAPIIntegration::test_01_search_tweets_hashtag_real PASSED     [ 7%]
tests/test_integration_real.py::TestRealAPIIntegration::test_02_search_tweets_text_real PASSED        [14%]
tests/test_integration_real.py::TestRealAPIIntegration::test_03_search_modes_real PASSED              [21%]
tests/test_integration_real.py::TestRealAPIIntegration::test_04_get_replies_real PASSED               [28%]
tests/test_integration_real.py::TestRealAPIIntegration::test_05_download_full_conversation_real PASSED[35%]
tests/test_integration_real.py::TestRealAPIIntegration::test_06_max_tweets_limit_real PASSED          [42%]
tests/test_integration_real.py::TestRealAPIIntegration::test_07_save_to_json_real PASSED              [50%]
tests/test_integration_real.py::TestRealAPIIntegration::test_08_export_to_csv_real PASSED             [57%]
tests/test_integration_real.py::TestRealAPIIntegration::test_09_filter_by_likes_real PASSED           [64%]
tests/test_integration_real.py::TestRealAPIIntegration::test_10_filter_verified_real PASSED           [71%]
tests/test_integration_real.py::TestRealAPIIntegration::test_11_pagination_real PASSED                [78%]
tests/test_integration_real.py::TestRealAPIIntegration::test_12_complete_workflow_real PASSED         [85%]
tests/test_integration_real.py::TestRealAPIIntegration::test_13_incremental_save_real PASSED          [92%]
tests/test_integration_real.py::TestRealAPIIntegration::test_14_date_range_filter_real PASSED         [100%]

=============== 14 passed in 45.23s ================
```

## Notas

- Tests ordenados numéricamente para ejecución secuencial
- Cada test es independiente
- Se usa directorio temporal para no contaminar archivos
- Limpieza automática después de cada test
- Compatible con CI/CD (si hay credenciales configuradas)
