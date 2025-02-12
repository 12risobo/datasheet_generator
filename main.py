from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Table, Paragraph, PageBreak, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import csv
import os
from datetime import datetime

# Update font registration with proper paths
font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
calibri_regular = os.path.join(font_dir, 'calibri.ttf')
calibri_bold = os.path.join(font_dir, 'calibrib.ttf')

# Register Calibri fonts
pdfmetrics.registerFont(TTFont('Calibri', calibri_regular))
pdfmetrics.registerFont(TTFont('Calibri-Bold', calibri_bold))

def resize_image(image_path, max_width, max_height):
    with PILImage.open(image_path) as img:
        img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
        return img.size

def generate_datasheet(product_id, specs_data, items_data, image_path, output_dir):
    # Set up PDF - switch to landscape by swapping width and height
    doc = SimpleDocTemplate(f"{output_dir}/{product_id}_datasheet.pdf", 
                          pagesize=(A4[1], A4[0]),  # Landscape
                          leftMargin=25*mm,
                          rightMargin=25*mm,
                          topMargin=25*mm,
                          bottomMargin=25*mm)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Add technical drawing with 1.75x size
    try:
        img_width, img_height = resize_image(image_path, 10.5*inch, 5.25*inch)  # 6*1.75=10.5, 3*1.75=5.25
        tech_drawing = Image(image_path, width=img_width, height=img_height)
        story.append(tech_drawing)
        story.append(Spacer(1, 20))
    except FileNotFoundError:
        print(f"Image {image_path} not found. Skipping image.")

    # Define section headers we want to identify
    section_headers = [
        'Specifications cable (A)',
        'Specifications Connector (B, C)',
        'Specifications fiber',
        'Specifications optical performance',
        'Standard compliances'
    ]

    # Group specs data by sections
    current_section = None
    sections = {}
    
    for row in specs_data:
        if not any(row):  # Skip empty rows
            continue
        if row[0] in section_headers:
            current_section = row[0]
            sections[current_section] = []
        elif current_section and len(row) == 2:  # Only add rows with 2 columns
            sections[current_section].append(row)

    # Add each section as a separate table
    story.append(Paragraph("Technical Specifications", styles['Heading2']))
    story.append(Spacer(1, 10))

    # Calculate table width (73% of available width)
    table_width = doc.width * 0.73
    col_width = table_width / 2.0  # Split into two equal columns

    # Updated table style with specific fonts, colors, and reduced row heights
    table_style = [
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Regular cell styling
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Calibri'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),  # Reduced from 8
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # Reduced from 8
        
        # Header row styling
        ('SPAN', (0, 0), (1, 0)),  # Span the header across both columns
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#104861')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('FONTNAME', (0, 0), (1, 0), 'Calibri'),
        ('FONTSIZE', (0, 0), (1, 0), 10),
        ('FONTWEIGHT', (0, 0), (1, 0), 'BOLD'),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
    ]

    for section_title, section_data in sections.items():
        if section_data:  # Only create table if there's data
            # Create table data with header row
            table_data = [[section_title, '']]  # Empty string for second column in header
            table_data.extend(section_data)
            
            # Create and style table with new dimensions
            section_table = Table(table_data, 
                                colWidths=[col_width]*2,
                                spaceBefore=5,
                                spaceAfter=5)
            section_table.setStyle(table_style)
            # Wrap table in KeepTogether
            story.append(KeepTogether([section_table, Spacer(1, 5)]))

    # Create a list to hold the product information section
    product_info_section = []
    
    # Add product information table
    product_info_section.append(Paragraph("Product Information", styles['Heading2']))
    product_info_section.append(Spacer(1, 10))
    
    # Get header and all non-empty rows (skip the second empty row)
    header = items_data[0]
    all_products = [row for row in items_data[2:] if any(row)]  # Get all non-empty rows
    
    # Calculate how many columns we want (e.g., 4 pairs of columns)
    num_column_pairs = 4
    total_columns = num_column_pairs * 2  # Each pair has Item and Length
    
    # Prepare data for the table
    table_data = []
    
    # Add header rows for each column pair
    header_row = []
    for _ in range(num_column_pairs):
        header_row.extend(header)
    table_data.append(header_row)
    
    # Calculate how many rows we need
    products_per_column = (len(all_products) + num_column_pairs - 1) // num_column_pairs
    
    # Fill in the product data
    for row_idx in range(products_per_column):
        row_data = []
        for col_idx in range(num_column_pairs):
            product_idx = row_idx + (col_idx * products_per_column)
            if product_idx < len(all_products):
                row_data.extend(all_products[product_idx])
            else:
                row_data.extend(['', ''])  # Empty cells for padding
        table_data.append(row_data)
    
    # Calculate column widths (distribute evenly across the table width)
    col_width = table_width / total_columns
    
    # Create and style table
    items_table = Table(table_data,
                       colWidths=[col_width] * total_columns,
                       spaceBefore=5,
                       spaceAfter=5)
    
    # Modify table style to handle multiple columns
    table_style_items = [
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Calibri'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#104861')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Calibri'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTWEIGHT', (0, 0), (-1, 0), 'BOLD'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
    ]
    
    items_table.setStyle(table_style_items)
    product_info_section.append(items_table)

    # Try to keep all content together, but allow page break if it doesn't fit
    try:
        story.append(KeepTogether(product_info_section))
    except:
        # If it doesn't fit, add a page break before the product information
        story.append(PageBreak())
        story.extend(product_info_section)

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