Anime Recommendation System

A machine learning–based Anime Recommendation System that suggests similar anime titles using TF-IDF and Cosine Similarity. The application is built with Python and Streamlit, featuring user authentication, watchlists, anime detail pages, and real-time data fetched from the Jikan (MyAnimeList) API.

🚀 Features

🔍 Content-Based Recommendations using TF-IDF & cosine similarity
👤 User Authentication (Login & Signup)
⭐ Personal Watchlist management
📄 Detailed Anime Pages (poster, synopsis, ratings, episodes, year)
📺 Official Streaming Platform Links (via Jikan API)
🎨 Modern UI inspired by Netflix, IMDb & Prime Video
⚡ Cached model loading for faster performance

🧠 Recommendation Logic

Anime metadata is vectorized using TF-IDF
Cosine similarity is calculated between anime vectors
Similar anime are ranked based on similarity score
Optional filters like minimum rating are applied
Top-N recommendations are returned

🛠 Tech Stack

Programming Language: Python
Frontend: Streamlit
Data Handling: Pandas, NumPy
Machine Learning: Scikit-learn
Similarity Handling: SciPy (sparse matrices)
API: Jikan (MyAnimeList)
Storage: CSV files, Pickle models

📂 Project Structure
anime-recommendation-system/
├── app.py                     # Main Streamlit application
├── anime_info.csv             # Anime dataset
├── anime_tfidf.pkl            # TF-IDF vectorizer
├── anime_similarity.pkl       # Cosine similarity matrix
├── users.csv                  # User credentials
├── watchlist.csv              # User watchlists
├── requirements.txt           # Dependencies
└── README.md                  # Project documentation

⚙️ Installation & Setup

Clone the repository:

git clone https://github.com/your-username/anime-recommendation-system.git
cd anime-recommendation-system


Install dependencies:

pip install -r requirements.txt


Run the application:

streamlit run app.py

🌐 Deployment Notes

Local / College Demo: Use Python 3.10 or 3.11
Streamlit Cloud: Compatible with Python 3.13 using:

streamlit>=1.53.0
altair>=5.0.0

📊 Dataset

Anime metadata includes: Name, Genre, Type, Rating
Additional real-time details are fetched using the Jikan API

📈 Future Enhancements

🔮 Hybrid recommendations (collaborative + content-based)
🤖 User-based personalization
💾 Database integration (MongoDB / PostgreSQL)
📱 Mobile-friendly UI
📊 Analytics dashboard for user preferences

👨‍🎓 Academic Relevance

Suitable for BCA / MCA / B.Tech projects, Data Science & ML portfolios, and research papers on recommender systems.

🧑‍💻 Authors

Shreeyansh Srivastava
Nitin Kamia

📜 License

This project is for educational purposes. Feel free to modify and enhance it for learning and portfolio use.
