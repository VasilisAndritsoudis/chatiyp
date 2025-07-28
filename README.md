# ChatIYP

**ChatIYP** enables natural language interaction with the [Internet Yellow Pages (IYP)](https://iyp.iijlab.net/). It offers a conversational interface—built with Streamlit—allowing users to query structured internet infrastructure data using simple text.

## 🔍 What is ChatIYP?

ChatIYP is a natural language interface for the Internet Yellow Pages (IYP), allowing users to ask questions like:

> "Which ASes host root DNS servers?"

> "Show me IXPs in South America."

ChatIYP parses these queries, translates them into Cypher (the query language for Neo4j), and fetches the relevant results from IYP.

## 🧠 Powered by LlamaIndex

ChatIYP uses [LlamaIndex](https://www.llamaindex.ai/) to translate natural language questions into Cypher queries.  
**⚠️ Important:** To support this functionality, a patch must be applied:

Replace the original LlamaIndex file:

```bash
llama_index/core/indices/property_graph/sub_retrievers/text_to_cypher.py
```

with the custom version located in:

```bash
patched/text_to_cypher.py
```

This step is critical for ChatIYP to function correctly.

## ⚙️ Prerequisites

1. **Internet Yellow Pages (IYP)** must be installed and running locally. Follow the setup instructions here:  
   👉 [IYP GitHub Repo](https://github.com/InternetHealthReport/internet-yellow-pages)

2. Python 3.8+ and dependencies listed in `requirements.txt`

3. (Optional) Docker, if you prefer containerized deployment.

---

## 🚀 Getting Started

### 📦 Installation

Clone the repository:

```bash
git clone https://github.com/VasilisAndritsoudis/chatiyp
cd chatiyp
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Apply the patch to LlamaIndex:

```bash
cp patched/text_to_cypher.py path/to/llama_index/core/indices/property_graph/sub_retrievers/text_to_cypher.py
```

Make sure IYP is up and running locally as per its documentation.

### ▶️ Run the App

You can launch ChatIYP using Streamlit:

```bash
streamlit run app.py
```

Or using Docker:

```bash
docker compose up -d
```

Make sure both containers (iyp and chatiyp) are running on the same docker network.

## Results and Analysis

The results of the experiments and their analysis are available in the following formats:

- **Jupyter Notebook**: A summary of the results and analysis is provided in [performance_analysis/results.ipynb](https://github.com/VasilisAndritsoudis/chatiyp/blob/main/performance_analysis/results.ipynb).
- **Detailed Report**: A more in-depth analysis is available in the accompanying **Results Analysis PDF** file.

These resources offer insights into the system's performance, evaluation metrics, and key findings.

