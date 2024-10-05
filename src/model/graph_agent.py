import os
import re
import logging
import numpy as np
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from src.model.groq_api import GroqAPIWrapper  
import en_core_web_sm

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Check for Groq API key
api_key = os.getenv("groq_token")
if not api_key:
    raise ValueError("Groq API token not found in environment variables")

# Initialize Groq API wrapper
groq_api = GroqAPIWrapper(api_key)

# Load spaCy model
nlp = en_core_web_sm.load()

def load_data():
    """
    Loads and preprocesses the commit data from a CSV file.
    """
    df = pd.read_csv("./src/data/commits.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['message_length'] = df['message'].str.len()
    return df

def extract_entities(text):
    """
    Extracts named entities from text using spaCy.
    """
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'LOC']]

def preprocess_commits(df):
    """
    Preprocesses commit messages to extract key information using NER.
    """
    # Extract entities from commit messages
    df['entities'] = df['message'].apply(extract_entities)
    
    # Count occurrences of each entity
    entity_counts = Counter([entity for entities in df['entities'] for entity in entities])
    
    # Extract file changes if available
    df['files_changed'] = df['message'].str.extract(r'Files changed:\s*(.*)')
    
    return df, entity_counts

def query_groq(user_query: str, data: pd.DataFrame, entity_counts: Counter) -> str:
    """
    Queries the Groq API with a user query and provided data,
    then processes and returns the path to the generated image.
    """
    # Convert DataFrame to a string representation
    grouped_commits = data.groupby('author')['message'].apply(lambda x: ' | '.join(x)).reset_index()
    data_summary = grouped_commits.to_string(index=False)
    
    # Prepare the prompt for Groq API
    prompt = f"""
    Given the following sample of GitHub commit data (first few rows) from the file 'data/commits.csv':\n
    {data_summary}\n
    Additional context:
    - Entities (technologies, organizations, locations) mentioned in commit messages and their frequencies: {dict(entity_counts)}
    
    Please answer the following query and provide Python code using only Plotly to generate interactive visualizations based on the commit data.
    Ensure the code adheres to these guidelines:
    1. The code should be complete and executable as is.
    2. Use only Plotly for visualizations.
    3. Only Give Me Code Here No Output or any Explanation
    4. Path of the CSV File is "./src/data/commits.csv" 
    Here is the query: {user_query}
    """
    
    try:
        # Send the request to Groq API
        response = groq_api.query(prompt)

        # Clean and format the generated code
        cleaned_code = response
        cleaned_code = re.sub(r'```python', '', cleaned_code)
        cleaned_code = re.sub(r'```', '', cleaned_code)
        cleaned_code = re.sub(r'^\s*[\r\n]+', '', cleaned_code, flags=re.MULTILINE)  # Remove leading newlines
        cleaned_code = re.sub(r'\s*$', '', cleaned_code)  # Remove trailing whitespace
        
        # Create a local context with necessary variables and modules
        local_context = {
            'pd': pd,
            'plt': plt,
            'np': np,
            'data': data,
            'entity_counts': entity_counts
        }
        
        # Execute the cleaned code in the local context
        exec(cleaned_code, local_context)
        
        # Return path to generated image if it exists
        if 'fig' in local_context:
            return local_context['fig']
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

def image_groq(user_query):
    # Load and preprocess data outside of Streamlit context for testing or other use cases.
    df = load_data()
    df, entity_counts = preprocess_commits(df)

    return query_groq(user_query, df, entity_counts)
