import pandas as pd
import logging
import json
import os
from collections import Counter
from dotenv import load_dotenv
import en_core_web_sm
from langchain_core.prompts import PromptTemplate
from src.model.groq_api import GroqAPIWrapper  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for Groq API key
api_key = os.getenv("GROQ_TOKEN")  # Ensure the environment variable name matches
if not api_key:
    raise ValueError("Groq API token not found in environment variables.")

# Initialize Groq API wrapper
groq_api = GroqAPIWrapper(api_key)

# Load spaCy model
nlp = en_core_web_sm.load()

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load commit data from a CSV file.
    """
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df['message_length'] = df['message'].str.len()
    logger.info("Data loaded successfully.")
    return df

def extract_entities(text: str) -> list:
    """
    Extract entities from commit messages using spaCy.
    """
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'LOC']]

def preprocess_commits(df: pd.DataFrame) -> tuple:
    """
    Preprocess commit data by extracting entities and counting their frequencies.
    """
    df['entities'] = df['message'].apply(extract_entities)
    entity_counts = Counter([entity for entities in df['entities'] for entity in entities])
    return df, entity_counts

def generate_response(user_query: str, data: pd.DataFrame, entity_counts: Counter) -> str:
    """
    Generate a response to the user's query using Groq API.
    """
    logger.info("Generating response using Groq API.")

    # Group commit messages by author
    grouped_commits = data.groupby('author')['message'].apply(lambda x: ' | '.join(x)).reset_index()
    data_summary = grouped_commits.to_string(index=False)

    # Prepare prompt using LangChain's PromptTemplate
    prompt_template = PromptTemplate(
        template=(
            "Given the following GitHub commit data:\n\n"
            "{data_summary}\n\n"  # Use summary instead of full data
            "Additional context:\n"
            "- Entities (technologies, organizations, locations) mentioned in commit messages and their frequencies: {entity_counts}\n"
            "Please answer the following query:\n"
            "{user_query}\n\n"
            "Provide your answer in a clear, concise manner."
        ),
        input_variables=["data_summary", "entity_counts", "user_query"]
    )

    prompt = prompt_template.format(
        data_summary=data_summary,
        entity_counts=dict(entity_counts),
        user_query=user_query
    )
    
    try:
        response = groq_api.query(prompt)
        return response.strip()
    except Exception as e:
        logger.error(f"Error occurred while querying Groq API: {str(e)}")
        return f"An error occurred: {str(e)}"

def load_products(file_path):
    """
    Load products from a JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def save_products(file_path, products):
    """
    Save the updated products to a JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(products, file, indent=4)

def generate_text_response(user_query_input: str):
    try:
        # Load and preprocess the data
        df = load_data("./src/data/commits.csv")
        df, entity_counts = preprocess_commits(df)
       
        response = generate_response(user_query_input, df, entity_counts)
        return response
        
    except Exception as e:
        logger.error(f"An error occurred in the main execution: {str(e)}")
