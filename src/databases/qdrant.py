import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def load_environment():
    load_dotenv()

def initialize_qdrant_client():
    try:
        return QdrantClient(
            url="https://153485d9-e06d-4545-b026-01bc5778ec9a.europe-west3-0.gcp.cloud.qdrant.io:6333", 
            api_key=os.getenv("qdrant_api"),
        )
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")
        return None

def initialize_sentence_transformer():
    return SentenceTransformer('all-MiniLM-L6-v2')

def get_plotly_graph_syntax():
    return {
        "pie_chart": {
            "description": "Pie chart that represents the proportion of items in each category.",
            "syntax": """
import plotly.express as px

fig = px.pie(df, names='category_column', values='value_column', title='Distribution by Category')
fig.show()
            """
        },
        "bar_chart": {
            "description": "Bar chart for showing categorical data with rectangular bars.",
            "syntax": """
import plotly.express as px

fig = px.bar(df, x='category_column', y='value_column', title='Values by Category')
fig.show()
            """
        },
        "line_chart": {
            "description": "Line chart that shows data trends over time or another continuous variable.",
            "syntax": """
import plotly.express as px

fig = px.line(df, x='x_column', y='y_column', title='Trend Over Time/Variable')
fig.show()
            """
        },
        "scatter_plot": {
            "description": "Scatter plot showing relationships between two variables.",
            "syntax": """
import plotly.express as px

fig = px.scatter(df, x='x_column', y='y_column', title='Relationship Between Variables')
fig.show()
            """
        },
        "box_plot": {
            "description": "Box plot to show distribution of numerical data and identify outliers.",
            "syntax": """
import plotly.express as px

fig = px.box(df, x='category_column', y='value_column', title='Distribution and Outliers')
fig.show()
            """
        },
        "histogram": {
            "description": "Histogram to show the distribution of a single numerical variable.",
            "syntax": """
import plotly.express as px

fig = px.histogram(df, x='value_column', title='Distribution of Values')
fig.show()
            """
        },
        "heatmap": {
            "description": "Heatmap to visualize the magnitude of a phenomenon as color in two dimensions.",
            "syntax": """
import plotly.express as px

fig = px.imshow(df.corr(), title='Correlation Heatmap')
fig.show()
            """
        },
        "3d_scatter": {
            "description": "3D scatter plot to show relationships between three variables.",
            "syntax": """
import plotly.express as px

fig = px.scatter_3d(df, x='x_column', y='y_column', z='z_column', title='3D Relationship')
fig.show()
            """
        },
        "bubble_chart": {
            "description": "Bubble chart to show relationships between three or four variables.",
            "syntax": """
import plotly.express as px

fig = px.scatter(df, x='x_column', y='y_column', size='size_column', color='color_column', 
                 hover_name='name_column', title='Multi-variable Relationship')
fig.show()
            """
        },
        "violin_plot": {
            "description": "Violin plot to visualize the distribution of data across several groups.",
            "syntax": """
import plotly.express as px

fig = px.violin(df, x='category_column', y='value_column', box=True, points="all", 
                title='Distribution Across Categories')
fig.show()
            """
        }
    }

def query_graph_type(client, model, collection_name, user_description):
    try:
        user_embedding = model.encode(user_description).tolist()
        results = client.search(
            collection_name=collection_name,
            query_vector=user_embedding,
            limit=1
        )

        if results:
            best_match = results[0]
            return best_match.payload['type'], best_match.payload['syntax']
        else:
            return None, None
    except Exception as e:
        print(f"Error querying graph type: {e}")
        return None, None

def query_graph(user_query):
    load_environment()
    client = initialize_qdrant_client()
    if not client:
        return

    model = initialize_sentence_transformer()
    collection_name = "plotly_graphs"
    return query_graph_type(client, model, collection_name, user_query)

