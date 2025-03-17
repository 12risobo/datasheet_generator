import pytest
from pathlib import Path
from reportlab.platypus import Image, Spacer
from reportlab.lib.units import inch
from datasheet.image_handler import ImageHandler

class TestImageHandler:
    """Tests for the ImageHandler class."""
    
    def test_init(self):
        """Test initialization with correct default values."""
        # Arrange & Act
        handler = ImageHandler()
        
        # Assert
        assert handler.default_image_size == (10.5 * inch, 5.25 * inch)
    
    def test_add_technical_drawing_svg(self, sample_svg_file):
        """Test adding an SVG technical drawing."""
        # Arrange
        handler = ImageHandler()
        
        # Act
        story_elements = handler.add_technical_drawing(sample_svg_file)
        
        # Assert
        assert len(story_elements) == 2
        # First element should be the drawing
        assert hasattr(story_elements[0], 'width')
        assert hasattr(story_elements[0], 'height')
        # Second element should be a spacer
        assert isinstance(story_elements[1], Spacer)
    
    def test_add_technical_drawing_image(self, temp_dir):
        """Test adding a non-SVG technical drawing."""
        # Arrange
        handler = ImageHandler()
        
        # Create a test image
        from PIL import Image as PILImage
        img_path = temp_dir / "test_image.png"
        img = PILImage.new('RGB', (300, 200), color='blue')
        img.save(img_path)
        
        # Act
        story_elements = handler.add_technical_drawing(img_path)
        
        # Assert
        assert len(story_elements) == 2
        # First element should be an image
        assert isinstance(story_elements[0], Image)
        # Second element should be a spacer
        assert isinstance(story_elements[1], Spacer)
    
    def test_add_technical_drawing_nonexistent_file(self):
        """Test adding a non-existent file."""
        # Arrange
        handler = ImageHandler()
        non_existent_path = Path("/path/to/nonexistent/file.jpg")
        
        # Act
        story_elements = handler.add_technical_drawing(non_existent_path)
        
        # Assert
        assert len(story_elements) == 0  # Should return empty list on error
    
    def test_resize_image(self, temp_dir):
        """Test image resizing functionality."""
        # Arrange
        handler = ImageHandler()
        
        # Create a test image
        from PIL import Image as PILImage
        img_path = temp_dir / "resize_test.png"
        img = PILImage.new('RGB', (1000, 500), color='red')
        img.save(img_path)
        
        # Act
        width, height = handler.resize_image(img_path, 500, 250)
        
        # Assert
        assert width <= 500
        assert height <= 250
        # Aspect ratio should be maintained
        assert abs((width / height) - 2.0) < 0.1  # Original aspect ratio is 2.0 