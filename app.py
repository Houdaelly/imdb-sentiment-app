import streamlit as st
import joblib
from preprocess import clean_text

st.set_page_config(page_title="IMDB Sentiment Classifier", page_icon="🎬")

# ---------- Purple theme ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg:       #0F0A1F;
        --surface:  #1A1230;
        --border:   #3B2A66;
        --accent:   #A855F7;
        --accent-2: #7C3AED;
        --text:     #EDE9FE;
        --muted:    #A78BFA;
    }

    html, body, .stApp, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }

    .stApp { background: var(--bg); }
    header[data-testid="stHeader"] { background: transparent; }
    footer { visibility: hidden; }

    .block-container { max-width: 720px; padding-top: 3rem; }

    h1 {
        color: var(--text);
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .stApp p, .stApp label { color: var(--muted); }

    /* Text area */
    .stTextArea textarea {
        background: var(--surface);
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent);
    }
    .stTextArea textarea::placeholder { color: #6D5BA8; }

    /* Button */
    .stButton > button {
        background: var(--accent-2);
        color: #fff;
        border: 1px solid var(--accent);
        border-radius: 10px;
        padding: 0.55rem 2rem;
        font-weight: 600;
        transition: background 0.15s, box-shadow 0.15s;
    }
    .stButton > button:hover {
        background: var(--accent);
        border-color: var(--accent);
        color: #fff;
        box-shadow: 0 0 18px rgba(168, 85, 247, 0.5);
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
    }
    div[data-testid="stAlert"] * { color: var(--text) !important; }

    /* Progress bar */
    .stProgress > div > div > div { background: var(--border); }
    .stProgress > div > div > div > div { background: var(--accent); }

    /* Expander */
    div[data-testid="stExpander"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
    }
    div[data-testid="stExpander"] summary { color: var(--muted); }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def load_model():
    return joblib.load("sentiment_model.joblib")

model = load_model()

st.title("🎬 IMDB Review Sentiment Classifier")
st.write("Type a movie review and the model will predict whether it is positive or negative.")

review = st.text_area("Enter a movie review:", height=200,
                      placeholder="This movie was absolutely fantastic...")

if st.button("Predict"):
    if review.strip() == "":
        st.warning("Please enter a review first.")
    else:
        cleaned = clean_text(review)
        label = model.predict([cleaned])[0]
        proba = model.predict_proba([cleaned])[0]

        if label == 1:
            st.success(f"Positive 😊  (confidence: {proba[1]:.1%})")
        else:
            st.error(f"Negative 😞  (confidence: {proba[0]:.1%})")

        st.progress(float(proba[1]), text=f"Positive probability: {proba[1]:.1%}")

        with st.expander("Show cleaned text"):
            st.write(cleaned)