from sentence_transformers import SentenceTransformer

# load model once (important)
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):
    embedding = model.encode(text)
    return embedding.tolist()