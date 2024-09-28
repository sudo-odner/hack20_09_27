import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import nltk
import pymorphy2
from nltk.corpus import stopwords

nltk.download('stopwords')
russian_stopwords = stopwords.words("russian")


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Удаление пунктуации
    words = text.split()
    words = [word for word in words if word not in russian_stopwords]
    return ' '.join(words)


def extract_keywords_tfidf(text, top_n=5):
    vectorizer = TfidfVectorizer(max_features=top_n)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().flatten()
    keywords = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
    return [keyword for keyword, score in keywords]


def generate_tags(text):
    top_n=round(len(text.split())*0.15)
    processed_text = preprocess_text(text)

    tfidf_keywords = extract_keywords_tfidf(processed_text, top_n)
    morph = pymorphy2.MorphAnalyzer()

    tags = []
    for i in list(set(tfidf_keywords))[:top_n]:
        tags.append(morph.parse(i)[0].normal_form)
    tags = set(tags)

    return list(tags)