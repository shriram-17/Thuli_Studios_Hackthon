Here’s the updated README file with detailed explanations of the functions in `graph_agent.py`. You can copy this directly into your `README.md`:

```markdown
# GitHub Repository Data Collector

This repository contains a collection of Python scripts that interact with the GitHub API to extract repository data, analyze commits, pull requests, issues, and visualize data using Plotly. The project also integrates a Qdrant database for storing graph syntax templates and utilizing embeddings for query handling.

## Table of Contents

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Files Description](#files-description)
    - [github_collection.py](#github_collectionpy)
    - [text_agent.py](#text_agentpy)
    - [graph_agent.py](#graph_agentpy)
    - [qdrant.py](#qdrantpy)
- [License](#license)

## Project Structure

```
.
├── data                   # Directory for storing CSV files
├── .env                   # Environment variables
├── github_collection.py    # Script for collecting GitHub repository data
├── text_agent.py           # Agent for handling text-based queries
├── graph_agent.py          # Agent for generating visualizations
├── qdrant.py               # Qdrant integration and query handling
└── README.md               # Project documentation
```

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your_username/repo.git
    cd repo
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and add your GitHub token and Qdrant API key:
    ```plaintext
    GITHUB_TOKEN=your_github_token
    qdrant_api=your_qdrant_api_key
    ```

## Usage

1. Run the `github_collection.py` script to collect repository data:
    ```bash
    python github_collection.py
    ```

2. Utilize the `text_agent.py` and `graph_agent.py` to analyze and visualize data.

3. Use the `qdrant.py` file to handle queries related to graph types and their syntax.

## Files Description

### `github_collection.py`
This script collects data from GitHub repositories. It extracts commits, pull requests, and issues, calculates relevant metrics, and saves the data into CSV files. The main functions include:
- `extract_repo_info(url)`: Extracts the owner and repository name from the GitHub URL.
- `process_commit(commit)`: Processes individual commit data.
- `process_pull_request(pr)`: Processes individual pull request data.
- `process_issue(issue)`: Processes individual issue data.
- `collect_repo_data(owner, repo_name)`: Collects data from the specified GitHub repository.
- `calculate_metrics(commits_df, prs_df, issues_df)`: Calculates metrics from the collected data.

### `text_agent.py`
This agent is responsible for processing text-based queries and extracting relevant information from the collected data. Key functionalities include:
- NLP processing for named entity extraction.
- Query handling for commit data analysis.

### `graph_agent.py`
This agent generates visualizations based on provided data and user queries. It integrates with Plotly for creating dynamic visualizations. Key functions include:

#### `load_data()`
Loads and preprocesses commit data from a CSV file, converting date strings into datetime objects and calculating message lengths.

#### `extract_entities(text)`
Uses spaCy to extract named entities from a given text, focusing on organizations, products, geographical entities, and locations.

#### `preprocess_commits(df)`
Processes commit messages to extract key information using Named Entity Recognition (NER). It counts occurrences of each entity and extracts file changes if available.

#### `query_groq(user_query: str, data: pd.DataFrame, entity_counts: Counter, graph_type: str, graph_syntax: str) -> str`
Queries the Groq API with a user query and provided commit data. It prepares a prompt with context about the commit data and requested visualization type, sends it to Groq API, cleans up the generated code, executes it in a local context, and returns any generated images.

#### `image_groq(user_query)`
Main function that orchestrates loading commit data, preprocessing it, querying for graph types using Qdrant, and generating visualizations based on user queries.

### `qdrant.py`
This script integrates with Qdrant to manage graph types and their corresponding syntax for visualizations. Key functionalities include:
- `load_environment()`: Loads environment variables from a `.env` file.
- `initialize_qdrant_client()`: Initializes the Qdrant client for database interaction.
- `initialize_sentence_transformer()`: Initializes the SentenceTransformer model for embedding sentences.
- `get_plotly_graph_syntax()`: Provides syntax templates for various Plotly graph types.
- `query_graph_type(client, model, collection_name, user_description)`: Queries Qdrant to find the best matching graph type based on the user's description.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
```

### Key Points:
- Ensure that you customize any placeholder URLs or tokens in sections like Installation.
- Feel free to adjust descriptions or function explanations as needed to better fit your project's specifics or style preferences. Let me know if you need any further changes!
