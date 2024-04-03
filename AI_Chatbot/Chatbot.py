import torch  # type: ignore
import transformers
import time
from Db import collection, generate_embedding
from pymongo import MongoClient
from dotenv import dotenv_values
from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from transformers import LlamaTokenizer, AutoConfig, LlamaForCausalLM, pipeline, BitsAndBytesConfig
from torch import cuda, bfloat16


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
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer: int = full_response.find("A:") + 2
    response = full_response[answer:].strip()
    return response
    """


def get_response(prompt) -> str:
    results = list(collection.aggregate([
        {"$vectorSearch": {
            "queryVector": generate_embedding(prompt),
            "path": "Lead_Paragraph_embedding_hf",
            "numCandidates": 100,
            "limit": 4,
            "index": "LeadParagraphSemanticSearch",
        }}
    ]))

    if results:
        # Process the results to compile response snippets
        response_snippets = [doc["Lead_Paragraph"] for doc in results]
        response = "\n" + "\n".join(["  * " + snippet for snippet in response_snippets])
    else:
        # Llama2 as fallback for response testing
        inputs = tokenizer(f"Q: {prompt} A:", return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=512)
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer: int = full_response.find("A:") + 2
        response = full_response[answer:].strip()
    return response

def feedback() -> str:
    print("\nØnsker du å gi en tilbakemelding på svaret du fikk? (y/n)")
    feedback_choice = input().lower()
    if feedback_choice == 'y':
        feedback_response = input("Din tilbakemelding: ")
        print(feedback_response)
    return "Takk for tilbakemeldingen!"

def introduce_chatbot():
    print ("Hei! Velkommen til forbrukertilsynets chatbot. Jeg er her for å svare på spørsmål, eller veilede deg til riktige ressurser dersom du trenger hjelp")

def main() -> None:
    introduce_chatbot()
    while(True):
        print("\n")
        prompt = input("Still meg et spørsmål: ")
        response = get_response(prompt)

        # Prints out the response and the total run time in seconds
        print(f"Svar: {response}")
        feedback()

if __name__ == '__main__':
    main()