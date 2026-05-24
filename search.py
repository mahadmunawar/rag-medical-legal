from qdrant_client import QdrantClient
from embeddings import get_embedding

client = QdrantClient(url="http://localhost:6333")

query_text = "Tell me about blood sugar"
query_vector = get_embedding(query_text)

# Using the modern 'query_points' method
search_result = client.query_points(
    collection_name="docs",
    query=query_vector,
    limit=1
).points

for hit in search_result:
    print(f"Match: {hit.payload['text']} (Score: {hit.score})")