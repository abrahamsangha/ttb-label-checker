import os
from fasthtml.common import *
from monsterui.all import *
from ocr_service import TesseractOCR
from verifier import LabelVerifier
from utils.form_validator import validate_form

app, rt = fast_app(hdrs=(Theme.blue.headers(),), pico=False)


def build_error_ui(title, message, show_back_link=True):
    """Build error card UI"""
    card_content = [
        H3(f"❌ {title}", style="color: red;"),
        P(message),
    ]
    if show_back_link:
        card_content.append(A("← Go Back", href="/"))

    return Container(Card(*card_content), style="padding: 2rem;")


def build_results_ui(results):
    """Build verification results UI"""
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

    # Overall status card
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
                    results["extracted_text"],
                    style="background: #f5f5f5; padding: 1rem; overflow-x: auto; color: #000; font-size: 0.9rem;",
                ),
            ),
            A("← Verify Another Label", href="/", style="margin-top: 1rem;"),
            style="gap: 1.5rem; align-items: flex-start;",
        ),
        style="padding: 2rem;",
    )


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
                    Label("Net Contents"),
                    DivHStacked(
                        Input(
                            name="net_contents_value",
                            type="number",
                            step="0.1",
                            placeholder="e.g., 750",
                            style="flex: 1;",
                            required=True,
                        ),
                        Select(
                            Option(
                                "Select unit...", value="", disabled=True, selected=True
                            ),
                            Option("mL", value="mL"),
                            Option("L", value="L"),
                            Option("oz", value="oz"),
                            Option("fl oz", value="fl oz"),
                            name="net_contents_unit",
                            style="flex: 0 0 100px;",
                            required=True,
                        ),
                        style="gap: 0.5rem; display: flex;",
                    ),
                    style="gap: 0.5rem;",
                ),
                DivVStacked(
                    Label("Upload Label Image", cls="whitespace-nowrap"),
                    Input(
                        name="label_image",
                        type="file",
                        accept="image/*",
                        required=True,
                    ),
                    style="gap: 0.5rem; align-items: flex-start;",
                ),
                Button("Verify Label", type="submit", cls=ButtonT.primary),
                style="gap: 1.5rem; align-items: flex-start;",
            ),
            style="max-width: 600px; text-align: left",
        ),
        enctype="multipart/form-data",
        cls="space-y-4",
        hx_post="/verify",
        hx_target="#results",
        hx_swap="innerHTML show:#results:top smooth",
    )
    return Container(
        Style(
            """
            .htmx-request ~ #results {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 200px;
            }
            .htmx-request ~ #results::after {
                content: '';
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        """
        ),
        form,
        Div(id="results"),
        style="padding: 2rem;",
    )


@rt("/verify")
async def post(
    brand_name: str,
    product_type: str,
    alcohol_content: float,
    net_contents_value: float,
    net_contents_unit: str,
    label_image: UploadFile,
):
    error = validate_form(alcohol_content, label_image, net_contents_unit)
    if error:
        return error

    try:
        if net_contents_value == int(net_contents_value):
            net_contents = f"{int(net_contents_value)} {net_contents_unit}"
        else:
            net_contents = f"{net_contents_value} {net_contents_unit}"

        content = await label_image.read()
        ocr = TesseractOCR()

        results = await LabelVerifier(ocr).verify(
            {
                "brand_name": brand_name,
                "product_type": product_type,
                "alcohol_content": alcohol_content,
                "net_contents": net_contents,
            },
            content,
        )

        return build_results_ui(results)

    except Exception as e:
        return build_error_ui(
            "Processing Error",
            f"An error occurred while processing the image: {str(e)}. Please try again with a different image or check that the image is readable.",
        )


serve(port=int(os.getenv("PORT", 5001)))
