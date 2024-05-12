# AI Chatbot for Forbrukertilsynet (AI Chatbot for the Norwegian Consumer Protection Authority)

## Project Overview
This Bachelor project, developed at the University of South-Eastern Norway (USN) Bø, was commissioned by Forbrukertilsynet (Norwegian Consumer Protection Authority) to prototype an AI chatbot. This chatbot is designed to assist consumers by helping them navigate the authority's website to find necessary information and determine the appropriate avenue for making complaints.

### Objectives
- **Explore AI Chatbot Technologies**: Experiment with Llama-2 and RAG technologies to create a functional AI chatbot prototype.
- **Identify and Overcome Challenges**: Address and document the challenges faced during the development, particularly those related to hardware limitations.
- **Prepare for Future Development**: Gather insights and knowledge that will aid in the full-scale development of a consumer-oriented AI chatbot for Forbrukertilsynet.

## Hardware Limitations
During the development, we encountered several limitations due to our PC hardware setup:
- **Model Training**: Inability to train our custom version of Llama-2 with Forbrukertilsynet data.
- **Data Extraction**: Challenges using RAG for data extraction from MongoDB, affecting the control over the format of responses.
- **Document Handling**: Constraints in processing multiple documents from MongoDB concurrently.
- **Query Limitations**: Limited to answering one type of question at a time due to data organization in MongoDB.

## Project Setup

### Prerequisites
- Windows OS with WSL 2 and Ubuntu installed.
- Python 3.11 installed within a Conda environment.
- PyTorch installed with appropriate CUDA version based on your Nvidia Graphics card.

### Environment Setup
1. **Install WSL 2 and Ubuntu**: Follow [Microsoft's WSL Installation Guide](https://docs.microsoft.com/en-us/windows/wsl/install).
2. **Create and Activate Conda Environment on both Windows and WSL 2 Ubuntu**:
```bash
conda create --name your_env_name python=3.11
conda activate your_env_name
```
3. **Install PyTorch**:
- Visit [PyTorch's Official Site](https://pytorch.org/get-started/locally/) and follow the installation instructions for Linux/Windows with Conda.
4. **Additional Dependencies**:
Navigate to the root directory of the project, where the `requirements.txt` file is located, then run the following commands to install the necessary Python packages:
```bash
conda install -c anaconda protobuf
pip install -r requirements.txt
```
### Configure Environment Variables
Ensure you create a `.env` file in both `/REST/` and `/AI_Chatbot/` folders with the following fields:

- `MONGO_URI=your_mongodb_uri` — URI for connecting to MongoDB.
- `USER_NAME=your_mongodb_username` — Username for MongoDB.
- `PASSWORD=your_mongodb_password` — Password for MongoDB.
- `SECRET_KEY=your_django_secret_key` — Secret key for Django.
- `HF_TOKEN=your_huggingface_token` — Token for accessing Hugging Face models.
- `SMTP_USERNAME=your_email_username` — Username for email service.
- `SMTP_PASS=your_email_password` — Password for email service.
- `EMBEDDING_URL=your_huggingface_api_url` — URL for Hugging Face API inference.
### Running the Project
- **Django REST API**: Navigate to `/REST/` and execute:
```bash
python manage.py runserver
```
- **Test Website**: Navigate to `/Website/chatbot/`, then execute:
```bash
npm install
npm start
```
### Running only the chatbot for testing/development
- **WSL 2 Ubuntu**: Navigate to `/AI_Chatbot/` and execute:
```bash
python Chatbot.py
```

## MongoDB Structure
- **TrainingData Collection**:
```json
{
  "link": "/document-url",
  "Tags": ["Tag1", "Tag2", "Tag3"],
  "Title": "Document Title",
  "Lead_Paragraph": "This is the lead paragraph of the document.",
  "Published": "2024-03-01",
  "Updated": "2024-03-05",
  "Paragraphs": [
    {"Title": "Section Title 1", "paragraph": "This is the first section."},
    {"Title": "Section Title 2", "paragraph": "This is the second section."}
  ]
}
```
- **NoCase Collection**:
```json
{
  "Title": "Case Title",
  "Case": "Complaint or tips",
  "Paragraph": "Detailed case paragraph",
  "Link": ["URLs to case-specific actions"]
}
```
## Contributon
Feel free to fork this project, clone it, or incorporate it into your own work. As this was developed as a Bachelor project, there may not be further updates or active maintenance.
## License
This project is open-sourced under the MIT License. See the [LICENSE](LICENSE) file for more details.
