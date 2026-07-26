from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def summarize_text(text, sentence_count=5):

    # Split the document into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Remove very short sentences
    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 30
    ]

    if len(sentences) <= sentence_count:
        return " ".join(sentences)

    # Convert sentences into TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(sentences)

    # Calculate importance of each sentence
    sentence_scores = cosine_similarity(
        tfidf_matrix,
        tfidf_matrix
    ).sum(axis=1)

    # Select the most important sentences
    important_indexes = sentence_scores.argsort()[
        -sentence_count:
    :]

    # Keep the original document order
    important_indexes = sorted(important_indexes)

    summary = " ".join(
        sentences[index]
        for index in important_indexes
    )

    return summary