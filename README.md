# Thuli Studios Hackathon Project

![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

A comprehensive GitHub repository analysis tool developed for the Thuli Studios Hackathon. This application provides insightful visualizations and metrics for repository data, including commits, pull requests, and developer activities.

## 🚀 Features

- GitHub repository data collection
- Commit and pull request analysis
- Developer activity metrics
- Natural Language Processing (NLP) for commit message analysis
- Interactive visualizations using Plotly
- Streamlit-based user interface

## 🛠 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shriram-17/Thuli_Studios_Hackthon.git
   cd Thuli_Studios_Hackthon
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory:
   ```plaintext
   GITHUB_TOKEN=your_github_token
   qdrant_api=your_qdrant_api_key
   ```

## 🖥 Usage

1. Collect repository data:
   ```bash
   python github_collection.py
   ```

2. Launch the application:
   ```bash
   streamlit run app.py
   ```

## 📁 File Structure and Detailed Descriptions

### `app.py`
The main application interface built with Streamlit. Key components include:

- `main()`: Controls the main workflow, including sidebar navigation and page rendering.
- `home_page()`: Allows users to enter a GitHub repository URL and fetches data.
- `commits_page()`: Displays commit data and visualizations with CSV export option.
- `pull_requests_page()`: Shows pull request data and visualizations with CSV export option.
- `nlp_module_page()`: Processes user queries about commit data using graph and text agents.
- `display_metrics()`: Renders key repository metrics in a card layout.
- `display_commit_visualizations()` and `display_pull_request_visualizations()`: Generate specific visualizations for commits and pull requests.
- `developer_page()`: Displays metrics and visualizations for developer activity.
- `classify(user_query: str)`: Determines if a user query requires a graph or text response.

### `github_collection.py`
Collects data from GitHub repositories, including commits, pull requests, and issues. Main functions:

- `extract_repo_info(url)`: Parses GitHub URLs to extract owner and repository name.
- `process_commit(commit)`, `process_pull_request(pr)`, `process_issue(issue)`: Process individual data points.
- `collect_repo_data(owner, repo_name)`: Collects comprehensive data from a specified repository.
- `calculate_metrics(commits_df, prs_df, issues_df)`: Computes various metrics from the collected data.

### `text_agent.py`
Processes text-based queries and extracts relevant information from collected data. Key functions:

- `load_data(file_path: str)`: Loads commit data from CSV and adds a message_length column.
- `extract_entities(text: str)`: Uses spaCy to extract named entities from commit messages.
- `categorize_commit(message: str)`: Categorizes commits into predefined types.
- `preprocess_commits(df: pd.DataFrame)`: Extracts entities and categorizes commits in bulk.
- `summarize_data(df: pd.DataFrame, top_n_authors: int, top_n_entities: int)`: Summarizes commit data by top authors and entities.
- `generate_response(user_query: str, grouped_commits: pd.DataFrame, top_entities: dict)`: Generates responses to user queries using the Groq API.

### `graph_agent.py`
Generates visualizations based on data and user queries using Plotly. Main functions:

- `load_data()`: Loads and preprocesses commit data from CSV.
- `extract_entities(text)`: Uses spaCy for Named Entity Recognition on commit messages.
- `preprocess_commits(df)`: Processes commit messages to extract key information and count entity occurrences.
- `query_groq(user_query: str, data: pd.DataFrame, entity_counts: Counter, graph_type: str, graph_syntax: str)`: Queries Groq API with user input and commit data to generate visualization code.
- `image_groq(user_query)`: Orchestrates the entire process of loading data, preprocessing, querying for graph types, and generating visualizations.

### `qdrant.py`
Manages graph types and their syntax for visualizations using Qdrant. Key functions:

- `load_environment()`: Loads environment variables from the .env file.
- `initialize_qdrant_client()`: Sets up the Qdrant client for database interactions.
- `initialize_sentence_transformer()`: Initializes the SentenceTransformer model for text embedding.
- `get_plotly_graph_syntax()`: Provides syntax templates for various Plotly graph types.
- `query_graph_type(client, model, collection_name, user_description)`: Queries Qdrant to find the best matching graph type based on user descriptions.

## 📊 Visualizations

### Commit Visualizations
- **Commit Timeline**: Tracks commit frequency over time.
- **Commit Frequency**: Shows commit patterns by hour, week, and month.
- **Commit Message Word Cloud**: Visualizes common terms in commit messages.

### Pull Request Visualizations
- **Additions and Deletions**: Bar plot comparing code added vs. removed.
- **Review Cycle Time**: Scatter plot showing PR review durations.
- **PR State Distribution**: Pie chart of open, closed, and merged PRs.
- **PR Complexity**: Bubble chart representing PR size and complexity.

## 🧠 NLP Module

The NLP module allows users to input natural language queries about commit data. It utilizes both graph and text agents to generate insightful responses and visualizations based on the query content.

## 👨‍💻 Developer Activity

Tracks and visualizes various aspects of developer contributions:
- Commit frequency per developer
- Lines of code added/removed
- Pull request involvement
- Issue resolution rates

## 📈 Metrics

Displays key repository metrics in a responsive card layout, including:
- Total commits and pull requests
- Average PR review time
- Most active contributors
- Repository growth rate
- Code churn

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/shriram-17/Thuli_Studios_Hackthon/issues).

## 📝 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

---

Developed with ❤️ for the Thuli Studios Hackathon
