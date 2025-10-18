FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
  tesseract-ocr \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install uv && uv sync --frozen

# Copy the rest of the application
COPY . .

EXPOSE 5001

CMD ["python", "main.py"]
