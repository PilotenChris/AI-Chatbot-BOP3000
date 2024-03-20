from dotenv import dotenv_values
from pymongo import MongoClient

# https://docs.llamaindex.ai/en/latest/examples/data_connectors/MongoDemo.html

config = dotenv_values(".env")
uri = config.get('MONGO_URI')
client = MongoClient(uri)
host = uri
port = 27017
db_name = "Bop3000"
collection_name = "Bop3000.TrainingData"
field_names = ["text"]
