"""All NLTK code for the Library Management System lives here."""
from collections import Counter

import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Auto-download corpora on first import if missing.
try:
    STOPWORDS = set(stopwords.words("english"))
    _ = word_tokenize("test")              # needs punkt
    _ = SentimentIntensityAnalyzer()       # needs vader_lexicon
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")
    nltk.download("stopwords")
    nltk.download("vader_lexicon")
    STOPWORDS = set(stopwords.words("english"))
    _ = word_tokenize("test")
    _ = SentimentIntensityAnalyzer()

_STEMMER = PorterStemmer()
_SIA = SentimentIntensityAnalyzer()


def normalize(text):
    """Lowercase + tokenize + remove stopwords -> list of tokens."""
    if not text:
        return []
    tokens = word_tokenize(text.lower())
    return [t for t in tokens if t.isalpha() and t not in STOPWORDS]


def stem(text):
    """Porter-stem each normalized token, e.g. 'searching' -> 'search'."""
    return [_STEMMER.stem(t) for t in normalize(text)]


def sentiment(text):
    """VADER polarity scores -> {pos, neg, neu, compound} plus a label."""
    if not text:
        return {"pos": 0.0, "neg": 0.0, "neu": 0.0, "compound": 0.0, "label": "Neutral"}
    scores = _SIA.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
    return {**scores, "label": label}


def keywords(text, top=6):
    """Most frequent normalized tokens, used as auto-tags for a book."""
    if not text:
        return []
    counts = Counter(normalize(text))
    return [word for word, _ in counts.most_common(top)]


def name_tokens(text):
    """Tokenize a full name preserving case, for first/last splitting."""
    if not text:
        return []
    return [t for t in word_tokenize(text.strip()) if t.isalpha()]
