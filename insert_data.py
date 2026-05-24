import uuid
import os
import time
import csv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# --- 1. SETUP ---
client = QdrantClient("localhost", port=6333)
# Keep the model initialization
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
collection_name = "medical_legal_collection"

# --- 2. SMART COLLECTION CHECK (NO DELETING) ---
collections = [c.name for c in client.get_collections().collections]
if collection_name not in collections:
    print(f"Collection '{collection_name}' does not exist. Creating it...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE, on_disk=True), # on_disk=True helps with memory
    )
else:
    info = client.get_collection(collection_name)
    print(f"Collection '{collection_name}' already exists with {info.points_count} points. Continuing...")

# --- 3. UPDATED UPSERT (WITH SMALLER BATCHES & DELAY) ---
def upsert_points(texts, category, batch_size=50): # Reduced batch size for stability
    total_count = 0
    points = []
    
    for i, text in enumerate(texts):
        if not text.strip():
            continue
            
        vector = model.encode(text.strip()).tolist()
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": text.strip(), "category": category}
        ))
        
        if len(points) >= batch_size:
            client.upsert(collection_name=collection_name, points=points)
            total_count += len(points)
            points = []
            time.sleep(0.1) # Brief pause to prevent memory spikes
            print(f"    Uploaded batch: {total_count} points total...")

    if points:
        client.upsert(collection_name=collection_name, points=points)
        total_count += len(points)
        
    return total_count


# --- 4. INGESTION WITH MANUAL SKIP ---
# Look at your previous terminal output. 
# You finished: 'deep_learning', 'covid_19', 'human_connectome'
# It crashed on: 'virtual_reality'
total = 0


def load_txt(file_path, category):
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found. Skipping...")
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        texts = f.readlines()
    
    print(f"\n--- Processing '{category}' from {file_path} ---")
    return upsert_points(texts, category)

def load_csv(file_path):
    import ast
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found. Skipping...")
        return 0
    
    total_uploaded = 0
    categories = [
        "deep_learning", "covid_19", "human_connectome", "virtual_reality",
        "brain_machine_interfaces", "electroactive_polymers", "pedot_electrodes", "neuroprosthetics",
        "deep_learning_links", "covid_19_links", "human_connectome_links", "virtual_reality_links",
        "brain_machine_interfaces_links", "electroactive_polymers_links", "pedot_electrodes_links", "neuroprosthetics_links"
    ]
    
    category_texts = {cat: [] for cat in categories}
    
    print(f"\n--- Reading CSV '{file_path}' ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for cat in categories:
                val = row.get(cat, "")
                if val and val != "[]" and "()" not in val:
                    try:
                        parsed = ast.literal_eval(val)
                        # Expecting format: (['abstract text'], 'Title')
                        if isinstance(parsed, tuple) and len(parsed) > 0 and isinstance(parsed[0], list) and len(parsed[0]) > 0:
                            category_texts[cat].append(parsed[0][0])
                    except Exception:
                        pass
                        
    for cat in categories:
        texts = category_texts[cat]
        if texts:
            print(f"\n--- Processing '{cat}' from CSV ({len(texts)} items) ---")
            total_uploaded += upsert_points(texts, cat)
            
    return total_uploaded

print("Starting txt and CSV ingestion...")

total += load_txt(r"C:\Users\mahad\OneDrive\Desktop\rag-api\medical_data.txt", category="medical")
total += load_txt(r"C:\Users\mahad\OneDrive\Desktop\rag-api\legal_data.txt", category="legal")
total += load_csv(r"C:\Users\mahad\OneDrive\Desktop\rag-api\pubmed_abstracts.csv")

print(f"\n--- Done! New chunks uploaded this session: {total} ---")
final_info = client.get_collection(collection_name)
print(f"Collection '{collection_name}' now total points: {final_info.points_count}")