class LabelVerifier:
    def __init__(self, ocr_service):
        self.ocr_service = ocr_service

    def verify(self, form_data: dict, image_bytes: bytes) -> dict:
        extracted_text = self.ocr_service.extract_text(image_bytes)

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
        alcohol_content = form_data["alcohol_content"]
        if alcohol_content == int(alcohol_content):
            alcohol_str = str(int(alcohol_content))
        else:
            alcohol_str = str(alcohol_content)

        alcohol_found = alcohol_str in extracted_text
        results["checks"].append(
            {
                "field": "Alcohol Content",
                "expected": f"{alcohol_str}%",
                "found": alcohol_found,
            }
        )
        if not alcohol_found:
            results["success"] = False

        # Check net contents (if provided)
        if form_data.get("net_contents"):
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
