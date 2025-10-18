import io
import pytesseract
from abc import ABC, abstractmethod
from PIL import Image


class OCRService(ABC):
    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> str:
        """Extract raw text from image"""
        pass


class TesseractOCR(OCRService):
    def extract_text(self, image_bytes: bytes) -> str:

        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text
