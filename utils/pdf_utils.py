from PyPDF2 import PdfReader, PdfWriter

def add_watermark_to_pdf(input_pdf_path, watermark_pdf_path, output_pdf_path):
    """Add watermark from a PDF file to another PDF file."""
    # Get watermark from the first page
    watermark = PdfReader(watermark_pdf_path).pages[0]
    
    # Read the input PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Apply watermark to each page
    for page in reader.pages:
        page.merge_page(watermark)
        writer.add_page(page)

    # Write the output PDF
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file) 