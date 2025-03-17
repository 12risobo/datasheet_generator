from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.units import mm
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class TemplateManager:
    """Manages PDF templates, frames, and page decorations."""
    
    def __init__(self):
        """Initialize the template manager."""
        self.assets_dir = Path(__file__).parent.parent / 'assets'
        self.fonts_dir = Path(__file__).parent.parent / 'fonts'
        self.register_fonts()
    
    def init_doc(self, product_id, output_dir):
        """Initialize a PDF document with the correct settings.
        
        Args:
            product_id: The product ID for the filename
            output_dir: The output directory for the PDF
            
        Returns:
            SimpleDocTemplate: The initialized document
        """
        file_path = output_dir / f"{product_id}_datasheet.pdf"
        
        doc = SimpleDocTemplate(
            str(file_path),  # Convert Path to string for ReportLab
            pagesize=(A4[1], A4[0]),  # Landscape orientation
            defaultStyle={'wordWrap': 'CJK'},
        )
        
        return doc
    
    def create_page_templates(self, doc, callback_fn=None):
        """Create page templates with appropriate frames.
        
        Args:
            doc: The document to add templates to
            callback_fn: Function to call on each page
            
        Returns:
            list: The created page templates
        """
        # First page template with no top margin
        first_page_frame = Frame(
            25 * mm,  # left margin
            25 * mm,  # bottom margin
            doc.width,  # width
            doc.height,  # full height for first page
            leftPadding=0,
            topPadding=-15*mm,
            rightPadding=0,
            bottomPadding=0
        )

        # Other pages template with normal margins
        other_pages_frame = Frame(
            25 * mm,
            25 * mm,
            doc.width,
            doc.height - 50 * mm,
            leftPadding=0,
            topPadding=0,
            rightPadding=0,
            bottomPadding=0
        )
        
        # Use the provided callback or default to add_drawn_by
        page_callback = callback_fn if callback_fn else self.add_drawn_by
        
        # Create templates
        templates = [
            PageTemplate(id='FirstPage', frames=first_page_frame, onPage=page_callback),
            PageTemplate(id='OtherPages', frames=other_pages_frame, onPage=page_callback)
        ]
        
        # Add templates to document
        for template in templates:
            doc.addPageTemplates(template)
            
        return templates
    
    def add_drawn_by(self, canvas, doc):
        """Add the 'drawn by' SVG to the canvas.
        
        Args:
            canvas: The ReportLab canvas to draw on
            doc: The document being created
        """
        canvas.saveState()
        
        # Add drawn_by SVG to bottom right of every page
        drawn_by_path = self.assets_dir / 'drawn_by.svg'
        
        # Convert SVG to ReportLab drawing
        drawing = svg2rlg(str(drawn_by_path))
        
        # Desired final dimensions
        target_width = 120*mm  # Width in mm
        target_height = 45*mm  # Height in mm
        
        # Calculate scale factors
        width_scale = target_width / drawing.width
        height_scale = target_height / drawing.height
        scale = min(width_scale, height_scale)
        
        # Calculate position
        page_width, page_height = doc.pagesize
        x = page_width - (drawing.width * scale) - 11*mm  # 11mm from right edge
        y = 11*mm  # 11mm from bottom
        
        # Apply transformations
        canvas.translate(x, y)
        canvas.scale(scale, scale)
        
        # Draw the SVG
        renderPDF.draw(drawing, canvas, 0, 0)
        canvas.restoreState()
    
    def register_fonts(self):
        """Register custom fonts for use in the document."""
        calibri_regular = self.fonts_dir / 'calibri.ttf'
        calibri_bold = self.fonts_dir / 'calibrib.ttf'
        
        pdfmetrics.registerFont(TTFont('Calibri', str(calibri_regular)))
        pdfmetrics.registerFont(TTFont('Calibri-Bold', str(calibri_bold))) 