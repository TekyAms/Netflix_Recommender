# Netflix Recommender System

Système de recommandation de films et séries Netflix basé sur la similarité de contenu (Content-Based Filtering) utilisant le NLP.

## Objectif

Recommander des films et séries similaires à partir d'un titre — comme Netflix "Parce que vous avez regardé..."

## Technique utilisée

- **TF-IDF Vectorization** — transforme le texte en vecteurs numériques
- **Cosine Similarity** — calcule la similarité entre les titres
- **difflib** — gère les fautes de frappe
- **TMDB API** — récupère les affiches des films

## Stack technique

- Python
- Pandas, NumPy
- Scikit-learn
- Streamlit
- TMDB API

## Structure du projet
netflix-recommender/
├── netflix_titles.csv    # Dataset Netflix (Kaggle)
├── recommender.py        # Logique NLP et recommandations
├── tmdb.py              # Récupération des affiches via TMDB
├── streamlit_app.py     # Interface utilisateur Streamlit
├── notebook.ipynb       # Exploration et visualisations
└── README.md

## Installation

```bash
pip install streamlit pandas numpy scikit-learn requests
```

## Lancer l'application

```bash
streamlit run streamlit_app.py
```

## Dataset

Dataset Netflix disponible sur Kaggle :
👉 [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)

## Fonctionnalités

- Recherche par titre (partielle ou complète)
- Filtrage par type (Film ou Série)
- Correction automatique des fautes de frappe
- Affiches des films via TMDB API
- Choix du nombre de recommandations (5, 10, 15)

## Démo en ligne

👉 [Voir l'application](https://tekyamsnetflixrecommender.streamlit.app/)

## 👩🏾‍💻 Auteure

**Tèkiyath Amoussa**
Ingénieure Data & IA | Dakar, Sénégal 
[LinkedIn](https://www.linkedin.com/in/t%C3%A8kiyath-amoussa-506918274/) | [GitHub](https://github.com/TekyAms)
