import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

negations = {"no", "nor", "not", "never", "neither", "none", "nothing"}

keep_words = {
    "very", "too", "but", "against", "only",
    "most", "more", "few", "just", "so"
}

stop_words = set(stopwords.words("english")) - negations - keep_words

lemmatizer = WordNetLemmatizer()


def clean_text(text):
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = text.lower()

    text = text.replace("\u2019", "'").replace("`", "'")
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't|cannot", "can not", text)
    text = re.sub(r"ain't", "is not", text)
    text = re.sub(r"n't\b", " not", text)

    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = [w for w in text.split() if w not in stop_words]
    words = [lemmatizer.lemmatize(w) for w in words]

    # Attach negation to the next word
    out, i = [], 0

    while i < len(words):
        if (
            words[i] in negations
            and i + 1 < len(words)
            and words[i + 1] not in negations
        ):
            out.append(words[i] + "_" + words[i + 1])
            i += 2
        else:
            out.append(words[i])
            i += 1

    return " ".join(out)
