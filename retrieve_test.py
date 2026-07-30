import os
import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(vec_a, vec_b):
    """Measures how similar two embedding vectors are. 1 = identical meaning, 0 = unrelated."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_index(index_path):
    with open(index_path, "r") as f:
        return json.load(f)

def find_top_chunks(question, index, top_n=3):
    question_embedding = get_embedding(question)

    scored_chunks = []
    for chunk in index:
        score = cosine_similarity(question_embedding, chunk["embedding"])
        scored_chunks.append((score, chunk["text"]))

    # Sort by score, highest similarity first
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    return scored_chunks[:top_n]

if __name__ == "__main__":
    index = load_index("documents/tennant/index.json")

    test_question = "What should I do if the battery emits hydrogen gas?"
    print(f"Question: {test_question}\n")

    results = find_top_chunks(test_question, index, top_n=3)

    for i, (score, text) in enumerate(results):
        print(f"--- Match {i+1} (similarity: {score:.3f}) ---")
        print(text[:300])  # just first 300 characters, to keep output readable
        print()