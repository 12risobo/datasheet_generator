from pathlib import Path
from reportlab.platypus import Image, Spacer
from reportlab.lib.units import inch
from svglib.svglib import svg2rlg
from PIL import Image as PILImage
import logging

logger = logging.getLogger(__name__)

class ImageHandler:
    """Handles image processing and rendering for the datasheet."""
    
    def __init__(self):
        """Initialize the image handler with default settings."""
        self.default_image_size = (10.5 * inch, 5.25 * inch)
    
    def add_technical_drawing(self, image_path):
        """Add a technical drawing to the story.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            list: Story elements for the technical drawing
        """
        story_elements = []
        
        try:
            image_path = Path(image_path)
            
            if image_path.suffix.lower() == '.svg':
                # Handle SVG files
                story_elements.extend(self._process_svg(image_path))
            else:
                # Handle other image formats
                story_elements.extend(self._process_image(image_path))
                
        except Exception as e:
            logger.error(f"Error loading technical drawing: {e}")
            
        return story_elements
    
    def _process_svg(self, svg_path):
        """Process an SVG file.
        
        Args:
            svg_path: Path to the SVG file
            
        Returns:
            list: Story elements for the SVG
        """
        drawing = svg2rlg(str(svg_path))
        if drawing:
            # Scale the drawing
            drawing.width *= 1.5
            drawing.height *= 1.5
            return [drawing, Spacer(1, 5)]
        return []
    
    def _process_image(self, image_path):
        """Process a non-SVG image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            list: Story elements for the image
        """
        # Calculate new image size
        img_width, img_height = self.resize_image(
            image_path, 
            self.default_image_size[0], 
            self.default_image_size[1]
        )
        
        tech_drawing = Image(str(image_path), width=img_width, height=img_height)
        return [tech_drawing, Spacer(1, 5)]
    
    def resize_image(self, image_path, max_width, max_height):
        """Resize an image while maintaining aspect ratio.
        
        Args:
            image_path: Path to the image file
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            tuple: (width, height) of the resized image
        """
        try:
            with PILImage.open(str(image_path)) as img:
                img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
                return img.size
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return (max_width, max_height) 