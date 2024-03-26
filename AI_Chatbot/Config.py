from dotenv import load_dotenv
import os

load_dotenv()
hf_token = os.getenv('HF_TOKEN')
embedding_url = os.getenv('EMBEDDING_URL')