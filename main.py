from fasthtml.common import *
from monsterui.all import *
from ocr_service import TesseractOCR
from verifier import LabelVerifier
from utils.form_validator import validate_form

app, rt = fast_app(hdrs=(Theme.blue.headers(),), pico=False)


@rt("/")
def get():
    form = Form(
        Card(
            H2("TTB Label Verification"),
            DivVStacked(
                DivHStacked(
                    Label("Brand Name", cls="whitespace-nowrap"),
                    Input(
                        name="brand_name",
                        placeholder="e.g., Old Tom Distillery",
                        required=True,
                    ),
                    style="gap: 0.5rem;",
                ),
                DivHStacked(
                    Label("Product Class/Type", cls="whitespace-nowrap"),
                    Input(
                        name="product_type",
                        placeholder="e.g., Kentucky Straight Bourbon Whiskey",
                        required=True,
                    ),
                    style="gap: 0.5rem;",
                ),
                DivHStacked(
                    Label("Alcohol Content (%)", cls="whitespace-nowrap"),
                    Input(
                        name="alcohol_content",
                        type="number",
                        step="0.1",
                        placeholder="e.g., 45",
                        required=True,
                    ),
                    style="gap: 0.5rem;",
                ),
                DivHStacked(
                    Label("Net Contents", cls="whitespace-nowrap"),
                    Input(
                        name="net_contents", placeholder="e.g., 750 mL", required=True
                    ),
                    style="gap: 0.5rem;",
                ),
                DivHStacked(
                    Label("Upload Label Image", cls="whitespace-nowrap"),
                    Input(
                        name="label_image",
                        type="file",
                        accept="image/*",
                        required=True,
                    ),
                    style="gap: 0.5rem;",
                ),
                Button("Verify Label", type="submit", cls=ButtonT.primary),
                style="gap: 1.5rem; align-items: flex-start",
            ),
            style="max-width: 600px; text-align: left",
        ),
        method="post",
        action="/verify",
        enctype="multipart/form-data",
        cls="space-y-4",
    )

    return Container(form, style="padding: 2rem;")


@rt("/verify")
async def post(
    brand_name: str,
    product_type: str,
    alcohol_content: float,
    net_contents: str,
    label_image: UploadFile,
):
    error = validate_form(
        brand_name, product_type, alcohol_content, net_contents, label_image
    )
    if error:
        return error

    try:
        content = await label_image.read()

        ocr = TesseractOCR()
        image_text = ocr.extract_text(content)
        results = LabelVerifier(ocr).verify(
            {
                "brand_name": brand_name,
                "product_type": product_type,
                "alcohol_content": alcohol_content,
                "net_contents": net_contents,
            },
            content,
        )
        check_items = []
        for check in results["checks"]:
            icon = "✓" if check["found"] else "✗"
            color = "green" if check["found"] else "red"
            check_items.append(
                DivHStacked(
                    Span(
                        icon,
                        style=f"color: {color}; font-weight: bold; font-size: 1.5rem; margin-right: 1rem;",
                    ),
                    DivVStacked(
                        Strong(check["field"]),
                        Span(
                            f"Expected: {check['expected']}",
                            style="font-size: 0.9rem; color: #666;",
                        ),
                        style="gap: 0.25rem;",
                    ),
                    style="align-items: center; gap: 1rem; padding: 0.5rem 0;",
                )
            )

        # Overall status
        if results["success"]:
            status_card = Card(
                H3("✓ Verification Passed", style="color: green;"),
                P("All required information matches the label."),
                style="background-color: #f0fff0; border: 2px solid green;",
            )
        else:
            status_card = Card(
                H3("✗ Verification Failed", style="color: red;"),
                P("Some information does not match the label."),
                style="background-color: #fff0f0; border: 2px solid red;",
            )

        return Container(
            DivVStacked(
                status_card,
                Card(
                    H3("Verification Details"),
                    DivVStacked(*check_items, style="gap: 0.5rem;"),
                ),
                Details(
                    Summary("View Extracted Text"),
                    Pre(
                        image_text,
                        style="background: #f5f5f5; padding: 1rem; overflow-x: auto; color: #000;",
                    ),
                ),
                A("← Verify Another Label", href="/", style="margin-top: 1rem;"),
                style="gap: 1.5rem;",
            ),
            style="padding: 2rem;",
        )
    except Exception as e:
        return Container(
            Card(
                H3("❌ Processing Error", style="color: red;"),
                P(f"An error occurred while processing the image: {str(e)}"),
                P(
                    "Please try again with a different image or check that the image is readable."
                ),
                A("← Go Back", href="/"),
            )
        )


serve()
