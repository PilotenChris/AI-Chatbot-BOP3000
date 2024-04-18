import os  # type: ignore
import torch  # type: ignore
import transformers  # type: ignore
import time  # type: ignore
import requests  # type: ignore
from Db import collection, generate_embedding, collectionFeedback, noCase  # type: ignore
from pymongo import MongoClient  # type: ignore
from dotenv import dotenv_values  # type: ignore
from llama_index.core import SummaryIndex  # type: ignore
from llama_index.readers.mongodb import SimpleMongoReader  # type: ignore
from transformers import LlamaTokenizer, AutoConfig, LlamaForCausalLM, pipeline, BitsAndBytesConfig  # type: ignore
from torch import cuda, bfloat16  # type: ignore

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
device = torch.device("cuda" if cuda.is_available() else "cpu")

# Check if CUDA is available (for informational purposes)
print(cuda.is_available())

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

"""
# Template for use to make the chatbot follow what we want it to do
template: str = (f"Du er en hjelpsom medarbeider for {company} og vil hjelpe brukeren med å finne informasjon om "
                 f"spørsmålet, du skal bare bruke konteksten 'dataene fra {company}' til å svare på spørsmålet og "
                 f"linke til hvor brukeren kan finne flere svar.")
                 """

# Define a 'answer_indicator' marker to help find and extracting
# the answer portion from the full text generated by Llama-2
answer_indicator: str = "Svar:"


# Function to generate a response based on a given prompt
# max_new_tokens is a bit too much at 1024, so use between 512-1024
def generate_answer_with_context(final_prompt: str) -> str:
    # Use the tokenizer and model to generate a response based on the final prompt
    inputs = tokenizer(final_prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=512, pad_token_id=tokenizer.eos_token_id, temperature=0.01)
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Find the start index of the answer in the model's response and extract the answer
    answer: int = full_response.rfind(answer_indicator) + len(answer_indicator)
    response = full_response[answer:].strip()
    return response


# Function to answer question from the user about information on our website
def get_response(prompt: str) -> str:
    # Query the MongoDB collection for documents that match the user's prompt
    # using vector search for relevance based on the Lead Paragraph embeddings
    try:
        results: list = list(collection.aggregate([
            {"$vectorSearch": {
                "queryVector": generate_embedding(prompt),
                "path": "Lead_Paragraph_embedding_hf",
                "numCandidates": 1,
                "limit": 1,
                "index": "LeadParagraphSemanticSearch",
            }}
        ]))
    except ValueError:
        results = []

    # Initialize the response variable
    response: str

    # Check if the search query returned any results
    if results:
        full_context: str = "Basert på dette dokumentet, oppsummer innholdet:\n"

        # List to hold various parts of the document's content
        context_parts = []
        # String to hold formatted document context for the response
        document_context: str = ""

        for doc in results:
            # Add the document's title to the context
            context = f"\n{doc['Title']}"

            # Concatenate section titles from the document
            section_titles: str = '\n'.join([f"- {para['Title']}" for para in doc.get("Paragraphs", [])])

            # Format the link to the document
            link: str = f"\nLes mer: https://www.forbrukertilsynet.no{doc['link']}"

            # Combine the title, section titles, and the link into the document context
            document_context = f"\n{context}\n{section_titles}{link}\n"

            # Add the document's title and lead paragraph to context_parts
            context_parts.append(doc["Title"])
            context_parts.append(doc["Lead_Paragraph"])
            # Add each paragraph's title and content to context_parts
            for paragraph in doc.get("Paragraphs", []):
                context_parts.append(f" {paragraph['Title']}:")
                context_parts.append(f" {paragraph['paragraph']}")

        # Combine all parts of the context into a single string
        full_context += " ".join(context_parts)

        # Construct the final prompt with the combined context and the user's question
        final_prompt: str = f"{full_context}\nSpørsmål: {prompt}\nSvar:"

        response = generate_answer_with_context(final_prompt)
        # Append the document context to the model-generated response
        response += document_context
    else:
        # If no relevant documents were found, return an appropriate message
        response = "Beklager, jeg kunne ikke finne nok informasjon om spørsmålet ditt"

    return response


# Function to get the user to the right page about their question for complaints cases
def get_case_response(prompt: str) -> str:
    # Query the MongoDB collection for documents that match the user's prompt
    # using vector search for relevance based on the Lead Paragraph embeddings
    try:
        results: list = list(noCase.aggregate([
            {"$vectorSearch": {
                "queryVector": generate_embedding(prompt),
                "path": "Paragraph_embedding_hf",
                "numCandidates": 1,
                "limit": 1,
                "index": "NoCaseSemanticSearch",
            }}
        ]))
    except ValueError:
        results = []

    # Initialize the response variable
    response: str

    # Check if the search query returned any results
    # Check if the search query returned any results
    if results:
        full_context: str = "Basert på dette dokumentet, oppsummer innholdet angående oppdrag vi ikke tar:\n"

        # List to hold various parts of the document's content
        context_parts = []
        # String to hold formatted document context for the response
        document_context: str = ""

        for doc in results:
            # Add the document's title to the context
            context = f"\n{doc['Title']}"

            # Concatenate section titles from the document
            case: str = f'\nSend {doc["Case"]} til:'

            # Format the link to the document
            link: str = '\n'.join(doc.get("Link", []))

            # Combine the title, section titles, and the link into the document context
            document_context = f"\n{context}\n{case}{link}\n"

            # Add the document's title and lead paragraph to context_parts
            context_parts.append(doc["Title"])
            context_parts.append(doc["Paragraph"])

        # Combine all parts of the context into a single string
        full_context += " ".join(context_parts)

        # Construct the final prompt with the combined context and the user's question
        final_prompt: str = f"{full_context}\nSpørsmål: {prompt}\nSvar:"

        response = generate_answer_with_context(final_prompt)
        # Append the document context to the model-generated response
        response += document_context
    else:
        # If no relevant documents were found, return an appropriate message
        response = "Beklager, jeg kunne ikke finne nok informasjon om spørsmålet ditt"

    return response


def feedback() -> str:
    print("\nØnsker du å gi en tilbakemelding på svaret du fikk? (y/n)")
    feedback_choice = input().lower()
    if feedback_choice == 'y':
        feedback_response = input("Din tilbakemelding: ")

        # Prepearing data of conversation and feedback for the database
        feedback_data = {
            'Conversation': '\n'.join(conversation_history),
            'Feedback': feedback_response,
        }

        # Inserting the feedback data into the feedback collection
        collectionFeedback.insert_one(feedback_data)

    return "Takk for tilbakemeldingen!"


def introduce_chatbot():
    print(
        "Hei! Velkommen til forbrukertilsynets chatbot. Jeg er her for å svare på spørsmål, eller veilede deg til riktige ressurser dersom du trenger hjelp")


def main() -> None:
    try:
        introduce_chatbot()
        while (True):
            print("\n")
            prompt = input("Still meg et spørsmål: ")
            # For testing. To be replaced by button on webpage
            if prompt == 'stop':
                break
            conversation_history.append(f"Question: {prompt}")
            response = get_response(prompt)
            conversation_history.append(f"Answer: {response}")
            # Prints out the response
            print(f"Svar: {response}")

        feedback()
    except EOFError:
        pass


if __name__ == '__main__':
    main()
