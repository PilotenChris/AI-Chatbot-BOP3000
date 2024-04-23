import os

import pymongo
from dotenv import load_dotenv


load_dotenv()
# Database connection
uri = os.getenv('MONGO_URI')
client = pymongo.MongoClient(uri)
db = client.Bop3000
collection = db.Feedback
