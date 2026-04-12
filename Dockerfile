FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --system -r <(uv pip compile pyproject.toml)

# Copy application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "math_app.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
