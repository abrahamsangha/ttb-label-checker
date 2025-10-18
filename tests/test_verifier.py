import pytest
from ocr_service import OCRService
from verifier import LabelVerifier


class MockOCR(OCRService):
    """Mock OCR for testing without actual image processing"""

    def __init__(self, text_to_return):
        self.text_to_return = text_to_return

    async def extract_text(self, image_bytes: bytes) -> str:
        return self.text_to_return


@pytest.mark.asyncio
async def test_verify_all_fields_match():
    """Test successful verification when all fields match"""
    mock_text = """
    HAMMER WHISKEY
    Kentucky Straight Bourbon Whiskey
    45% Alc./Vol.
    750 mL
    GOVERNMENT WARNING: According to the Surgeon General...
    """

    ocr = MockOCR(mock_text)
    verifier = LabelVerifier(ocr)

    form_data = {
        "brand_name": "Hammer Whiskey",
        "product_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol_content": 45.0,
        "net_contents": "750 mL",
    }

    results = await verifier.verify(form_data, b"fake_image_bytes")

    assert results["success"] == True
    assert len(results["checks"]) == 5
    assert all(check["found"] for check in results["checks"])


@pytest.mark.asyncio
async def test_verify_brand_name_mismatch():
    """Test failure when brand name doesn't match"""
    mock_text = """
    DIFFERENT BRAND
    Kentucky Straight Bourbon Whiskey
    45% Alc./Vol.
    750 mL
    GOVERNMENT WARNING
    """

    ocr = MockOCR(mock_text)
    verifier = LabelVerifier(ocr)

    form_data = {
        "brand_name": "Hammer Whiskey",
        "product_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol_content": 45.0,
        "net_contents": "750 mL",
    }

    results = await verifier.verify(form_data, b"fake_image_bytes")

    assert results["success"] == False
    brand_check = next(c for c in results["checks"] if c["field"] == "Brand Name")
    assert brand_check["found"] == False


@pytest.mark.asyncio
async def test_verify_missing_alcohol_content():
    """Test failure when alcohol content is missing"""
    mock_text = """
    HAMMER WHISKEY
    Kentucky Straight Bourbon Whiskey
    750 mL
    GOVERNMENT WARNING
    """

    ocr = MockOCR(mock_text)
    verifier = LabelVerifier(ocr)

    form_data = {
        "brand_name": "Hammer Whiskey",
        "product_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol_content": 45.0,
        "net_contents": "750 mL",
    }

    results = await verifier.verify(form_data, b"fake_image_bytes")

    assert results["success"] == False
    alcohol_check = next(
        c for c in results["checks"] if c["field"] == "Alcohol Content"
    )
    assert alcohol_check["found"] == False


@pytest.mark.asyncio
async def test_verify_missing_government_warning():
    """Test failure when government warning is missing"""
    mock_text = """
    HAMMER WHISKEY
    Kentucky Straight Bourbon Whiskey
    45% Alc./Vol.
    750 mL
    """

    ocr = MockOCR(mock_text)
    verifier = LabelVerifier(ocr)

    form_data = {
        "brand_name": "Hammer Whiskey",
        "product_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol_content": 45.0,
        "net_contents": "750 mL",
    }

    results = await verifier.verify(form_data, b"fake_image_bytes")

    assert results["success"] == False
    warning_check = next(
        c for c in results["checks"] if c["field"] == "Government Warning"
    )
    assert warning_check["found"] == False


@pytest.mark.asyncio
async def test_verify_handles_spacing_variations():
    """Test that verifier handles OCR spacing issues"""
    # OCR often removes spaces
    mock_text = """
    HAMMERWHISKEY
    KentuckyStraightBourbonWhiskey
    45%Alc./Vol.
    750mL
    GOVERNMENTWARNING
    """

    ocr = MockOCR(mock_text)
    verifier = LabelVerifier(ocr)

    form_data = {
        "brand_name": "Hammer Whiskey",
        "product_type": "Kentucky Straight Bourbon Whiskey",
        "alcohol_content": 45.0,
        "net_contents": "750 mL",
    }

    results = await verifier.verify(form_data, b"fake_image_bytes")

    # Should still match because we normalize by removing spaces
    assert results["success"] == True


@pytest.mark.asyncio
async def test_verify_whole_number_alcohol_content():
    """Test that 45.0 is converted to 45 for matching"""
    mock_text = """
    HAMMER WHISKEY
    Bourbon
    45% Alc./Vol.
    750 mL
    GOVERNMENT WARNING
    """

    ocr = MockOCR(mock_text)
    verifier = LabelVerifier(ocr)

    form_data = {
        "brand_name": "Hammer Whiskey",
        "product_type": "Bourbon",
        "alcohol_content": 45.0,  # Should match "45" in text
        "net_contents": "750 mL",
    }

    results = await verifier.verify(form_data, b"fake_image_bytes")

    alcohol_check = next(
        c for c in results["checks"] if c["field"] == "Alcohol Content"
    )
    assert alcohol_check["found"] == True
