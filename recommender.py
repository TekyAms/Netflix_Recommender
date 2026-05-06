import pandas as pd # pour manipuler les données sous forme de tableaux
import re # pour nettoyer du texte et les caractères spéciaux
import difflib # gère les fautes de frappe
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer # pour convertir du texte en vecteurs numériques
from sklearn.metrics.pairwise import cosine_similarity # pour calculer la similarité entre les vecteurs de texte

# Variables globales
df = None
tfidf = None
cosine_sim = None
indices = None
data_path = None


def ensure_model_ready(csv_path="netflix_titles.csv"):
    global df, tfidf, cosine_sim, indices

    if df is None or tfidf is None or cosine_sim is None or indices is None:
        init(csv_path)

def load_data(csv_path):
    global df, data_path

    path = Path(csv_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path

    data_path = path
    df = pd.read_csv(path)
    print(f"Dataset chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")

def explore_data():
    ensure_model_ready()
    print("=== Exploration du dataset ===")
    print(f"Nombre de titres : {df.shape[0]}")
    print(f"Nombre de colonnes : {df.shape[1]}")
    print(f"\nValeurs manquantes :")
    print(df.isnull().sum())
    print(f"\nRépartition Films/Séries :")
    print(df['type'].value_counts())

def clean_data():
    global df

    # Nettoyer la colonne type
    df['type'] = df['type'].str.strip()
    
    # Colonnes à nettoyer
    cols = ['title', 'listed_in', 'description', 'director', 'cast']
    
    # Remplir les valeurs manquantes
    for col in cols:
        df[col] = df[col].fillna('')
    
    # Créer des colonnes nettoyées pour le NLP (on garde les originales pour l'affichage)
    for col in cols:
        df[col + '_clean'] = df[col].str.lower()
        df[col + '_clean'] = df[col + '_clean'].apply(lambda x: re.sub(r'[^a-z0-9\s]', '', x))
    #On crée des colonnes nettoyées (title_clean, description_clean...) uniquement pour le NLP, on garde les colonnes originales pour l'affichage   
    print("Nettoyage terminé ")

def create_features():
    global df
    
    # Combiner toutes les colonnes nettoyées en une seule
    df['features'] = (
        df['title_clean'] + ' ' +
        df['listed_in_clean'] + ' ' +
        df['description_clean'] + ' ' +
        df['director_clean'] + ' ' +
        df['cast_clean']
    )
    
    print("Features créées ")
    print(f"Exemple : {df['features'][0][:100]}...") # Affiche les 100 premiers caractères du premier film (index 0) pour vérifier

def vectorize():
    global df, tfidf, cosine_sim, indices
    
    # Initialiser le vectoriseur TF-IDF
    tfidf = TfidfVectorizer(stop_words='english') # On ignore les mots courants en anglais (the, and, is, a etc.) pour se concentrer sur les mots importants
    
    # Transformer le texte en matrice de vecteurs
    tfidf_matrix = tfidf.fit_transform(df['features']) # On applique le TF-IDF sur la colonne 'features' qui contient le texte combiné de tous les champs nettoyés
    
    print(f"Matrice TF-IDF : {tfidf_matrix.shape}")
    
    # Calculer la similarité entre tous les titres
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix) # On calcule la similarité cosinus entre tous les titres, ce qui nous donnera une matrice de similarité où chaque élément (i, j) représente la similarité entre le titre i et le titre j
    
    # Créer un mapping titre → index
    indices = pd.Series(df.index, index=df['title_clean']).drop_duplicates() # On crée une série pandas qui mappe chaque titre nettoyé à son index dans le DataFrame, ce qui nous permettra de retrouver facilement l'index d'un titre donné pour faire des recommandations
    
    print("Vectorisation terminée")


def correct_typo(title):
    ensure_model_ready()

    # Récupère tous les titres nettoyés du dataset
    all_titles = df['title_clean'].unique() 
    
    # Cherche le titre le plus similaire
    matches = difflib.get_close_matches(title, all_titles, n=1, cutoff=0.6) #  title le titre saisi par l'utilisateur, all_tilte la liste de tous les titres à comparer  n=1 signifie qu'on veut la meilleure correspondance, cutoff=0.6 signifie que la correspondance doit être d'au moins 60% pour être considérée comme valide
    
    if matches:
        return matches[0]
    return None

def get_recommendations(title, top_n=5, content_type=None):
    
    # Garder le titre original pour l'affichage
    original_title = title
    
    # Nettoyer le titre saisi (comme on a nettoyé le dataset)
    title_clean = title.lower() # On met le titre en minuscules pour correspondre au format de nos titres nettoyés
    title_clean = re.sub(r'[^a-z0-9\s]', '', title_clean) # On enlève les caractères spéciaux pour correspondre au format de nos titres nettoyés

    # Chercher correspondance exacte d'abord
    matches = df[df['title_clean'] == title_clean]
    
    # Si aucune correspondance exacte on cherche une sous-chaîne
    if matches.empty:
        matches = df[df['title_clean'].str.contains(title_clean, na=False)]
    
    # Si toujours rien on essaie de corriger la faute de frappe
    if matches.empty:
        corrected = correct_typo(title_clean)
        
        if corrected:
            # Titre corrigé trouvé on récupère le titre original (non nettoyé) pour l'affichage
            suggestion = df[df['title_clean'] == corrected]['title'].values[0]
            matches = df[df['title_clean'] == corrected]
            correction_message = f"'{original_title}' non trouvé. Résultats pour : '{suggestion}'"
        else:
            # Rien trouvé du tout
            return {
                'error': f"Titre '{original_title}' non trouvé. Vérifiez l'orthographe."
            }
    else:
        correction_message = None

    # Filtrer par type pour le titre de départ si spécifié
    if content_type:
        matches_filtered = matches[matches['type'] == content_type]
        if matches_filtered.empty:
            # Le titre existe mais pas dans ce type on continue quand même
            pass
        else:
            matches = matches_filtered
    
    # Index du premier titre correspondant — on prend le premier résultat trouvé
    idx = matches.index[0]
    
    # Calculer les scores de similarité — liste de tuples (index, score)
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Trier par ordre décroissant pour avoir les plus similaires en premier
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Exclure le titre lui-même (toujours en première position avec score 1.0)
    sim_scores = sim_scores[1:]

    # Filtrer les résultats par type si spécifié
    if content_type:
        sim_scores = [
            (i, score) for i, score in sim_scores
            if df.iloc[i]['type'] == content_type # On garde seulement les titres du type demandé
        ]
    
    # Prendre les top_n premiers
    sim_scores = sim_scores[:top_n]
    
    # Vérifier s'il y a des résultats après filtrage
    if not sim_scores:
        return {
            'error': f"Aucune recommandation trouvée pour '{original_title}' avec le type '{content_type}'."
        }
    
    # Récupérer les indices des films recommandés
    movie_indices = [i for i, score in sim_scores]
    
    # Récupérer les informations des films recommandés
    results = df.iloc[movie_indices][['title', 'type', 'listed_in', 'description']].copy()
    results = results.reset_index(drop=True)
    
    return {
        'results': results,
        'correction': correction_message # None si pas de correction, sinon le message de correction
    }

def fit(): # regroupe toutes les étapes de préparation en une seule fonction
    clean_data() # Nettoyage des données
    create_features() # Création de la colonne 'features' qui combine tous les champs de texte
    vectorize() # Vectorisation du texte et calcul de la matrice de similarité (TF-IDF + cosine similarity)
    print("Modèle prêt pour les recommandations !")


def init(csv_path): #  le point de départ de tout le projet qu'on appelera dans streamlit pour initialiser le modèle
    load_data(csv_path)
    fit()