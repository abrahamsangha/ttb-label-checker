FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
  tesseract-ocr \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN uv sync

# Expose port
EXPOSE 5001

# Run the app
CMD ["uv", "run", "python", "main.py"]
