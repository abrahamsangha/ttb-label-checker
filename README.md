# TTB Label Verification App

AI-powered web application that simulates the Alcohol and Tobacco Tax and Trade Bureau (TTB) label approval process. The app verifies that information on alcohol beverage labels matches submitted form data.

## Overview

This application allows users to submit product information via a web form and upload a label image. Using OCR technology, it extracts text from the label and verifies that all required information matches the form submission, similar to how TTB agents review labels for compliance.

## Features

- **Web Form Interface**: Simple, responsive form for entering product details
  - Brand Name
  - Product Class/Type (e.g., Kentucky Straight Bourbon Whiskey)
  - Alcohol Content (% ABV)
  - Net Contents with unit selector (mL, L, oz, fl oz)
- **Image Upload**: Support for common image formats (JPEG, PNG, GIF)
- **OCR Processing**: Asynchronous text extraction using Tesseract OCR
- **Smart Verification**: Context-aware matching with regex patterns
- **Detailed Results**: Clear success/failure indicators with field-by-field breakdown
- **Error Handling**: Comprehensive validation and error messages
- **Responsive Design**: Mobile-friendly single-page application
- **Government Warning Check**: Verifies presence of mandatory health warning

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

Run all tests:

```
uv run pytest
```

Run specific test files:

```
uv run pytest tests/<test_file_name>
```

## Technical Approach

### OCR Implementation

The app uses **Tesseract OCR** via `pytesseract` for text extraction. The OCR service is implemented with an abstract base class (`OCRService`) to allow easy swapping of implementations.

**Async Processing**: OCR operations run asynchronously using `asyncio.to_thread()` to prevent blocking the server during CPU-intensive text extraction.

### Verification Logic

The verification process uses intelligent text matching:

1. **Case-insensitive matching**: All text comparisons ignore case differences
2. **Space normalization**: Removes spaces to handle OCR spacing errors
3. **Context-aware regex patterns**:
   - **Alcohol Content**: Looks for percentage near keywords like "alc", "abv", "vol", or "%"
   - **Net Contents**: Matches number with specific unit (e.g., "750" + "mL"), preventing false matches
4. **Government Warning**: Checks for both "government" and "warning" keywords

### Form Validation

Server-side validation includes:

- Alcohol content must be between 0-100%
- Image file must be provided and be a valid image type (JPEG, PNG, GIF)
- Net contents unit must be selected (not placeholder value)

### Key Assumptions & Design Decisions

1. **Fuzzy Matching**: The app allows minor OCR errors (spacing, case) but flags obvious mismatches
2. **Single Page App**: Uses HTMX for seamless form submission without page reload
3. **Mobile First**: Responsive design with vertical stacking on narrow screens

### Testing Approach

The project includes both unit and integration tests to ensure reliability:

#### Integration Tests (`test_ocr.py`)

- **Purpose**: Verify end-to-end OCR functionality with real Tesseract
- **Approach**: Generates test label images using PIL/Pillow with known text content
- **What's tested**:
  - Tesseract installation and basic functionality
  - Text extraction accuracy for brand names, product types, alcohol content, net contents, and government warnings
  - Real-world OCR behavior including common errors (spacing issues, character misreads)
- **Why integration**: Ensures the actual OCR library works correctly in the deployment environment

#### Unit Tests (`test_verifier.py`)

- **Purpose**: Test verification logic in isolation
- **Approach**: Uses mock OCR service that returns controlled text strings
- **What's tested**:
  - All fields matching successfully
  - Individual field mismatches (brand, alcohol content, net contents, warning)
  - Text normalization (handling spacing variations)
  - Whole number conversion (45.0 → 45)
- **Benefits**: Fast execution, deterministic results, no external dependencies

#### Validation Tests (`test_validation.py`)

- **Purpose**: Verify form input validation
- **Approach**: Uses mock upload file objects
- **What's tested**:
  - Valid inputs pass validation
  - Invalid alcohol content ranges (negative, >100%)
  - Missing or invalid image files
  - Invalid file types (non-images)
  - Missing unit selection

#### Test Philosophy

- **Integration tests** ensure the system works with real OCR
- **Unit tests** ensure business logic is correct and maintainable
- **Mocking** is used strategically to isolate components and speed up tests
- All async functions are properly tested with `pytest-asyncio`

### Known Limitations

- OCR accuracy depends on label image quality and text clarity
- Government warning check is basic (presence only, not exact text verification)
- No support for multiple beverage categories with different requirements
- Limited to English text recognition

## Project Structure

```
ttb-label-checker/
├── main.py              # FastHTML app with routes and UI
├── ocr_service.py       # OCR abstraction and implementations
├── verifier.py          # Label verification logic
├── utils/
│   └── form_validator.py # Form validation logic
├── tests/
│   ├── test_ocr.py      # Integration tests for OCR
│   ├── test_verifier.py # Unit tests for verification logic
│   └── test_validation.py # Tests for form validation
├── pyproject.toml       # Dependencies
├── uv.lock              # Locked dependency versions
└── README.md
```

## Technology Stack

- **Backend**: Python with FastHTML
- **UI Framework**: MonsterUI components
- **OCR**: Tesseract via pytesseract
- **Async**: asyncio for non-blocking operations
- **Testing**: pytest with pytest-asyncio
- **Frontend**: HTMX for dynamic updates

## Future Enhancements

### LLM-Based OCR

The codebase includes support for alternative OCR implementations. A `LlmOCR` class could be added to use vision-capable LLMs (GPT-4 Vision, Claude) for potentially more accurate text extraction.

Benefits:

- Better handling of complex layouts
- More context-aware text extraction
- Improved accuracy on stylized fonts

### Scalability with Job Queues

For high-traffic scenarios, OCR processing could be moved to a background job queue:

- Use Celery or RQ for async task processing
- Return immediate response with job ID
- Poll for results or use WebSockets for updates
- Our async OCR implementation already prepares for this architecture

### Additional Features

- **Detailed Compliance Checks**: Verify exact government warning text, check alcohol content descriptors
- **Multiple Product Types**: Different validation rules for beer, wine, spirits
- **Image Highlighting**: Visual indication of where text was found on label
- **Fuzzy String Matching**: Use edit distance for more forgiving comparisons
- **Label Image Preview**: Show uploaded image alongside results
- **Batch Processing**: Upload and verify multiple labels at once
- **Export Results**: Download verification report as PDF or CSV
