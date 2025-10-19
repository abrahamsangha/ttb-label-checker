import re


class LabelVerifier:
    def __init__(self, ocr_service):
        self.ocr_service = ocr_service

    def _add_check(self, results, field_name, expected_value, found):
        """Helper to add a check result"""
        results["checks"].append(
            {"field": field_name, "expected": expected_value, "found": found}
        )
        if not found:
            results["success"] = False

    def _check_net_contents(self, form_data, extracted_text):
        """Check if net contents from form matches extracted text"""
        import re

        form_match = re.search(r"(\d+\.?\d*)\s*([a-zA-Z.]+)", form_data["net_contents"])

        if not form_match:
            return False

        volume_number = form_match.group(1)
        volume_unit = form_match.group(2).lower().replace(".", "")

        # Normalize common unit variations
        unit_map = {"ml": "ml", "oz": "oz", "floz": "oz", "l": "l"}
        normalized_unit = unit_map.get(volume_unit, volume_unit)

        # Create pattern for the specific unit
        if normalized_unit == "ml":
            unit_pattern = r"(?:mL|ml|ML)"
        elif normalized_unit == "oz":
            unit_pattern = r"(?:oz|OZ|fl\.?\s*oz)"
        elif normalized_unit == "l":
            unit_pattern = r"(?:L|l)"
        else:
            unit_pattern = re.escape(volume_unit)

        volume_pattern = rf"\b{volume_number}\s{{0,3}}{unit_pattern}\b"
        return bool(re.search(volume_pattern, extracted_text, re.IGNORECASE))

    async def verify(self, form_data: dict, image_bytes: bytes) -> dict:

        extracted_text = await self.ocr_service.extract_text(image_bytes)
        extracted_lower = extracted_text.lower().replace(" ", "")

        results = {"success": True, "checks": [], "extracted_text": extracted_text}

        brand_normalized = form_data["brand_name"].lower().replace(" ", "")
        brand_found = brand_normalized in extracted_lower
        self._add_check(results, "Brand Name", form_data["brand_name"], brand_found)

        # Check product type
        product_normalized = form_data["product_type"].lower().replace(" ", "")
        product_found = product_normalized in extracted_lower
        self._add_check(
            results, "Product Type", form_data["product_type"], product_found
        )

        alcohol_value = form_data["alcohol_content"]
        if alcohol_value == int(alcohol_value):
            alcohol_str = str(int(alcohol_value))
        else:
            alcohol_str = str(alcohol_value)

        alcohol_pattern = rf"{alcohol_str}\s*%|\b{alcohol_str}\s*(?:alc|abv|alcohol)|\b{alcohol_str}\s*(?:proof)"
        alcohol_found = bool(re.search(alcohol_pattern, extracted_text, re.IGNORECASE))
        self._add_check(results, "Alcohol Content", f"{alcohol_str}%", alcohol_found)

        if form_data.get("net_contents"):
            contents_found = self._check_net_contents(form_data, extracted_text)
            self._add_check(
                results, "Net Contents", form_data["net_contents"], contents_found
            )

        warning_found = "government" in extracted_lower and "warning" in extracted_lower
        self._add_check(results, "Government Warning", "Present", warning_found)

        return results
