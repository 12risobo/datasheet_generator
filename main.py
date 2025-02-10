import csv
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Table, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from PIL import Image as PILImage
from reportlab.lib import colors

def resize_image(image_path, max_width, max_height):
    with PILImage.open(image_path) as img:
        img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
        return img.size

def generate_datasheet(product_id, specs_data, items_data, image_path, output_dir):
    # Set up PDF
    doc = SimpleDocTemplate(f"{output_dir}/{product_id}_datasheet.pdf", 
                          pagesize=A4,
                          leftMargin=25*mm,
                          rightMargin=25*mm,
                          topMargin=25*mm,
                          bottomMargin=25*mm)
    story = []
    styles = getSampleStyleSheet()
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph(f"Product Datasheet: {product_id}", title_style))
    
    # Add technical drawing
    try:
        img_width, img_height = resize_image(image_path, 6*inch, 3*inch)
        tech_drawing = Image(image_path, width=img_width, height=img_height)
        story.append(tech_drawing)
        story.append(Spacer(1, 20))
    except FileNotFoundError:
        print(f"Image {image_path} not found. Skipping image.")

    # Add specs table with formatting
    story.append(Paragraph("Technical Specifications", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Format specs table
    filtered_specs = [row for row in specs_data if any(row)]  # Remove empty rows
    table_style = [
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]
    specs_table = Table(filtered_specs, colWidths=[doc.width/2.0]*2)
    specs_table.setStyle(table_style)
    story.append(specs_table)
    story.append(PageBreak())

    # Add product information table
    story.append(Paragraph("Product Information", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    header = items_data[0]  # Get header row
    current_product = [row for row in items_data[1:] if row[0] == product_id]
    
    if current_product:
        items_table = Table([header] + current_product,
                          colWidths=[doc.width/3.0]*3)
        items_table.setStyle(table_style)
        story.append(items_table)

    # Add footer
    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.grey
    )
    footer = Paragraph(
        f"Revision: 1.0 | Date: {datetime.now().strftime('%Y-%m-%d')} | Author: Your Name",
        footer_style
    )
    story.append(footer)

    doc.build(story)

def read_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader]

def main():
    specs_data = read_csv('data/specs.csv')
    items_data = read_csv('data/productrange.csv')
    output_dir = 'generated_datasheets'
    os.makedirs(output_dir, exist_ok=True)

    # Use the product codes from productrange.csv instead
    # Skip the first two rows (header and empty row)
    for product in items_data[2:]:
        product_id = product[0]  # Get the item code (e.g., RL9752)
        if product_id:  # Only process if product_id is not empty
            generate_datasheet(product_id, specs_data, items_data, 'assets/cable_drawing.png', output_dir)

if __name__ == "__main__":
    main() 