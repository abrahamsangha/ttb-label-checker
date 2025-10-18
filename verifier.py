import re


class LabelVerifier:
    def __init__(self, ocr_service):
        self.ocr_service = ocr_service

    async def verify(self, form_data: dict, image_bytes: bytes) -> dict:
        extracted_text = await self.ocr_service.extract_text(image_bytes)

        # Normalize text for comparison (remove spaces for fuzzy matching)
        extracted_lower = extracted_text.lower().replace(" ", "")

        results = {"success": True, "checks": [], "extracted_text": extracted_text}

        # Check brand name
        brand_normalized = form_data["brand_name"].lower().replace(" ", "")
        brand_found = brand_normalized in extracted_lower
        results["checks"].append(
            {
                "field": "Brand Name",
                "expected": form_data["brand_name"],
                "found": brand_found,
            }
        )
        if not brand_found:
            results["success"] = False

        # Check product type
        product_normalized = form_data["product_type"].lower().replace(" ", "")
        product_found = product_normalized in extracted_lower
        results["checks"].append(
            {
                "field": "Product Type",
                "expected": form_data["product_type"],
                "found": product_found,
            }
        )
        if not product_found:
            results["success"] = False

        # Check alcohol content
        alcohol_value = form_data["alcohol_content"]
        # Convert to int if it's a whole number (45.0 -> 45)
        if alcohol_value == int(alcohol_value):
            alcohol_str = str(int(alcohol_value))
        else:
            alcohol_str = str(alcohol_value)

        # Look for the alcohol percentage with context (%, ABV, alc, vol, etc.)
        alcohol_pattern = rf"{alcohol_str}\s*%|\b{alcohol_str}\s*(?:alc|abv|alcohol)|\b{alcohol_str}\s*(?:proof)"
        alcohol_found = bool(re.search(alcohol_pattern, extracted_text, re.IGNORECASE))

        results["checks"].append(
            {
                "field": "Alcohol Content",
                "expected": f"{alcohol_str}%",
                "found": alcohol_found,
            }
        )
        if not alcohol_found:
            results["success"] = False

        # Check net contents
        form_match = re.search(r"(\d+\.?\d*)\s*([a-zA-Z.]+)", form_data["net_contents"])

        if form_match:
            volume_number = form_match.group(1)
            volume_unit = form_match.group(2).lower().replace(".", "")  # normalize unit

            # Normalize common unit variations
            unit_map = {
                "ml": "ml",
                "oz": "oz",
                "floz": "oz",
                "l": "l",
            }
            normalized_unit = unit_map.get(volume_unit, volume_unit)

            # Look for the number AND unit together in extracted text
            # Create pattern for the specific unit with variations
            if normalized_unit == "ml":
                unit_pattern = r"(?:mL|ml|ML)"
            elif normalized_unit == "oz":
                unit_pattern = r"(?:oz|OZ|fl\.?\s*oz)"
            elif normalized_unit == "l":
                unit_pattern = r"(?:L|l)"
            else:
                unit_pattern = re.escape(volume_unit)

            # volume_pattern = rf"{volume_number}\s*{unit_pattern}"
            volume_pattern = rf"\b{volume_number}\s{{0,3}}{unit_pattern}\b"

            contents_found = bool(
                re.search(volume_pattern, extracted_text, re.IGNORECASE)
            )
        else:
            # Fallback
            contents_normalized = form_data["net_contents"].lower().replace(" ", "")
            contents_found = contents_normalized in extracted_lower

        results["checks"].append(
            {
                "field": "Net Contents",
                "expected": form_data["net_contents"],
                "found": contents_found,
            }
        )
        if not contents_found:
            results["success"] = False
        # Check for government warning
        warning_found = "government" in extracted_lower and "warning" in extracted_lower
        results["checks"].append(
            {
                "field": "Government Warning",
                "expected": "Present",
                "found": warning_found,
            }
        )
        if not warning_found:
            results["success"] = False

        return results
