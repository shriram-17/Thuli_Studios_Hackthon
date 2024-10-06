
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
### `app.py`
This file serves as the main application interface with several key functions:

#### Main Function (main)
Controls the main workflow of the application, including sidebar navigation and page rendering.

#### Home Page Function (home_page)
Allows users to enter a GitHub repository URL to fetch data. It parses the repository URL and collects relevant metrics to display.

#### Commits Page Function (commits_page)
Displays commit data along with visualizations. Provides users with an option to export this commit data to a CSV file for offline use.

#### Pull Requests Page Function (pull_requests_page)
Displays pull request data along with visualizations. Offers an option to export pull request data to a CSV file.

#### NLP Module Page Function (nlp_module_page)
Allows users to input queries about commit data. Utilizes both graph and text agents to generate responses based on user queries.

#### Display Metrics Function (display_metrics)
Renders key metrics related to the GitHub repository in a responsive card layout.

#### Display Visualizations Functions:
- **Commit Visualizations (display_commit_visualizations)**: Generates and displays visualizations specifically for commit data.
- **Pull Request Visualizations (display_pull_request_visualizations)**: Similar to commit visualizations but tailored for pull requests.

#### Developer Activity Page Function (developer_page)
Displays metrics and visualizations related to developer activity within the repository.

#### Graph State and Nodes Functions
Defines the structure of the graph state and includes logic for classifying user input as requiring either a graph or text response.
Helper Functions: - **classify(user_query: str)**: Classifies user input to determine if it requires a graph or text response.
  
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
- `load_data()` : Loads and preprocesses commit data from a CSV file, converting date strings into datetime objects and calculating message lengths.
- `extract_entities(text)`: Uses spaCy to extract named entities from a given text, focusing on organizations, products, geographical entities, and locations.
- `preprocess_commits(df)` Processes commit messages to extract key information using Named Entity Recognition (NER). It counts occurrences of each entity and extracts file changes if available.
- `query_groq(user_query: str, data: pd.DataFrame, entity_counts: Counter, graph_type: str, graph_syntax: str) -> str` Queries the Groq API with a user query and provided commit data. It prepares a prompt with       context about the commit data and requested visualization type, sends it to the Groq API, cleans up the generated code, executes it in a local context, and returns any generated images.
- `image_groq(user_query)` : Main function that orchestrates loading commit data, preprocessing it, querying for graph types using Qdrant, and generating visualizations based on user queries.

### `qdrant.py`
This script integrates with Qdrant to manage graph types and their corresponding syntax for visualizations. Key functionalities include:
- `load_environment()`: Loads environment variables from a `.env` file.
- `initialize_qdrant_client()`: Initializes the Qdrant client for database interaction.
- `initialize_sentence_transformer()`: Initializes the SentenceTransformer model for embedding sentences.
- `get_plotly_graph_syntax()`: Provides syntax templates for various Plotly graph types.
- `query_graph_type(client, model, collection_name, user_description)`: Queries Qdrant to find the best matching graph type based on the user's description.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
