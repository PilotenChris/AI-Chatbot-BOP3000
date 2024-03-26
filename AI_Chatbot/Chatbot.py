import torch
import transformers
import time
from Config import embedding_url, hf_token
from Db import collection
from pymongo import MongoClient
from dotenv import dotenv_values
from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from transformers import LlamaTokenizer, AutoConfig, LlamaForCausalLM, pipeline, BitsAndBytesConfig
from torch import cuda, bfloat16
from langchain_community.llms import HuggingFacePipeline
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import load_tools
from langchain.agents import initialize_agent
import requests


# Llama-2 from Hugging Face
model_dir = "meta-llama/Llama-2-7b-chat-hf"

"""
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    device_map='auto',
    token=""
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
"""

# Determine if a GPU is available and set the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Record the start time
start = time.time()

# Check if CUDA is available (for informational purposes)
print(torch.cuda.is_available())

# Configuration for BitsAndBytes, an optimization for model quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

# Load the Llama-2 model with the specified quantization configuration
model = LlamaForCausalLM.from_pretrained(
    pretrained_model_name_or_path=model_dir,
    cache_dir="./",
    device_map='auto',
    quantization_config=bnb_config
)

# Load the tokenizer for the model
tokenizer = LlamaTokenizer.from_pretrained(pretrained_model_name_or_path=model_dir, cache_dir="./", device_map="auto")

# Function to generate a response based on a given prompt
# max_new_tokens is a bit too much at 1024, so use between 512-1024
"""
def get_response(prompt) -> str:
    inputs = tokenizer(f"Q: {prompt} A:", return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=512)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
    
    """
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

def get_response(prompt) -> str:
    results = list(collection.aggregate([
        {"$vectorSearch": {
            "queryVector": generate_embedding(prompt),
            "path": "plot_embedding_hf",
            "numCandidates": 100,
            "limit": 4,
            "index": "LeadParagraphSemanticSearch",
        }}
    ]))

    if results:
        # Process the results to compile response snippets
        response_snippets = [doc["Lead_Paragraph"] for doc in results]
        response = "Found relevant information:\n" + "\n".join(["  * " + snippet for snippet in response_snippets])
    else:
        # Llama2 as fallback for response testing
        inputs = tokenizer(f"Q: {prompt} A:", return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=512)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
def introduce_chatbot():
    print ("Hei! Velkommen til forbrukertilsynets chatbot. Jeg er her for å svare på spørsmål, eller veilede deg til riktige ressurser dersom du trenger hjelp")

def main() -> None:
    introduce_chatbot()
    prompt = input("Still meg et spørsmål: ")
    response = get_response(prompt)
    print(f"Response: {response}")

    # Record the end time
    end = time.time()

    # Prints out the response and the total run time in seconds
    print(f"Response: {response}, time: {end - start}")

if __name__ == '__main__':
    main()