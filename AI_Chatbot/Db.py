import os

import pymongo
from Chatbot import generate_embedding
from dotenv import load_dotenv
from Config import hf_token, embedding_url

# https://docs.llamaindex.ai/en/latest/examples/data_connectors/MongoDemo.html

load_dotenv()

uri = os.getenv('MONGO_URI')
client = pymongo.MongoClient(uri)
db = client.Bop3000
collection = db.TrainingData

# Updating documents in the collection
for doc in collection.find({'Lead_Paragraph': {"$exists": True}}):
    try:
        embedding = generate_embedding(doc['Lead_Paragraph'])
        doc['Lead_Paragraph_embedding_hf'] = embedding
        collection.replace_one({'_id': doc['_id']}, doc)
        print(f"Updated document ID")
    except Exception as e:
        print(f"Failed to update document ID: Error: {e}")