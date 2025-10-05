#!/bin/bash
echo "Pega tu nueva API key de RapidAPI:"
read NEW_KEY
echo "RAPIDAPI_KEY=$NEW_KEY" > /home/r/Escritorio/Xcom/.env
echo "RAPIDAPI_HOST=twitter-api45.p.rapidapi.com" >> /home/r/Escritorio/Xcom/.env
echo "✓ API key actualizada en .env"
