import re
import nltk
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import pymorphy3

nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('russian'))


def preprocess_text_for_text_data(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub('\n', ' ', text)
    text = re.sub('\t', ' ', text)
    text = re.sub(r'[^A-Za-zА-яа-я0-9\s]', ' ', text)

    words = [word for word in word_tokenize(text) if word not in stop_words]
    return ' '.join(words)


def preprocess_sentences(text):
    sentences = sent_tokenize(text.lower())
    return sentences


def extract_keywords(text, num_keywords=5):
    tfidf_vectorizer = TfidfVectorizer(max_features=num_keywords)
    tfidf_matrix = tfidf_vectorizer.fit_transform([text])
    keywords = tfidf_vectorizer.get_feature_names_out()
    return keywords


def extract_key_sentences(text, num_sentences=1):
    sentences = preprocess_sentences(text)

    # Построение графа для TextRank
    def sentence_similarity(sent1, sent2):
        words1 = set(word_tokenize(sent1))
        words2 = set(word_tokenize(sent2))
        common_words = words1.intersection(words2)
        return len(common_words) / (np.log(len(words1)) + np.log(len(words2)))

    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 != idx2:
                similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2])

    nx_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(nx_graph)

    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    key_sentences = [ranked_sentences[i][1] for i in range(min(num_sentences, len(ranked_sentences)))]
    return key_sentences


def generate_text_data(text, num_keywords=5, num_sentences=1):
    # Извлечение ключевых слов с использованием TF-IDF
    dirty_keywords = extract_keywords(preprocess_text_for_text_data(text), num_keywords)

    morph = pymorphy3.MorphAnalyzer()

    keywords = []
    for i in list(set(dirty_keywords)):
        nf_word = morph.parse(i)[0].normal_form
        if nf_word not in keywords: keywords.append(nf_word)

    # Извлечение ключевых предложений с использованием TextRank
    key_sentences = extract_key_sentences(text, num_sentences=num_sentences)

    # Комбинирование ключевых слов и предложений для формирования заголовка
    combined_keywords = ' '.join(keywords).capitalize()
    for i in range(len(key_sentences)):
        key_sentences[i] = key_sentences[i].capitalize()

    combined_sentences = ' '.join(key_sentences)

    return combined_keywords,combined_sentences