import requests

# Ta clé API TMDB
TMDB_API_KEY = "753503821039499649ae0cc548b78790"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


def get_poster(title):
    """Récupère l'URL de l'affiche d'un film ou série via l'API TMDB."""
    try:
        # Rechercher le film sur TMDB
        response = requests.get(
            f"{TMDB_BASE_URL}/search/multi",
            params={
                "api_key": TMDB_API_KEY,
                "query": title,
                "language": "fr-FR"
            }
        )
        
        # Convertir la réponse en dictionnaire
        data = response.json()
        
        # Vérifier si des résultats ont été trouvés
        if data['results']:
            poster_path = data['results'][0].get('poster_path')
            
            if poster_path:
                return f"{TMDB_IMAGE_URL}{poster_path}"
        
        # Si aucune affiche trouvée
        return None
        
    except Exception:
        return None
