from openai import OpenAI
import numpy as np
import os

client = OpenAI(api_key=os.getenv("CHATBOT_OPENAI_API_KEY"))

def search_chunks(query, embeddings, top_n=5):
    
    data = embeddings.to_dict(orient="records")

    chunks = [{"chunk": item["chunk"], "embedding": np.array(item["embedding"])} for item in data]

    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[query]
    )
    query_embedding = np.array(response.data[0].embedding)

    # Using Cosine Similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    # Rank chunks by similarity
    scored_chunks = [(chunk["chunk"], cosine_similarity(query_embedding, chunk["embedding"])) for chunk in chunks]
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    # Return top N results
    return " ".join([chunk[0] for chunk in scored_chunks[:top_n]])
