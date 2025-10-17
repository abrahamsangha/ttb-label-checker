from fasthtml.common import *
from monsterui.all import *

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
                    Input(name="net_contents", placeholder="e.g., 750 mL"),
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
    # TODO: Process image and verify
    return Container(
        Card(
            H2("Verification Results"),
            P(f"Brand: {brand_name}"),
            P(f"Type: {product_type}"),
            P(f"ABV: {alcohol_content}%"),
            P(f"Contents: {net_contents}"),
            P(f"Image: {label_image.filename}"),
        ),
        style="padding: 2rem;",
    )


serve()
