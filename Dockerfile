# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for better caching)
# If requirements don't change, Docker won't reinstall packages on every build
COPY requirements-docker.txt .

# Install all Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Pre-download embedding model so it's cached in the image
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')"

# Copy the rest of the project files
COPY . .

RUN python ingest.py

CMD ["python", "agent.py", "start"]