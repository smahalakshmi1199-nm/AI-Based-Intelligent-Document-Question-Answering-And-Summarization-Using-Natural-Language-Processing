from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_answer(document_text, question):

    # Split document into separate paragraphs
    paragraphs = document_text.split("\n")

    # Remove empty paragraphs
    paragraphs = [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]

    if not paragraphs:
        return "No content found in the document."

    # Add the question along with document paragraphs
    all_text = paragraphs + [question]

    # Convert text into numerical vectors
    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(all_text)

    # Compare question with every paragraph
    similarity_scores = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    )

    # Find the paragraph with the highest similarity
    best_match_index = similarity_scores.argmax()

    best_score = similarity_scores[0][best_match_index]

    # If similarity is too low
    if best_score < 0.1:
        return "Sorry, I could not find a relevant answer in the document."

    return paragraphs[best_match_index]