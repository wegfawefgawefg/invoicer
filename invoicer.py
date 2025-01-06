import os
import sys
import yaml
import argparse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime, timedelta


def load_yaml(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
    with open(file_path, "r") as file:
        try:
            data = yaml.safe_load(file)
            if data is None:
                print(f"Error: File '{file_path}' is empty.")
                sys.exit(1)
            return data
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file '{file_path}': {e}")
            sys.exit(1)


def validate_identity(identity, identity_type):
    required_fields = ["name"]
    optional_fields = ["address", "phone", "email"]

    # Check for missing required fields
    missing_required = [
        field
        for field in required_fields
        if field not in identity or not identity[field]
    ]
    if missing_required:
        print(
            f"Error: {identity_type} identity is missing required fields: {', '.join(missing_required)}."
        )
        sys.exit(1)

    # Check for missing optional fields and set them to empty strings
    for field in optional_fields:
        if field not in identity or not identity[field]:
            print(
                f"Warning: {identity_type} identity is missing optional field '{field}'. Using empty string."
            )
            identity[field] = ""


def calculate_totals(items, tax_rate):
    subtotal = sum(item["quantity"] * item["unit_price"] for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax
    return subtotal, tax, total


def parse_date(date_str):
    """
    Parses the input date string into a datetime object.
    Supports 'YYYY-MM-DD', 'YYYY/MM/DD', 'MM/DD/YYYY' formats.
    """
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    print(
        "Error: Date format is invalid. Please use 'YYYY-MM-DD', 'YYYY/MM/DD', or 'MM/DD/YYYY'."
    )
    sys.exit(1)


def nl2br(value):
    if value is None:
        return ""
    return value.replace("\n", "<br>\n")


def render_invoice(
    biller, billee, invoice, items, subtotal, tax, total, tax_rate, notes
):
    # Load the external HTML template
    env = Environment(loader=FileSystemLoader("templates"))
    env.filters["nl2br"] = nl2br
    try:
        template = env.get_template("invoice_template.html")
    except Exception as e:
        print(f"Error loading HTML template: {e}")
        sys.exit(1)

    rendered_html = template.render(
        biller=biller,
        billee=billee,
        invoice=invoice,
        items=items,
        subtotal=subtotal,
        tax=tax,
        total=total,
        tax_rate=tax_rate,
        notes=notes,
    )
    return rendered_html


def main():
    parser = argparse.ArgumentParser(description="Generate an invoice.")
    parser.add_argument(
        "--biller", required=True, help="Path to the biller's identity YAML file."
    )
    parser.add_argument(
        "--billee", required=True, help="Path to the billee's identity YAML file."
    )
    parser.add_argument("--items", required=True, help="Path to the items YAML file.")
    parser.add_argument(
        "--date",
        required=False,
        help="Invoice date in 'YYYY/MM/DD', 'YYYY-MM-DD', or 'MM/DD/YYYY' format.",
    )
    args = parser.parse_args()

    # Load data
    biller = load_yaml(args.biller)
    print("Biller Data:", biller)  # Debugging line
    billee = load_yaml(args.billee)
    print("Billee Data:", billee)  # Debugging line
    items_data = load_yaml(args.items)
    print("Items Data:", items_data)  # Debugging line

    # Validate identities
    validate_identity(biller, "Biller")
    validate_identity(billee, "Billee")

    # Validate items
    if not isinstance(items_data, list):
        print("Error: Items file should contain a list of items.")
        sys.exit(1)
    for idx, item in enumerate(items_data):
        required_item_fields = ["description", "quantity", "unit_price", "date"]
        missing_fields = [
            field
            for field in required_item_fields
            if field not in item or not item[field]
        ]
        if missing_fields:
            print(
                f"Error: Item at index {idx} is missing required fields: {', '.join(missing_fields)}."
            )
            sys.exit(1)

        # Parse and format the date
        parsed_date = parse_date(item["date"])
        # You can format the date as needed. For example, 'MM/DD/YYYY':
        item["date"] = parsed_date.strftime("%m/%d/%Y")

        # Optionally, validate quantity and unit_price
        if not isinstance(item["quantity"], (int, float)) or item["quantity"] < 0:
            print(
                f"Error: Item at index {idx} has invalid quantity '{item['quantity']}'. Must be a non-negative number."
            )
            sys.exit(1)
        if not isinstance(item["unit_price"], (int, float)) or item["unit_price"] < 0:
            print(
                f"Error: Item at index {idx} has invalid unit_price '{item['unit_price']}'. Must be a non-negative number."
            )
            sys.exit(1)

    # Determine invoice date
    if args.date:
        invoice_date = parse_date(args.date)
    else:
        invoice_date = datetime.now()

    # Extract invoice details
    invoice = {
        "number": f"INV-{invoice_date.strftime('%Y%m%d%H%M%S')}",  # Unique invoice number based on timestamp
        "date": invoice_date.strftime("%Y-%m-%d"),
        # 'due_date': (invoice_date + timedelta(days=30)).strftime('%Y-%m-%d'),  # Removed due_date
    }

    tax_rate = 0.0  # Set tax rate to 0% for now
    notes = "Thank you for your business!"

    # Calculate totals
    subtotal, tax, total = calculate_totals(items_data, tax_rate)

    # Render HTML
    rendered_html = render_invoice(
        biller, billee, invoice, items_data, subtotal, tax, total, tax_rate, notes
    )

    # Ensure 'outputs' directory exists
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
        print(f"Created directory: {outputs_dir}")

    # Save HTML
    html_filename = f"invoice_{invoice['number']}.html"
    html_path = os.path.join(outputs_dir, html_filename)
    with open(html_path, "w") as html_file:
        html_file.write(rendered_html)
    print(f"HTML Invoice generated successfully: {html_path}")

    # Convert to PDF
    pdf_filename = f"invoice_{invoice['number']}.pdf"
    pdf_path = os.path.join(outputs_dir, pdf_filename)
    try:
        HTML(string=rendered_html).write_pdf(pdf_path)
        print(f"PDF Invoice generated successfully: {pdf_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
