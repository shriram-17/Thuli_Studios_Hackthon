import os
import re
import logging
import numpy as np
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from src.model.groq_api import GroqAPIWrapper  
from src.databases.qdrant import query_graph
import en_core_web_sm
import nltk
import wordcloud

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

def query_groq(user_query: str, data: pd.DataFrame, entity_counts: Counter, graph_type: str, graph_syntax: str) -> str:
    """
    Queries the Groq API with a user query and provided data,
    then processes and returns the path to the generated image.
    """
    # Convert DataFrame to a string representation
    grouped_commits = data.groupby('author')['message'].apply(lambda x: ' | '.join(x)).reset_index()
    data_summary = grouped_commits.to_string(index=False)

    # Create a summary of column names and their data types
    columns_info = {col: str(data[col].dtype) for col in data.columns}

    # Prepare the prompt for Groq API
    prompt = f"""
Given the following GitHub commit data sample (first few rows) from 'data/commits.csv':\n
{data[['sha', 'date', 'author', 'message']].head(2)}\n
The SHA represents the unique identifier for each commit. The 'date' is when the commit was made, 'author' is the name of the individual who made the commit, and 'message' describes the changes made in the commit. The visualization to be generated is of type {graph_type}. Please use the following syntax for creating it as a reference:\n
{graph_syntax}\n
Additional context:
- The data includes columns like 'date', 'author', and 'commits'.
- Info about columns is {columns_info}
- The query from the user is: "{user_query}"
- Ensure the code meets the following guidelines:
1. Provide complete executable Python code using only Plotly for the visualization.
2. Use the CSV file located at './src/data/commits.csv'.
3. Format the code correctly and avoid including extra explanations or headings.
4. For line charts, avoid using 'message_length' as a variable. Use 'date' and 'commits' for trends.
5. The code should not contain inline comments explaining what it does.
6. Provide visualizations based on the graph type requested (e.g., pie_chart, bar_chart, scatter_plot).
"""

    try:
        # Send the initial request to Groq API
        response = groq_api.query(prompt)

        # Prepare a second prompt to clean the code by removing explanations
        prompt_clean = f"""
Remove any explanation from this code, give me only code here, I don't want any like "Here is the Code" or "Python code" like something
{response}
"""
        response_cleaned = groq_api.query(prompt_clean)

        # Clean and format the generated code
        cleaned_code = response_cleaned
        cleaned_code = re.sub(r'```python', '', cleaned_code)
        cleaned_code = re.sub(r'```', '', cleaned_code)
        cleaned_code = re.sub(r'^\s*[\r\n]+', '', cleaned_code, flags=re.MULTILINE)  # Remove leading newlines
        cleaned_code = re.sub(r'\s*$', '', cleaned_code)  # Remove trailing whitespace
        cleaned_code = re.sub(r'(\n)+', '\n', cleaned_code)  # Remove multiple newlines
        print(cleaned_code)
        # Create a local context with necessary variables and modules
        local_context = {
            'pd': pd,
            'plt': plt,
            'np': np,
            'nltk': nltk,
            'data': data,
            'wordcloud': wordcloud,
            'entity_counts': entity_counts
        }

        # Execute the cleaned code in the local context
        exec(cleaned_code, local_context)

        # Return path to generated image if it exists
        if 'fig' in local_context:
            return local_context['fig']
        
    except Exception as e:
        logging.error(f"An error occurred in query_groq: {str(e)}")
        return f"An error occurred: {str(e)}"


def image_groq(user_query):
    # Load and preprocess data outside of Streamlit context for testing or other use cases.
    df = load_data()
    df, entity_counts = preprocess_commits(df)
    graph_type, graph_syntax = query_graph(user_query)
    
    return query_groq(user_query, df, entity_counts, graph_type, graph_syntax)
