import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
import requests
from scipy.sparse import issparse
import hashlib
import os

# =====================================================
#  PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Anime Recommender",
    page_icon="✨",
    layout="wide",
)

# =====================================================
#  CUSTOM CSS (IMDb + Netflix + Prime Vibes)
# =====================================================
st.markdown("""
    <style>
    /* Background and fonts */
    .stApp {
        background: radial-gradient(circle at top, #1b2735 0%, #090a0f 45%, #000000 100%);
        color: #fff;
        font-family: 'Poppins', sans-serif;
    }

    /* Titles */
    h1, h2, h3 {
        font-weight: 600;
        color: #e5a50a;  /* IMDb-ish gold */
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #070b12;
        border-right: 1px solid #20222a;
    }

    /* Global buttons */
    div.stButton > button {
        color: white;
        background: linear-gradient(135deg, #e50914 0%, #f40612 40%, #0f79af 100%);
        border: none;
        border-radius: 999px;
        padding: 0.5rem 1.4rem;
        font-weight: 500;
        transition: 0.2s ease-in-out;
        box-shadow: 0 0 15px rgba(0,0,0,0.5);
    }
    div.stButton > button:hover {
        transform: scale(1.04) translateY(-1px);
        filter: brightness(1.1);
    }

    /* Anime cards on home/profile */
    .anime-card {
        background: radial-gradient(circle at top left, #1f2933 0%, #111827 45%, #020617 100%);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 18px 45px rgba(0,0,0,0.75);
        border: 1px solid rgba(148,163,184,0.25);
        transition: 0.25s ease-in-out;
    }
    .anime-card:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 24px 60px rgba(0,0,0,0.9);
        border-color: #e5a50a;
    }

    /* Tag chips */
    .tag-chip {
        display: inline-block;
        padding: 0.25rem 0.8rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
        border-radius: 999px;
        background: rgba(31,41,55,0.9);
        border: 1px solid rgba(148,163,184,0.5);
        font-size: 0.75rem;
    }

    /* Top nav bar */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 1.2rem;
        border-radius: 999px;
        background: rgba(15,23,42,0.92);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(148,163,184,0.35);
        margin-bottom: 1.2rem;
        box-shadow: 0 18px 40px rgba(0,0,0,0.75);
    }
    .top-nav-left {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .brand-pill {
        background: linear-gradient(135deg,#e50914,#f40612,#0f79af);
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .top-nav-title {
        font-size: 1.05rem;
        font-weight: 500;
    }
    .top-nav-links {
        display: flex;
        gap: 0.6rem;
        align-items: center;
    }
    .user-chip {
        font-size: 0.8rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(15,23,42,0.9);
        border: 1px solid rgba(148,163,184,0.45);
    }

    /* Detail hero like IMDb */
    .detail-hero {
        background: radial-gradient(circle at top, #32302f 0%, #14110f 40%, #050505 100%);
        border-radius: 26px;
        padding: 24px;
        display: flex;
        gap: 18px;
        box-shadow: 0 26px 70px rgba(0,0,0,0.9);
        margin-bottom: 22px;
    }
    .detail-left {
        flex: 0 0 220px;
        border-radius: 18px;
        overflow: hidden;
    }
    .detail-center {
        flex: 1.8;
        border-radius: 20px;
        overflow: hidden;
    }
    .detail-right {
        flex: 0.9;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .detail-title {
        font-size: 2.2rem;
        font-weight: 600;
    }
    .detail-meta {
        font-size: 0.9rem;
        color: #e5e7eb;
        margin-top: 0.3rem;
    }
    .detail-rating {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-top: 0.8rem;
        font-size: 0.95rem;
    }
    .rating-badge {
        background: #f5c518;
        color: #000;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-weight: 600;
    }

    /* Streaming platforms row */
    .platform-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.6rem;
    }
    .platform-card {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: radial-gradient(circle at top left, #111827 0%, #020617 100%);
        border: 1px solid rgba(148,163,184,0.5);
        cursor: pointer;
        font-size: 0.8rem;
        text-decoration: none;
        color: #e5e7eb;
    }
    .platform-card:hover {
        border-color: #f5c518;
        transform: translateY(-1px);
    }
    .platform-logo {
        width: 22px;
        height: 22px;
        border-radius: 6px;
        object-fit: contain;
        background: #000;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #9ca3af;
        margin-top: 40px;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================
#  HEADER
# =====================================================
col1, col2 = st.columns([1, 5])
with col1:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png",
        width=100
    )
with col2:
    st.markdown("<h1>Anime Recommendation System</h1>", unsafe_allow_html=True)
    st.caption("Inspired by IMDb • Netflix • Prime Video • Powered by TF-IDF, Cosine Similarity & Jikan API")

st.markdown("---")

# =====================================================
#  LOAD MODEL
# =====================================================
@st.cache_resource
def load_model():
    with open("anime_tfidf.pkl", "rb") as f:
        tfidf = pickle.load(f)
    with open("anime_similarity.pkl", "rb") as f:
        similarity = pickle.load(f)
    df = pd.read_csv("anime_info.csv")
    return tfidf, similarity, df

try:
    tfidf, similarity, anime_df = load_model()
except Exception as e:
    st.error(f"Could not load model files: {e}")
    st.stop()

# =====================================================
#  AUTH & WATCHLIST HELPERS
# =====================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> pd.DataFrame:
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    else:
        return pd.DataFrame(columns=["username", "password"])

def save_user(username: str, password: str):
    users = load_users()
    if username in users["username"].values:
        raise ValueError("Username already exists.")
    hashed = hash_password(password)
    users.loc[len(users)] = [username, hashed]
    users.to_csv("users.csv", index=False)

def verify_user(username: str, password: str) -> bool:
    users = load_users()
    if users.empty:
        return False
    hashed = hash_password(password)
    return ((users["username"] == username) & (users["password"] == hashed)).any()

def load_watchlist() -> pd.DataFrame:
    if os.path.exists("watchlist.csv"):
        return pd.read_csv("watchlist.csv")
    else:
        return pd.DataFrame(columns=["username", "anime_name"])

def save_watchlist(df: pd.DataFrame):
    df.to_csv("watchlist.csv", index=False)

def add_to_watchlist(username: str, anime_name: str):
    wl = load_watchlist()
    if not ((wl["username"] == username) & (wl["anime_name"] == anime_name)).any():
        wl.loc[len(wl)] = [username, anime_name]
        save_watchlist(wl)

def remove_from_watchlist(username: str, anime_name: str):
    wl = load_watchlist()
    wl = wl[~((wl["username"] == username) & (wl["anime_name"] == anime_name))]
    save_watchlist(wl)

def get_user_watchlist(username: str):
    wl = load_watchlist()
    return wl[wl["username"] == username]["anime_name"].tolist()

# =====================================================
#  SESSION STATE (LOGIN + NAVIGATION + DETAIL VIEW)
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "Home"   # "Home", "Profile", "Details"
if "detail_anime" not in st.session_state:
    st.session_state.detail_anime = None

# =====================================================
#  LOGIN / SIGNUP PAGE
# =====================================================
if not st.session_state.logged_in:
    st.title("🔐 Login / Signup")

    choice = st.radio("Select Option", ["Login", "Signup"], horizontal=True)

    if choice == "Login":
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            if verify_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    else:
        new_username = st.text_input("Create Username")
        new_password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if not new_username or not new_password:
                st.error("Please enter both username and password.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    save_user(new_username, new_password)
                    st.success("✅ Account created successfully! Please login from the Login tab.")
                except ValueError as ve:
                    st.error(str(ve))
                except Exception as e:
                    st.error(f"Error creating user: {e}")

    st.stop()

# =====================================================
#  AFTER LOGIN – TOP NAV BAR
# =====================================================
st.markdown(
    f"""
    <div class="top-nav">
        <div class="top-nav-left">
            <div class="brand-pill">AniFlix</div>
            <div class="top-nav-title">Welcome, {st.session_state.username}</div>
        </div>
        <div class="top-nav-links">
            <span class="user-chip">Logged in • {st.session_state.username}</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

nav_cols = st.columns([1, 1, 1, 3])
with nav_cols[0]:
    if st.button("🏠 Home", key="nav_home"):
        st.session_state.page = "Home"
        st.session_state.detail_anime = None
        st.rerun()
with nav_cols[1]:
    if st.button("🙍 My Profile / Watchlist", key="nav_profile"):
        st.session_state.page = "Profile"
        st.rerun()
with nav_cols[2]:
    if st.button("🚪 Logout", key="nav_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "Home"
        st.session_state.detail_anime = None
        st.rerun()

# =====================================================
#  SIDEBAR CONTROLS
# =====================================================
st.sidebar.header("🎯 Find Your Next Anime")
anime_titles = sorted(anime_df['name'].dropna().astype(str).tolist())

selected_anime = st.sidebar.selectbox("Select an Anime Title", anime_titles)
top_n = st.sidebar.slider("Number of Recommendations", 5, 20, 10)
min_rating = st.sidebar.slider("Minimum Rating Filter", 0.0, 10.0, 0.0, 0.1)

st.sidebar.markdown("---")
st.sidebar.caption("Designed by *Shreeyansh Srivastava & Nitin Kamia*")

# =====================================================
#  JIKAN HELPERS
# =====================================================
@st.cache_data(show_spinner=False)
def get_anime_info(title: str):
    """Fetch anime poster, synopsis, basic info & MAL ID from Jikan API."""
    try:
        url = f"https://api.jikan.moe/v4/anime?q={title}&limit=1"
        res = requests.get(url, timeout=10).json()
        if "data" in res and len(res["data"]) > 0:
            anime_data = res["data"][0]
            poster = anime_data["images"]["jpg"].get("large_image_url") or \
                     anime_data["images"]["jpg"].get("image_url")
            synopsis = anime_data.get("synopsis", "Synopsis not available.")
            score = anime_data.get("score", "N/A")
            episodes = anime_data.get("episodes", "N/A")
            year = anime_data.get("year", "N/A")
            mal_id = anime_data.get("mal_id", None)
            return poster, synopsis, score, episodes, year, mal_id
        else:
            return None, "No information found.", "N/A", "N/A", "N/A", None
    except Exception:
        return None, "Error fetching info.", "N/A", "N/A", "N/A", None

@st.cache_data(show_spinner=False)
def get_watch_platforms(mal_id):
    """
    Fetch official streaming platforms for the given MAL ID.
    Returns list of dicts: [{name, url}]
    """
    if mal_id is None:
        return []

    try:
        url = f"https://api.jikan.moe/v4/anime/{mal_id}/streaming"
        res = requests.get(url, timeout=10).json()

        platforms = []
        if "data" in res and len(res["data"]) > 0:
            for entry in res["data"]:
                name = entry.get("name", "Unknown platform")
                link = entry.get("url", "")
                platforms.append({"name": name, "url": link})
        return platforms
    except Exception:
        return []

# Platform logo mapping (simple keyword-based)
PLATFORM_LOGOS = {
    "Netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    "Prime": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Prime_Video.png",
    "Amazon": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Prime_Video.png",
    "Crunchyroll": "https://upload.wikimedia.org/wikipedia/commons/7/71/Crunchyroll_Logo.png",
    "Disney": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg",
    "Hulu": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Hulu_Logo.svg",
    "Funimation": "https://upload.wikimedia.org/wikipedia/commons/8/8f/Funimation_2016_logo.svg",
    "Hidive": "https://upload.wikimedia.org/wikipedia/commons/8/89/Hidive_logo.svg",
}

def get_platform_logo(name: str):
    for key, url in PLATFORM_LOGOS.items():
        if key.lower() in name.lower():
            return url
    # generic play icon
    return "https://upload.wikimedia.org/wikipedia/commons/3/3c/Black_triangle.svg"

# =====================================================
#  RECOMMENDATION FUNCTION
# =====================================================
def recommend_anime(title, top_n=10, min_rating=0.0):
    if title not in anime_df['name'].values:
        return pd.DataFrame(columns=['name', 'genre', 'type', 'rating'])

    idx = anime_df[anime_df['name'] == title].index[0]
    sims = similarity[idx]
    sims = sims.toarray().ravel() if issparse(sims) else np.asarray(sims).ravel()

    sim_scores = sorted(list(enumerate(sims)), key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n + 50]

    anime_indices = [i for i, _ in sim_scores]
    result = anime_df.iloc[anime_indices].copy()
    result['similarity'] = [s for _, s in sim_scores]

    if min_rating > 0 and 'rating' in result.columns:
        result = result[result['rating'].fillna(0) >= min_rating]

    return result.head(top_n)

# =====================================================
#  DETAIL PAGE (IMDb-like layout)
# =====================================================
def render_detail_page(anime_name: str):
    current_user = st.session_state.username
    user_watchlist = set(get_user_watchlist(current_user))

    poster_url, synopsis, score, episodes, year, mal_id = get_anime_info(anime_name)
    platforms = get_watch_platforms(mal_id)
    in_watchlist = anime_name in user_watchlist

    # Meta info from dataset
    row = anime_df[anime_df["name"] == anime_name]
    genre_str = row["genre"].iloc[0] if not row.empty and "genre" in row.columns else ""
    anime_type = row["type"].iloc[0] if not row.empty and "type" in row.columns else "Anime"
    rating_ds = row["rating"].iloc[0] if not row.empty and "rating" in row.columns else "N/A"

    tags = [g.strip() for g in str(genre_str).split(",") if g.strip()]

    st.markdown("### ")
    # Hero section
    st.markdown('<div class="detail-hero">', unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2.1, 1])

    with col_left:
        st.markdown('<div class="detail-left">', unsafe_allow_html=True)
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/300x450.png?text=No+Image", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_center:
        st.markdown('<div class="detail-center">', unsafe_allow_html=True)
        if poster_url:
            st.image(poster_url, use_container_width=True)  # acts like big preview
        else:
            st.image("https://via.placeholder.com/640x360.png?text=Anime+Preview", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="detail-right">', unsafe_allow_html=True)
        st.markdown(f"<div class='detail-title'>{anime_name}</div>", unsafe_allow_html=True)
        meta = f"{anime_type} • {year if year!='N/A' else ''} • {episodes} eps"
        st.markdown(f"<div class='detail-meta'>{meta}</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="detail-rating">
                <span class="rating-badge">IMDb</span> <span>{score}/10</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='margin-top:0.3rem;font-size:0.85rem;color:#d1d5db;'>Dataset rating: {rating_ds}</div>",
            unsafe_allow_html=True,
        )

        # Watchlist button
        if not in_watchlist:
            if st.button("➕ Add to Watchlist", key="detail_add_wl"):
                add_to_watchlist(current_user, anime_name)
                st.success("Added to your watchlist!")
                st.rerun()
        else:
            if st.button("🗑 Remove from Watchlist", key="detail_rm_wl"):
                remove_from_watchlist(current_user, anime_name)
                st.success("Removed from your watchlist.")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Tags + synopsis
    if tags:
        chip_html = "".join([f"<span class='tag-chip'>{t}</span>" for t in tags])
        st.markdown(chip_html, unsafe_allow_html=True)

    st.markdown("")
    st.markdown(f"**Overview**  \n{(synopsis or 'Synopsis not available.')}")

    # Streaming platforms with logos
    st.markdown("### 📺 Streaming")
    if not platforms:
        st.write("No official streaming information available.")
    else:
        st.markdown('<div class="platform-row">', unsafe_allow_html=True)
        for p in platforms:
            name = p.get("name", "Unknown")
            url = p.get("url", "")
            logo = get_platform_logo(name)

            # clickable badge using markdown+HTML
            if url:
                st.markdown(
                    f"""
                    <a class="platform-card" href="{url}" target="_blank">
                        <img class="platform-logo" src="{logo}">
                        <span>{name}</span>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="platform-card">
                        <img class="platform-logo" src="{logo}">
                        <span>{name}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
#  PAGE: HOME
# =====================================================
if st.session_state.page == "Home":
    with st.spinner("🔍 Finding the best recommendations for you..."):
        time.sleep(1)
        recs = recommend_anime(selected_anime, top_n=top_n, min_rating=min_rating)

    if recs.empty:
        st.warning("No recommendations found. Try changing filters.")
    else:
        st.success(f"🎉 Top {len(recs)} anime similar to *{selected_anime}*:")
        st.markdown("")

        current_user = st.session_state.username
        user_watchlist = set(get_user_watchlist(current_user))

        for idx, row in recs.iterrows():
            poster_url, synopsis, score, episodes, year, mal_id = get_anime_info(row['name'])
            platforms = get_watch_platforms(mal_id)
            in_watchlist = row['name'] in user_watchlist

            with st.container():
                st.markdown("<div class='anime-card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 3])

                with col1:
                    if poster_url:
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.image(
                            "https://via.placeholder.com/200x300.png?text=No+Image",
                            use_container_width=True
                        )

                with col2:
                    st.markdown(f"### {row['name']}")
                    st.markdown(f"*Genre:* {row.get('genre', 'N/A')}")
                    st.markdown(
                        f"*Type:* {row.get('type', 'N/A')}  |  "
                        f"*Episodes:* {episodes}  |  *Year:* {year}"
                    )
                    st.markdown(
                        f"*MAL Score:* {score}  |  "
                        f"*Dataset Rating:* {row.get('rating', 'N/A')}"
                    )
                    st.markdown(
                        f"*Synopsis:* {(synopsis or 'Synopsis not available.')[:350]}..."
                    )

                    try:
                        sim_val = float(row['similarity'])
                        st.progress(min(sim_val, 1.0))
                    except Exception:
                        pass

                    with st.expander("📺 Where to Watch"):
                        if not platforms:
                            st.write("No official streaming information available.")
                        else:
                            for p in platforms:
                                name = p.get("name", "Unknown")
                                url = p.get("url", "")
                                if url:
                                    st.markdown(f"- [{name}]({url})")
                                else:
                                    st.markdown(f"- {name}")

                    btn_cols = st.columns([1, 1, 4])
                    with btn_cols[0]:
                        if not in_watchlist:
                            if st.button("➕ Watchlist", key=f"add_{idx}"):
                                add_to_watchlist(current_user, row['name'])
                                st.success("Added to your watchlist!")
                                st.rerun()
                        else:
                            st.markdown("✅ In watchlist")
                    with btn_cols[1]:
                        if st.button("ℹ View Details", key=f"detail_{idx}"):
                            st.session_state.detail_anime = row['name']
                            st.session_state.page = "Details"
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
#  PAGE: PROFILE + WATCHLIST
# =====================================================
elif st.session_state.page == "Profile":
    current_user = st.session_state.username
    user_list = get_user_watchlist(current_user)

    st.subheader("🙍 My Profile")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"**Username:** `{current_user}`")
        st.markdown(f"**Total in Watchlist:** `{len(user_list)}`")
    with col_p2:
        st.markdown("**Account Type:** Standard User")
        st.markdown("**Features:** Recommendations, Watchlist, Streaming Links")

    st.markdown("---")
    st.subheader("📺 My Watchlist")

    if not user_list:
        st.info("Your watchlist is empty. Go to **Home** and add some anime!")
    else:
        for idx, name in enumerate(user_list):
            poster_url, synopsis, score, episodes, year, mal_id = get_anime_info(name)
            platforms = get_watch_platforms(mal_id)

            with st.container():
                st.markdown("<div class='anime-card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 3])

                with col1:
                    if poster_url:
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.image(
                            "https://via.placeholder.com/200x300.png?text=No+Image",
                            use_container_width=True
                        )

                with col2:
                    st.markdown(f"### {name}")
                    st.markdown(
                        f"*Episodes:* {episodes}  |  *Year:* {year}  |  *MAL Score:* {score}"
                    )
                    st.markdown(
                        f"*Synopsis:* {(synopsis or 'Synopsis not available.')[:350]}..."
                    )

                    with st.expander("📺 Where to Watch"):
                        if not platforms:
                            st.write("No official streaming information available.")
                        else:
                            for p in platforms:
                                pname = p.get("name", "Unknown")
                                url = p.get("url", "")
                                if url:
                                    st.markdown(f"- [{pname}]({url})")
                                else:
                                    st.markdown(f"- {pname}")

                    btn_cols = st.columns([1, 1, 4])
                    with btn_cols[0]:
                        if st.button("🗑 Remove", key=f"rm_{idx}"):
                            remove_from_watchlist(current_user, name)
                            st.success("Removed from your watchlist.")
                            st.rerun()
                    with btn_cols[1]:
                        if st.button("ℹ Details", key=f"detail_prof_{idx}"):
                            st.session_state.detail_anime = name
                            st.session_state.page = "Details"
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
#  PAGE: DETAILS
# =====================================================
elif st.session_state.page == "Details":
    if not st.session_state.detail_anime:
        st.info("No anime selected. Go to **Home** and click on *View Details*.")
    else:
        render_detail_page(st.session_state.detail_anime)

# =====================================================
#  FOOTER
# =====================================================
st.markdown("<br><div class='footer'>Made with ❤️ using Streamlit, scikit-learn, and Jikan API.</div>", unsafe_allow_html=True)
