from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, NextPageTemplate
from utils.pdf_utils import add_watermark_to_pdf
import logging
from .template_manager import TemplateManager
from .content_builder import ContentBuilder
from .image_handler import ImageHandler

logger = logging.getLogger(__name__)

class DatasheetGenerator:
    """Main class for generating datasheets."""
    
    def __init__(self, product_id, specs_data, items_data, image_path, output_dir):
        """Initialize the datasheet generator.
        
        Args:
            product_id: The product ID for the datasheet
            specs_data: The specifications data
            items_data: The product items data
            image_path: Path to the technical drawing
            output_dir: Directory to save the output
        """
        self.product_id = product_id
        self.specs_data = specs_data
        self.items_data = items_data
        self.image_path = Path(image_path)
        self.output_dir = Path(output_dir)
        self.story = []
        
        # Initialize components
        self.template_manager = TemplateManager()
        self.content_builder = ContentBuilder()
        self.image_handler = ImageHandler()
        
        # Initialize document
        self.doc = self.template_manager.init_doc(self.product_id, self.output_dir)
        
        # Create page templates - this was missing!
        self.templates = self.template_manager.create_page_templates(self.doc)
        
        # Set table width based on document width
        self.content_builder.set_document_width(self.doc.width)
    
    def generate(self):
        """Generate the datasheet PDF."""
        # Build the story
        self._build_story()
        
        # Set the first page template
        self.story.insert(0, NextPageTemplate('FirstPage'))
        
        # Generate temporary PDF without watermark
        temp_pdf_path = self.output_dir / f"temp_{self.product_id}_datasheet.pdf"
        final_pdf_path = self.output_dir / f"{self.product_id}_datasheet.pdf"
        
        # Build the initial PDF
        self.doc.filename = str(temp_pdf_path)
        self.doc.build(
            self.story,
            onFirstPage=self.template_manager.add_drawn_by,
            onLaterPages=self.template_manager.add_drawn_by
        )
        
        # Add watermark
        watermark_path = Path(__file__).parent.parent / 'assets' / 'Watermerk.pdf'
        add_watermark_to_pdf(
            str(temp_pdf_path),
            str(watermark_path),
            str(final_pdf_path)
        )
        
        # Clean up temporary file
        temp_pdf_path.unlink()
        
        logger.info(f"Generated datasheet: {final_pdf_path}")
    
    def _build_story(self):
        """Build the story for the document."""
        # Add technical drawing
        self.story.extend(
            self.image_handler.add_technical_drawing(self.image_path)
        )
        
        # Add specifications section
        self.story.extend(
            self.content_builder.create_specifications_section(self.specs_data)
        )
        
        # Add product information section
        self.story.extend(
            self.content_builder.create_product_info_section(self.items_data)
        ) 