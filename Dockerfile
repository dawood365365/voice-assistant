# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for better caching)
# If requirements don't change, Docker won't reinstall packages on every build
COPY requirements-docker.txt .

# Install all Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy the rest of the project files
COPY . .

# Expose port 5000 for Flask server
EXPOSE 5000