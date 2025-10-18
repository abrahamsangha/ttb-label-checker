from utils.form_validator import validate_form


class MockUploadFile:
    """Mock UploadFile for testing"""

    def __init__(self, filename, content_type):
        self.filename = filename
        self.content_type = content_type


def test_validate_form_with_valid_inputs():
    """Test that validation passes with valid inputs"""
    mock_file = MockUploadFile("label.png", "image/png")
    result = validate_form("Brand", "Type", 45.0, "750 mL", mock_file)
    assert result is None


def test_validate_form_with_invalid_alcohol_content_too_high():
    """Test validation fails when alcohol content is too high"""
    mock_file = MockUploadFile("label.png", "image/png")
    result = validate_form("Brand", "Type", 150.0, "750 mL", mock_file)
    assert result is not None


def test_validate_form_with_invalid_alcohol_content_negative():
    """Test validation fails when alcohol content is negative"""
    mock_file = MockUploadFile("label.png", "image/png")
    result = validate_form("Brand", "Type", -5.0, "750 mL", mock_file)
    assert result is not None


def test_validate_form_with_missing_image():
    """Test validation fails when no image is uploaded"""
    mock_file = MockUploadFile("", "image/png")
    result = validate_form("Brand", "Type", 45.0, "750 mL", mock_file)
    assert result is not None


def test_validate_form_with_invalid_file_type():
    """Test validation fails with non-image file"""
    mock_file = MockUploadFile("document.pdf", "application/pdf")
    result = validate_form("Brand", "Type", 45.0, "750 mL", mock_file)
    assert result is not None
