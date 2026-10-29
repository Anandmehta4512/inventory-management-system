import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_gst_invoice(order_id: str, customer_name: str, items: list, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Title Style
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#003366'),
        alignment=1,
        spaceAfter=10
    )

    story.append(Paragraph("TAX INVOICE - ZOHO INVENTORY", title_style))
    story.append(Paragraph(f"<b>Order ID:</b> {order_id} | <b>Customer:</b> {customer_name}", styles['Normal']))
    story.append(Spacer(1, 15))

    # Table data
    table_data = [["Item Description", "Qty", "Price (₹)", "Total (₹)"]]
    subtotal = 0.0

    for item in items:
        name = item.get('name', 'Product')
        qty = item.get('quantity', 1)
        price = item.get('price', 0.0)
        total = qty * price
        subtotal += total
        table_data.append([name, str(qty), f"{price:.2f}", f"{total:.2f}"])

    cgst = subtotal * 0.09
    sgst = subtotal * 0.09
    grand_total = subtotal + cgst + sgst

    table_data.append(["Subtotal", "", "", f"{subtotal:.2f}"])
    table_data.append(["CGST (9%)", "", "", f"{cgst:.2f}"])
    table_data.append(["SGST (9%)", "", "", f"{sgst:.2f}"])
    table_data.append(["Grand Total", "", "", f"{grand_total:.2f}"])

    t = Table(table_data, colWidths=[250, 60, 100, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-5), colors.HexColor('#F2F5F8')),
        ('GRID', (0,0), (-1,-5), 0.5, colors.grey),
        ('LINEBELOW', (0,-4), (-1,-1), 1, colors.HexColor('#003366')),
        ('FONTNAME', (0,-4), (-1,-1), 'Helvetica-Bold'),
    ]))

    story.append(t)
    doc.build(story)
    return output_path
