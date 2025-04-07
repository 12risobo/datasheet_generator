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
        # Get the directory containing this file
        current_dir = Path(__file__).parent
        
        # Set up assets and fonts directories
        self.assets_dir = current_dir / 'assets'
        self.fonts_dir = current_dir / 'fonts'
        
        # Ensure directories exist
        self.assets_dir.mkdir(exist_ok=True)
        self.fonts_dir.mkdir(exist_ok=True)
        
        # Register fonts
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
        
        try:
            if not drawn_by_path.exists():
                raise FileNotFoundError(f"SVG file not found at {drawn_by_path}")
                
            # Convert SVG to ReportLab drawing
            drawing = svg2rlg(str(drawn_by_path))
            if drawing is None:
                # Create a simple drawing if SVG cannot be loaded
                from reportlab.graphics.shapes import Drawing, Rect, String
                drawing = Drawing(120, 45)
                drawing.add(Rect(0, 0, 120, 45, fillColor='#305496'))
                drawing.add(Rect(5, 5, 110, 35, fillColor='white', fillOpacity=0.9))
                # Add text with fallback font
                drawing.add(String(10, 25, "Drawn By", fontName='Helvetica', fontSize=12, fillColor='#305496'))
            
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
        except Exception as e:
            # Log error but continue without the drawing
            import logging
            logging.getLogger(__name__).error(f"Error adding drawn_by SVG: {e}")
            # Create a simple drawing as fallback
            from reportlab.graphics.shapes import Drawing, Rect, String
            drawing = Drawing(120, 45)
            drawing.add(Rect(0, 0, 120, 45, fillColor='#305496'))
            drawing.add(Rect(5, 5, 110, 35, fillColor='white', fillOpacity=0.9))
            drawing.add(String(10, 25, "Drawn By", fontName='Helvetica', fontSize=12, fillColor='#305496'))
            # Draw the fallback
            renderPDF.draw(drawing, canvas, 0, 0)
        finally:
            canvas.restoreState()
    
    def register_fonts(self):
        """Register custom fonts for use in the document."""
        # Get the absolute paths to the font files
        calibri_regular = self.fonts_dir / 'calibri.ttf'
        calibri_bold = self.fonts_dir / 'calibrib.ttf'
        
        try:
            # Check if font files exist
            if not calibri_regular.exists() or not calibri_bold.exists():
                raise FileNotFoundError("Calibri font files not found")
            
            # Register the fonts
            pdfmetrics.registerFont(TTFont('Calibri', str(calibri_regular)))
            pdfmetrics.registerFont(TTFont('Calibri-Bold', str(calibri_bold)))
            
            # Register the font family
            pdfmetrics.registerFontFamily(
                'Calibri',
                normal='Calibri',
                bold='Calibri-Bold',
            )
        except Exception as e:
            # Log warning and use Helvetica as fallback
            import logging
            logging.getLogger(__name__).warning(
                f"Could not load Calibri fonts: {e}. Using Helvetica as fallback."
            )
            # Register Helvetica as fallback
            pdfmetrics.registerFontFamily(
                'Calibri',
                normal='Helvetica',
                bold='Helvetica-Bold',
            ) 