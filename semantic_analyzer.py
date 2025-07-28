from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Define the path to our local model
MODEL_PATH = './model/'
print("Loading semantic model...")
model = SentenceTransformer(MODEL_PATH)
print("Model loaded successfully.")

def rank_chunks(query, doc_chunks):
    """
    Ranks document chunks based on semantic similarity to a user query.
    """
    print("Ranking document chunks...")
    
    # Create embeddings for the query and all chunk texts
    query_embedding = model.encode([query])
    chunk_texts = [chunk['section_title'] + ". " + chunk['text'] for chunk in doc_chunks]
    chunk_embeddings = model.encode(chunk_texts)

    # Calculate cosine similarity
    similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]

    # Attach scores to each chunk and sort
    for i, score in enumerate(similarities):
        doc_chunks[i]['relevance_score'] = score
    
    ranked_chunks = sorted(doc_chunks, key=lambda x: x['relevance_score'], reverse=True)
    
    print("Ranking complete.")
    return ranked_chunks

def get_refined_subsections(query, top_chunks, similarity_threshold=0.35):
    """
    Finds all relevant sentences within the top-ranked chunks.
    """
    print("Analyzing top sections for refined subsections...")
    subsections = []

    for chunk in top_chunks:
        # Split the chunk's text into individual sentences
        sentences = chunk['text'].split('. ')
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            continue

        # Find sentences that are highly relevant to the query
        sentence_embeddings = model.encode(sentences)
        query_embedding = model.encode([query])
        similarities = cosine_similarity(query_embedding, sentence_embeddings)[0]

        for i, score in enumerate(similarities):
            if score > similarity_threshold:
                subsections.append({
                    "document": chunk["doc_name"],
                    "page_number": chunk["page_num"],
                    "refined_text": sentences[i]
                })

    print(f"Found {len(subsections)} relevant subsections.")
    return subsections