from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_invoice(order):
    file_name = f"invoice_{order['id']}.pdf"

    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"Invoice - Order #{order['id']}", styles["Title"]))
    content.append(Paragraph(f"Total: ₹{order['total']}", styles["Normal"]))

    for item in order["items"]:
        content.append(
            Paragraph(f"{item['name']} x{item['quantity']} - ₹{item['price']}", styles["Normal"])
        )

    doc.build(content)

    return file_name