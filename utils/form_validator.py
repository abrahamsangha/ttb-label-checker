from fasthtml.common import *
from monsterui.all import *


def validate_form(alcohol_content, label_image, net_contents_unit):
    """Validate form inputs and return error UI if invalid, None if valid"""

    # Validate alcohol content
    if alcohol_content < 0 or alcohol_content > 100:
        return Container(
            Card(
                H3("❌ Validation Error", style="color: red;"),
                P("Alcohol content must be between 0 and 100%."),
                A("← Go Back", href="/"),
            ),
            style="padding: 2rem;",
        )

    # Validate image file
    if not label_image.filename:
        return Container(
            Card(
                H3("❌ Upload Error", style="color: red;"),
                P("Please upload a label image."),
                A("← Go Back", href="/"),
            ),
            style="padding: 2rem;",
        )
    if not net_contents_unit or net_contents_unit == "Select unit...":
        return Container(
            Card(
                H3("❌ Validation Error", style="color: red;"),
                P("Please select a unit for net contents."),
                A("← Go Back", href="/"),
            ),
            style="padding: 2rem;",
        )

    # Check file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif"]
    if label_image.content_type not in allowed_types:
        return Container(
            Card(
                H3("❌ File Type Error", style="color: red;"),
                P(f"Please upload an image file. Received: {label_image.content_type}"),
                A("← Go Back", href="/"),
            ),
            style="padding: 2rem;",
        )

    return None
