# 🎬 CineMood: IMDB Review Sentiment Classifier

Binary sentiment classification (positive / negative) on 50,000 IMDB movie reviews,
with a Streamlit web app.

## Results
| Model | Accuracy |
|---|---|
| Rule-based baseline | 67.7% |
| Logistic Regression (TF-IDF, tuned C) | ~90% |

## Pipeline
1. EDA (balance, duplicates, review length, frequent words)
2. Text cleaning (HTML, URLs, lowercase, punctuation, stopwords, lemmatization; negations kept)
3. TF-IDF (unigrams + bigrams, 20,000 features)
4. Logistic Regression, tuned with Grid Search on C
5. Streamlit app

## Dataset
IMDB Dataset of 50K Movie Reviews (not included, download it from Kaggle).

## Run the app
```bash
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `sentiment_analysis.ipynb`: EDA, cleaning, training, baseline, tuning
- `preprocess.py`: text cleaning used by the app
- `app.py`: Streamlit interface
- `sentiment_model.joblib`: trained TF-IDF + Logistic Regression pipeline

## Authors
- Nourelhouda Kherbachi
- Ikram Graichi