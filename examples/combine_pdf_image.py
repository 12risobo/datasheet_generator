from PyPDF2 import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from PIL import Image
import io

def create_pdf_with_image():
    # Create a new PDF with the image in landscape
    packet = io.BytesIO()
    page_width, page_height = landscape(letter)  # Switch to landscape
    c = canvas.Canvas(packet, pagesize=landscape(letter))
    
    # Get original image dimensions to calculate aspect ratio
    with Image.open('cable_drawing.png') as img:
        img_original_width, img_original_height = img.size
    
    # Calculate dimensions maintaining aspect ratio
    # Use 80% of page width as maximum width
    max_width = page_width * 0.8
    max_height = page_height * 0.8
    
    # Calculate scaling factor
    width_ratio = max_width / img_original_width
    height_ratio = max_height / img_original_height
    # Use the smaller ratio to ensure image fits on page
    scale_factor = min(width_ratio, height_ratio)
    
    # Calculate final dimensions
    img_width = img_original_width * scale_factor
    img_height = img_original_height * scale_factor
    
    # Position image at top center
    x = (page_width - img_width) / 2  # Center horizontally
    y = page_height - img_height - 50  # Position from top with 50pt margin
    
    c.drawImage('cable_drawing.png', x, y, width=img_width, height=img_height)
    c.save()
    
    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    return PdfReader(packet)

def main():
    # Create a new PDF with the image
    new_pdf = create_pdf_with_image()
    
    # Get the watermark from the existing PDF
    watermark_pdf = PdfReader('Watermerk.pdf')
    watermark_page = watermark_pdf.pages[0]
    
    # Create output PDF
    output = PdfWriter()
    
    # Get the page with the image
    page = new_pdf.pages[0]
    
    # Scale the watermark to 95% of its original size
    operation = Transformation().scale(0.95)
    watermark_page.add_transformation(operation)
    
    # Merge the watermark with the image page
    page.merge_page(watermark_page)
    
    # Add the merged page to the output
    output.add_page(page)
    
    # Write the output PDF
    with open('output.pdf', 'wb') as output_file:
        output.write(output_file)

if __name__ == "__main__":
    main() 