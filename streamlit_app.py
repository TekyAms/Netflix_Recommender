import streamlit as st
from recommender import init, get_recommendations
from tmdb import get_poster

# Configuration de la page
st.set_page_config(
    page_title="Netflix Recommender",
    page_icon="🎬",
    layout="wide"
)

# Style CSS inspiré Netflix
st.markdown("""
    <style>
        .stApp {
            background-color: #141414;
            color: white;
        }
        .titre-film {
            color: #E50914;
            font-size: 20px;
            font-weight: bold;
        }
        .info-film {
            color: #AAAAAA;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# Charger le modèle une seule fois
@st.cache_resource 
def load_model():
    init("netflix_titles.csv")
    return True

load_model()

# Titre principal
st.markdown("<h1 style='text-align:center; color:#E50914;'>🎬 Netflix Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#AAAAAA;'>Découvrez des films et séries similaires à ce que vous aimez</p>", unsafe_allow_html=True)

st.markdown("---")

# Formulaire de recherche
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    title = st.text_input("🔍 Entrez un titre", placeholder="Ex: Stranger Things, Money Heist...")

with col2:
    content_type = st.selectbox(
        "Type",
        options=["Tout", "Movie", "TV Show"],
        index=0
    )

with col3:
    top_n = st.selectbox(
        "Nombre de résultats",
        options=[5, 10, 15],
        index=0
    )

# Bouton recommander
search = st.button("🎬 Recommander", use_container_width=True)

# Afficher les résultats quand l'utilisateur clique
if search and title:
    
    # Convertir le type
    content_type_filter = None
    if content_type != "Tout":
        content_type_filter = content_type
    
    # Afficher un spinner pendant le chargement
    with st.spinner("Recherche en cours..."):
        data = get_recommendations(
            title, 
            top_n=top_n, 
            content_type=content_type_filter
        )
    
    # Si erreur
    if 'error' in data:
        st.error(data['error'])
    
    else:
        # Afficher le message de correction si faute de frappe
        if data['correction']:
            st.info(data['correction'])
        
        # Afficher le nombre de résultats
        results = data['results']
        st.success(f" {len(results)} recommandation(s) trouvée(s)")
        
        # Afficher les résultats en colonnes
        cols = st.columns(5)
        
        for i, row in results.iterrows():
            with cols[i % 5]:
                # Récupérer l'affiche
                poster = get_poster(row['title'])
                
                if poster:
                    st.image(poster, width="stretch")
                else:
                    st.image("https://via.placeholder.com/300x450?text=No+Poster", 
                            width="stretch")
                
                # Titre en rouge
                st.markdown(f"<p class='titre-film'>{row['title']}</p>", 
                          unsafe_allow_html=True)
                
                # Type et genre
                st.markdown(f"<p class='info-film'>📺 {row['type']}</p>", 
                          unsafe_allow_html=True)
                st.markdown(f"<p class='info-film'>🎭 {row['listed_in']}</p>", 
                          unsafe_allow_html=True)
                
                # Description dans un expander
                with st.expander(" Description"):
                    st.write(row['description'])