import pytest
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from datasheet.template_manager import TemplateManager

class TestTemplateManager:
    """Tests for the TemplateManager class."""
    
    def test_init_doc(self, temp_dir):
        """Test document initialization with correct page size and orientation."""
        # Arrange
        product_id = "TEST123"
        output_dir = temp_dir
        manager = TemplateManager()
        
        # Act
        doc = manager.init_doc(product_id, output_dir)
        
        # Assert
        assert isinstance(doc, SimpleDocTemplate)
        assert doc.pagesize == (A4[1], A4[0])  # Landscape orientation
        assert str(doc.filename) == str(output_dir / f"{product_id}_datasheet.pdf")
    
    def test_create_page_templates(self, temp_dir):
        """Test creation of page templates with correct frames."""
        # Arrange
        product_id = "TEST123"
        manager = TemplateManager()
        doc = manager.init_doc(product_id, temp_dir)
        
        # Act
        templates = manager.create_page_templates(doc, callback_fn=None)
        
        # Assert
        assert len(templates) == 2
        assert templates[0].id == 'FirstPage'
        assert templates[1].id == 'OtherPages'
        
        # Check frame dimensions
        first_frame = templates[0].frames[0]
        other_frame = templates[1].frames[0]
        
        assert first_frame.height > other_frame.height  # First page has more space
    
    def test_add_drawn_by(self, temp_dir, mock_assets_dir):
        """Test adding the 'drawn by' SVG to the canvas."""
        # This test would need to mock the canvas and verify the drawing is added
        # For now, we'll just test that the method doesn't raise exceptions
        
        # Arrange
        manager = TemplateManager()
        manager.assets_dir = mock_assets_dir  # Override the assets directory
        
        # Create a mock canvas and doc
        from unittest.mock import MagicMock
        canvas = MagicMock()
        doc = MagicMock()
        doc.pagesize = (A4[1], A4[0])
        
        # Act & Assert
        try:
            manager.add_drawn_by(canvas, doc)
            # If no exception, the test passes
            assert True
        except Exception as e:
            pytest.fail(f"add_drawn_by raised an exception: {e}") 