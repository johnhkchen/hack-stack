FROM python:3.11-slim

# Install uv for ultra-fast package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* ./

# Install dependencies with uv  
RUN uv sync

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "8000"]