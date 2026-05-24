# qdrant_db.py

from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

def search_qdrant(vector):
    # Change 'client.search' to 'client.query_points'
    response = client.query_points(
        collection_name="medical_legal_collection",
        query=vector,    # Note: query_points uses 'query' instead of 'query_vector'
        limit=5
    )
    
    # Extract payload along with score and dynamic source file mapping
    results = []
    for hit in response.points:
        category = hit.payload.get("category", "general")
        
        # Map specific category to their source document names
        pubmed_cats = [
            "deep_learning", "covid_19", "human_connectome", "virtual_reality",
            "brain_machine_interfaces", "electroactive_polymers", "pedot_electrodes", "neuroprosthetics"
        ]
        
        if category in pubmed_cats or "links" in category:
            source = "pubmed_abstracts.csv"
        elif category == "medical":
            source = "medical_data.txt"
        elif category == "legal":
            source = "legal_data.txt"
        else:
            source = "general_knowledge"
            
        results.append({
            "text": hit.payload.get("text", ""),
            "category": category,
            "score": hit.score,
            "source": source
        })
        
    return results