import pymongo
import logging
import sys
from pymongo import MongoClient
from dotenv import dotenv_values
from pymongo.server_api import ServerApi
from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
import os

config = dotenv_values(".env")
uri = config.get('MONGO_URI')
client = MongoClient(uri)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

host = uri
port = 27017
db_name = "Bop3000"
collection_name = "Bop3000.TrainingData"
# query_dict is passed into db.collection.find()
query_dict = {}
field_names = ["text"]
reader = SimpleMongoReader(host, port)
documents = reader.load_data(
    db_name, collection_name, field_names, query_dict=query_dict
)

index = SummaryIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("<query_text>")

display(Markdown(f"<b>{response}</b>"))