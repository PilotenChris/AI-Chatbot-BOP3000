import os

import pymongo
from dotenv import load_dotenv
import requests

# https://docs.llamaindex.ai/en/latest/examples/data_connectors/MongoDemo.html

load_dotenv()
# Database connection
uri = os.getenv('MONGO_URI')
client = pymongo.MongoClient(uri)
db = client.Bop3000
collection = db.TrainingData

# Huggingcace token & API
hf_token = os.getenv('HF_TOKEN')
embedding_url = os.getenv('EMBEDDING_URL')


# Function to generate embeddings using huggingface api
def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json={"inputs": text}
    )

    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
    return response.json()

# Updating documents in the collection
for doc in collection.find({'Lead_Paragraph': {"$exists": True}}):
    try:
        embedding = generate_embedding(doc['Lead_Paragraph'])
        doc['Lead_Paragraph_embedding_hf'] = embedding
        collection.replace_one({'_id': doc['_id']}, doc)
    except Exception as e:
        print(f"Failed to update document ID: Error: {e}")
