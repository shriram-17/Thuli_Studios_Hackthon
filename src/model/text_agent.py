import pandas as pd
import logging
import json
import os
from collections import Counter
from dotenv import load_dotenv
import en_core_web_sm
from langchain_core.prompts import PromptTemplate
from src.model.groq_api import GroqAPIWrapper  # Ensure this module is correctly implemented

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Environment Variables
load_dotenv()

# Retrieve Groq API Key
api_key = os.getenv("GROQ_TOKEN")  # Ensure the environment variable name matches
if not api_key:
    raise ValueError("Groq API token not found in environment variables.")

# Initialize Groq API Wrapper
groq_api = GroqAPIWrapper(api_key)

# Load spaCy Model
nlp = en_core_web_sm.load()

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load commit data from a CSV file.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded commit data with additional message_length column.
    """
    try:
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        df['message_length'] = df['message'].str.len()
        logger.info("Data loaded successfully.")
        return df
    except Exception as e:
        logger.exception(f"Failed to load data from {file_path}: {str(e)}")
        raise

def extract_entities(text: str) -> list:
    """
    Extract entities from commit messages using spaCy.

    Args:
        text (str): Commit message text.

    Returns:
        list: List of extracted entities.
    """
    try:
        doc = nlp(text)
        return [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'LOC']]
    except Exception as e:
        logger.exception(f"Failed to extract entities from text: {text[:50]}... Error: {str(e)}")
        return []

def categorize_commit(message: str) -> str:
    """
    Categorize commit messages into predefined categories.

    Args:
        message (str): Commit message text.

    Returns:
        str: Category of the commit.
    """
    message_lower = message.lower()
    if any(keyword in message_lower for keyword in ['fix', 'bug', 'resolve', 'error']):
        return "Bug Fix"
    elif any(keyword in message_lower for keyword in ['add', 'implement', 'feature', 'create']):
        return "Feature Addition"
    elif any(keyword in message_lower for keyword in ['update', 'docs', 'documentation', 'readme']):
        return "Documentation"
    elif 'merge' in message_lower:
        return "Merge"
    elif 'chore' in message_lower:
        return "Chore"
    else:
        return "Other"

def preprocess_commits(df: pd.DataFrame) -> tuple:
    """
    Preprocess commit data by extracting entities, categorizing commits, and counting their frequencies.

    Args:
        df (pd.DataFrame): Raw commit data.

    Returns:
        tuple: Preprocessed DataFrame and Counter object of entity frequencies.
    """
    try:
        # Extract entities
        df['entities'] = df['message'].apply(extract_entities)

        # Categorize commits
        df['category'] = df['message'].apply(categorize_commit)

        # Count entity frequencies
        entity_counts = Counter([entity for entities in df['entities'] for entity in entities])

        logger.info("Preprocessing completed successfully.")
        return df, entity_counts
    except Exception as e:
        logger.exception(f"Failed to preprocess commits: {str(e)}")
        raise

def summarize_data(df: pd.DataFrame, top_n_authors: int = 5, top_n_entities: int = 10) -> tuple:
    """
    Summarize commit data by selecting top authors and top entities to reduce data volume.

    Args:
        df (pd.DataFrame): Preprocessed commit data.
        top_n_authors (int): Number of top authors to include.
        top_n_entities (int): Number of top entities to include.

    Returns:
        tuple: Summarized DataFrame and limited entity counts.
    """
    try:
        # Select top N authors by commit count
        top_authors = df['author'].value_counts().nlargest(top_n_authors).index
        df_top_authors = df[df['author'].isin(top_authors)]

        # Further aggregate commit messages by author
        grouped_commits = df_top_authors.groupby('author').agg({
            'message': lambda msgs: ' | '.join(msgs),
            'category': lambda cats: ', '.join(sorted(set(cats)))
        }).reset_index()

        # Limit entity counts to top N
        entity_counts = Counter([entity for entities in df_top_authors['entities'] for entity in entities])
        top_entities = dict(entity_counts.most_common(top_n_entities))

        logger.info("Data summarized successfully.")
        return grouped_commits, top_entities
    except Exception as e:
        logger.exception(f"Failed to summarize data: {str(e)}")
        raise

def generate_response(user_query: str, grouped_commits: pd.DataFrame, top_entities: dict) -> str:
    """
    Generate a response to the user's query using Groq API.

    Args:
        user_query (str): The user's question or request.
        grouped_commits (pd.DataFrame): Summarized commit data grouped by author.
        top_entities (dict): Top entities and their frequencies.

    Returns:
        str: Response generated by the Groq API.
    """
    logger.info("Generating response using Groq API.")

    try:
        # Convert grouped data to a concise string format
        data_summary = ""
        for _, row in grouped_commits.iterrows():
            data_summary += f"Author: {row['author']}\n"
            data_summary += f"Categories: {row['category']}\n"
            data_summary += f"Messages: {row['message'][:100]}... | \n"  # Truncate messages to reduce tokens
            data_summary += "\n"

        # Prepare prompt using LangChain's PromptTemplate with further token reduction
        prompt_template = PromptTemplate(
            template=(
                "You are analyzing GitHub commit data. Below is a summary of commit messages grouped by author along with their commit categories.\n\n"
                "{data_summary}\n\n"
                "Additional context:\n"
                "- Top Entities (technologies, organizations, locations) mentioned in commit messages and their frequencies: {entity_counts}\n\n"
                "Please answer the following query concisely:\n"
                "{user_query}\n\n"
                "Provide your answer in a clear and concise manner."
            ),
            input_variables=["data_summary", "entity_counts", "user_query"]
        )

        # Format the prompt with actual data
        prompt = prompt_template.format(
            data_summary=data_summary,
            entity_counts=top_entities,
            user_query=user_query
        )

        # Optionally, further summarize the prompt to reduce tokens
        # For example, limit the data_summary to a certain number of lines or characters
        if len(prompt) > 3000:  # Assuming a token limit around 4096
            prompt = prompt[:3000] + "..."

        # Query the Groq API
        response = groq_api.query(prompt)
        logger.info("Response generated successfully.")
        return response.strip()

    except Exception as e:
        logger.error(f"Error occurred while querying Groq API: {str(e)}")
        return f"An error occurred while generating the response: {str(e)}"

def load_products(file_path: str) -> dict:
    """
    Load products from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Loaded products data.
    """
    try:
        with open(file_path, 'r') as file:
            products = json.load(file)
        logger.info("Products loaded successfully.")
        return products
    except Exception as e:
        logger.exception(f"Failed to load products from {file_path}: {str(e)}")
        raise

def save_products(file_path: str, products: dict):
    """
    Save the updated products to a JSON file.

    Args:
        file_path (str): Path to the JSON file.
        products (dict): Products data to save.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(products, file, indent=4)
        logger.info("Products saved successfully.")
    except Exception as e:
        logger.exception(f"Failed to save products to {file_path}: {str(e)}")
        raise

def generate_text_response(user_query_input: str) -> str:
    """
    Main function to generate a text response based on user query.

    Args:
        user_query_input (str): The user's query.

    Returns:
        str: The generated response.
    """
    try:
        # Load and preprocess the data
        df = load_data("./src/data/commits.csv")
        df, entity_counts = preprocess_commits(df)

        # Summarize data to reduce tokens
        grouped_commits, top_entities = summarize_data(df, top_n_authors=5, top_n_entities=10)

        # Generate response
        response = generate_response(user_query_input, grouped_commits, top_entities)
        return response

    except Exception as e:
        logger.error(f"An error occurred in the main execution: {str(e)}")
        return f"An error occurred while processing your request: {str(e)}"

