FROM python:3.13-slim

# Install uv for ultra-fast package management
RUN pip install uv

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies with uv (10-100x faster than pip)
RUN uv pip install --system -r requirements.txt

# Copy application
COPY main.py .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]