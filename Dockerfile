FROM python:3.13

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY . .

# Replace the original LlamaIndex file with your patched version
# Make sure the version and Python match your local environment
RUN cp patched/text_to_cypher.py \
    /usr/local/lib/python3.13/site-packages/llama_index/core/indices/property_graph/sub_retrievers/text_to_cypher.py

# Run Streamlit app
CMD streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
