import io
import pytest
from PIL import Image, ImageDraw, ImageFont
from ocr_service import TesseractOCR


def generate_test_label():
    """Generate a simple whiskey label image with PIL"""
    img = Image.new("RGB", (700, 900), color="white")
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70
        )
        font_medium = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45
        )
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28
        )
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    y_position = 120
    draw.text(
        (350, y_position), "HAMMER WHISKEY", fill="black", font=font_large, anchor="mm"
    )

    y_position += 120
    draw.text(
        (350, y_position),
        "Kentucky Straight Bourbon Whiskey",
        fill="black",
        font=font_medium,
        anchor="mm",
    )

    y_position += 100
    draw.text(
        (350, y_position), "45% Alc./Vol.", fill="black", font=font_medium, anchor="mm"
    )

    y_position += 100
    draw.text((350, y_position), "750 mL", fill="black", font=font_medium, anchor="mm")

    y_position += 150
    draw.text(
        (350, y_position),
        "GOVERNMENT WARNING",
        fill="black",
        font=font_small,
        anchor="mm",
    )
    y_position += 40
    warning = "According to the Surgeon General, women should not\ndrink alcoholic beverages during pregnancy because\nof the risk of birth defects."
    draw.text(
        (350, y_position),
        warning,
        fill="black",
        font=font_small,
        anchor="mm",
        align="center",
    )

    return img


@pytest.mark.asyncio
async def test_ocr_can_extract_brand_name():
    """Test that OCR extracts brand name"""
    img = generate_test_label()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")

    ocr = TesseractOCR()
    extracted_text = await ocr.extract_text(img_bytes.getvalue())

    assert "hammer" in extracted_text.lower()


@pytest.mark.asyncio
async def test_ocr_can_extract_product_type():
    """Test that OCR extracts product type"""
    img = generate_test_label()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")

    ocr = TesseractOCR()
    extracted_text = await ocr.extract_text(img_bytes.getvalue())

    assert "bourbon" in extracted_text.lower() or "whiskey" in extracted_text.lower()


@pytest.mark.asyncio
async def test_ocr_can_extract_alcohol_content():
    """Test that OCR extracts alcohol content"""
    img = generate_test_label()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")

    ocr = TesseractOCR()
    extracted_text = await ocr.extract_text(img_bytes.getvalue())

    assert "45" in extracted_text


@pytest.mark.asyncio
async def test_ocr_can_extract_net_contents():
    """Test that OCR extracts net contents"""
    img = generate_test_label()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")

    ocr = TesseractOCR()
    extracted_text = await ocr.extract_text(img_bytes.getvalue())

    assert "750" in extracted_text and "ml" in extracted_text.lower()


@pytest.mark.asyncio
async def test_ocr_can_extract_government_warning():
    """Test that OCR extracts government warning"""
    img = generate_test_label()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")

    ocr = TesseractOCR()
    extracted_text = await ocr.extract_text(img_bytes.getvalue())

    assert "governmentwarning" in extracted_text.lower()


def save_test_label(id=None):
    """Helper to save test label for inspection"""
    img = generate_test_label()
    img.save(f"test_label_{id}.png")
    print(f"Test label saved as test_label_{id}.png")
