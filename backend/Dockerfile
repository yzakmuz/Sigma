FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .

# Copy application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the initialization script and then start FastAPI
CMD ["sh", "-c", "python math_app/scripts/init_db.py && uvicorn math_app.app.main:app --host 0.0.0.0 --port 8000"]
