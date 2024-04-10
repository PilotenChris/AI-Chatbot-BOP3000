import os
import torch  # type: ignore
import transformers
import time
import requests
from Db import collection, generate_embedding
from pymongo import MongoClient
from dotenv import dotenv_values
from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from transformers import LlamaTokenizer, AutoConfig, LlamaForCausalLM, pipeline, BitsAndBytesConfig
from torch import cuda, bfloat16

# feedback_uri = os.getenv('FEEDBACK_URL')
conversation_history: list = []

# Llama-2 from Hugging Face
model_dir = "RuterNorway/Llama-2-7b-chat-norwegian"

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

# Company name for the company using this chatbot
company: str = "Forbrukertilsynet"

# Template for use to make the chatbot follow what we want it to do
template: str = (f"Du er en hjelpsom medarbeider for {company} og vil hjelpe brukeren med å finne informasjon om "
                 f"spørsmålet, du skal bare bruke konteksten 'dataene fra {company}' til å svare på spørsmålet og "
                 f"linke til hvor brukeren kan finne flere svar.")


answer_indicator: str = "Svar:"

# Function to generate a response based on a given prompt
# max_new_tokens is a bit too much at 1024, so use between 512-1024
def generate_answer_with_context(question: str, context: str) -> str:
    inputs = tokenizer(f"{template}\n Kontekst: {context}\n Spørsmål: {question}\n. Svar:", return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=512)
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer: int = full_response.find(answer_indicator) + len(answer_indicator)
    response = full_response[answer:].strip()
    return response


def get_response(prompt: str) -> str:
    results: list = list(collection.aggregate([
        {"$vectorSearch": {
            "queryVector": generate_embedding(prompt),
            "path": "Lead_Paragraph_embedding_hf",
            "numCandidates": 50,
            "limit": 2,
            "index": "LeadParagraphSemanticSearch",
        }}
    ]))

    response: str


    if results:
        full_context: str = "Basert på dokumentene, oppsummer hovedavsnittet og list opp seksjonstitlene:\n"

        for idx, doc in enumerate(results, start=1):
            context = (f"\nDokument {idx} Tittel: '{doc['Title']}'\n"
                       f"Hovedavsnitt: '{doc['Lead_Paragraph']}'\n"
                       "Seksjonstitler:")

            section_titles: str = '\n'.join([f"- {para['Title']}" for para in doc.get("Paragraphs", [])])

            link: str = f"\nLes mer: https://www.forbrukertilsynet.no/{doc['link']}"

            full_context += f"{context}\n{section_titles}{link}\n"

        final_prompt: str = f"{full_context}\nSpørsmål: {prompt}\nSvar:"

        inputs = tokenizer(final_prompt, return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=512, pad_token_id=tokenizer.eos_token_id, temperature=0.01)
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        answer: int = full_response.rfind(answer_indicator) + len(answer_indicator)
        response = full_response[answer:].strip()
    else:
        response = "Beklager, jeg kunne ikke finne nok informasjon om spørsmålet ditt"

    return response


def feedback() -> str:
    print("\nØnsker du å gi en tilbakemelding på svaret du fikk? (y/n)")
    feedback_choice = input().lower()
    if feedback_choice == 'y':
        feedback_response = input("Din tilbakemelding: ")

        # Prepare data for API request
        data = {
            'conversation': '\n'.join(conversation_history),
            'feedback': feedback_response,
        }

        # Add feedback at end of conversation
        conversation_history.append(f"feedback: {feedback_response}")

        # Send POST request to Django API
        print(conversation_history)
        # response =  requests.post(feedback_uri, json=data)

    return "Takk for tilbakemeldingen!"


def introduce_chatbot():
    print(
        "Hei! Velkommen til forbrukertilsynets chatbot. Jeg er her for å svare på spørsmål, eller veilede deg til riktige ressurser dersom du trenger hjelp")


def main() -> None:
    introduce_chatbot()
    while (True):
        print("\n")
        prompt = input("Still meg et spørsmål: ")
        response = get_response(prompt)
        # For testing. To be replaced by button on webpage
        if prompt == 'stop':
            break

        # Prints out the response
        print(f"Svar: {response}")

    feedback()


if __name__ == '__main__':
    main()
