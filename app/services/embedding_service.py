import os
os.environ["USE_TF"] = "0"

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

faq_embeddings = None
faq_questions = []


def build_faq_embeddings(faqs):

    global faq_embeddings
    global faq_questions

    faq_questions = [
        faq.Questions
        for faq in faqs
    ]

    faq_embeddings = model.encode(
        faq_questions,
        convert_to_numpy=True
    )


def semantic_search(user_query, faqs):

    global faq_embeddings
    global faq_questions

    if faq_embeddings is None:
        build_faq_embeddings(faqs)

    query_embedding = model.encode(
        [user_query],
        convert_to_numpy=True
    )

    similarities = cosine_similarity(
        query_embedding,
        faq_embeddings
    )[0]

    best_index = np.argmax(similarities)

    best_score = float(
        similarities[best_index]
    )

    best_faq = faqs[best_index]

    return best_faq, round(best_score * 100, 2)