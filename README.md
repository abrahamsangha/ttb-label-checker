# TTB Label Verification App

AI-powered web application for verifying alcohol beverage labels against form data.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Tesseract OCR

### Install Tesseract

**Mac:**

```
brew install tesseract
```

**Ubuntu/Debian:**

```
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

## Installation

```
uv sync
```

To activate the python environment:

```
source .venv/bin/activate
```

## Running the App

```
uv run python main.py
```

Then open your browser to the URL shown in the terminal (typically http://localhost:5001).

## Testing

```
pytest
```
