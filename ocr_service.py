import asyncio
import io
import pytesseract
from abc import ABC, abstractmethod
from PIL import Image
from google import genai


class OCRService(ABC):
    @abstractmethod
    async def extract_text(self, image_bytes: bytes) -> str:
        """Extract raw text from image"""
        pass


class TesseractOCR(OCRService):
    async def extract_text(self, image_bytes: bytes) -> str:

        image = Image.open(io.BytesIO(image_bytes))
        text = await asyncio.to_thread(pytesseract.image_to_string, image)
        return text


class LlmOCR(OCRService):
    def __init__(self, api_key=None):
        self.client = genai.Client()

    async def extract_text(self, image_bytes: bytes) -> str:

        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        prompt = "Extract all text from this alcohol beverage label image. Include brand name, product type, alcohol content, volume, warnings, and any other text visible on the label. Return just the text you see."

        def generate():
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=[prompt, image]
            )
            return response.text or ""

        return await asyncio.to_thread(generate)
