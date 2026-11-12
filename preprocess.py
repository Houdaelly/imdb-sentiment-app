import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

# Keep negations: "not good" is the opposite of "good"
stop_words = set(stopwords.words("english")) - {"no", "nor", "not"}
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = re.sub(r"<.*?>", " ", text)               # HTML tags
    text = re.sub(r"http\S+|www\.\S+", " ", text)    # URLs
    text = text.lower()                              # lowercase

    text = re.sub(r"won't", "will not", text)        # contractions -> "not"
    text = re.sub(r"can't", "can not", text)
    text = re.sub(r"n't\b", " not", text)

    text = re.sub(r"[^a-z\s]", " ", text)            # punctuation, digits, special chars
    text = re.sub(r"\s+", " ", text).strip()         # extra whitespace

    words = [w for w in text.split() if w not in stop_words]   # stopwords
    words = [lemmatizer.lemmatize(w) for w in words]           # lemmatization
    return " ".join(words)