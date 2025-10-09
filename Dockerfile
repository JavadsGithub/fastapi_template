FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Copy dependency files first (for better caching)
COPY pyproject.toml pdm.lock ./

# Install pdm and dependencies
RUN pip install pdm
RUN pdm install 

# Copy application code
COPY . /app

# Expose the correct port


# Run the application (remove --reload for production)
CMD ["pdm", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
