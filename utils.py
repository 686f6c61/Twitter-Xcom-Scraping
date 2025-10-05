"""
Utilidades para análisis de datos extraídos de Twitter/X
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from collections import Counter


def load_conversation(filepath: str) -> Dict:
    """
    Carga una conversación desde un archivo JSON
    
    Args:
        filepath: Ruta al archivo JSON
        
    Returns:
        Diccionario con la conversación
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_conversation(conversation: Dict) -> Dict:
    """
    Analiza una conversación y retorna estadísticas
    
    Args:
        conversation: Diccionario con la conversación
        
    Returns:
        Diccionario con estadísticas
    """
    stats = {
        "total_replies": len(conversation.get("replies", [])),
        "main_tweet_text_length": len(conversation.get("main_tweet", {}).get("text", "")),
        "main_tweet_likes": conversation.get("main_tweet", {}).get("like_count", "0"),
        "main_tweet_retweets": conversation.get("main_tweet", {}).get("retweet_count", "0"),
        "unique_repliers": len(set(r.get("username", "") for r in conversation.get("replies", []))),
        "avg_reply_length": 0,
        "most_active_replier": None
    }
    
    # Calcular longitud promedio de respuestas
    if stats["total_replies"] > 0:
        reply_lengths = [len(r.get("text", "")) for r in conversation.get("replies", [])]
        stats["avg_reply_length"] = sum(reply_lengths) / len(reply_lengths)
        
        # Encontrar usuario más activo en respuestas
        usernames = [r.get("username", "") for r in conversation.get("replies", [])]
        if usernames:
            username_counts = Counter(usernames)
            stats["most_active_replier"] = username_counts.most_common(1)[0]
    
    return stats


def export_to_csv(conversations: List[Dict], output_file: str):
    """
    Exporta conversaciones a formato CSV
    
    Args:
        conversations: Lista de conversaciones
        output_file: Archivo de salida CSV
    """
    import csv
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Escribir encabezados
        writer.writerow([
            'Tweet URL', 'Main Tweet Username', 'Main Tweet Text', 
            'Main Tweet Timestamp', 'Likes', 'Retweets', 'Replies Count',
            'Reply Username', 'Reply Text', 'Reply Timestamp'
        ])
        
        # Escribir datos
        for conv in conversations:
            main_tweet = conv.get("main_tweet", {})
            
            # Si no hay respuestas, escribir solo el tweet principal
            if not conv.get("replies"):
                writer.writerow([
                    conv.get("tweet_url", ""),
                    main_tweet.get("username", ""),
                    main_tweet.get("text", ""),
                    main_tweet.get("timestamp", ""),
                    main_tweet.get("like_count", "0"),
                    main_tweet.get("retweet_count", "0"),
                    main_tweet.get("reply_count", "0"),
                    "", "", ""
                ])
            else:
                # Escribir una fila por cada respuesta
                for reply in conv.get("replies", []):
                    writer.writerow([
                        conv.get("tweet_url", ""),
                        main_tweet.get("username", ""),
                        main_tweet.get("text", ""),
                        main_tweet.get("timestamp", ""),
                        main_tweet.get("like_count", "0"),
                        main_tweet.get("retweet_count", "0"),
                        main_tweet.get("reply_count", "0"),
                        reply.get("username", ""),
                        reply.get("text", ""),
                        reply.get("timestamp", "")
                    ])


def print_conversation_summary(conversation: Dict):
    """
    Imprime un resumen legible de una conversación
    
    Args:
        conversation: Diccionario con la conversación
    """
    print("\n" + "=" * 80)
    print("RESUMEN DE CONVERSACIÓN")
    print("=" * 80)
    
    main_tweet = conversation.get("main_tweet", {})
    print(f"\nTweet Principal:")
    print(f"  Usuario: {main_tweet.get('username', 'N/A')}")
    print(f"  Fecha: {main_tweet.get('timestamp', 'N/A')}")
    print(f"  Texto: {main_tweet.get('text', 'N/A')[:200]}...")
    print(f"  Estadísticas: {main_tweet.get('like_count', '0')} likes, "
          f"{main_tweet.get('retweet_count', '0')} RTs, "
          f"{main_tweet.get('reply_count', '0')} respuestas")
    
    replies = conversation.get("replies", [])
    print(f"\nRespuestas encontradas: {len(replies)}")
    
    if replies:
        print("\nPrimeras 3 respuestas:")
        for i, reply in enumerate(replies[:3], 1):
            print(f"\n  {i}. {reply.get('username', 'N/A')}")
            print(f"     {reply.get('text', 'N/A')[:150]}...")
            print(f"     {reply.get('like_count', '0')} likes")
    
    # Estadísticas
    stats = analyze_conversation(conversation)
    print("\nEstadísticas:")
    print(f"  - Total de respuestas: {stats['total_replies']}")
    print(f"  - Usuarios únicos: {stats['unique_repliers']}")
    print(f"  - Longitud promedio de respuesta: {stats['avg_reply_length']:.1f} caracteres")
    if stats['most_active_replier']:
        print(f"  - Usuario más activo: {stats['most_active_replier'][0]} ({stats['most_active_replier'][1]} respuestas)")
    
    print("=" * 80 + "\n")


def main():
    """Función de ejemplo para usar las utilidades"""
    # Ejemplo: cargar y analizar conversación
    example_file = "data/conversation_20240115_143000.json"
    
    if os.path.exists(example_file):
        conversation = load_conversation(example_file)
        print_conversation_summary(conversation)
        
        stats = analyze_conversation(conversation)
        print("Estadísticas detalladas:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print(f"Archivo de ejemplo no encontrado: {example_file}")
        print("Ejecuta primero el scraper para generar datos.")


if __name__ == "__main__":
    main()
