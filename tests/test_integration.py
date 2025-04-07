import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datasheet.generator import DatasheetGenerator
from datasheet.template_manager import TemplateManager
from datasheet.image_handler import ImageHandler
from svglib.svglib import svg2rlg

@pytest.fixture
def sample_specs_data():
    return [
        ["Specifications cable (A) [H1]", ""],
        ["Type", "Patchcord - Duplex"],
        ["Outer diameter", "1.8mm"],
        ["Tensile strength", "90N (short time 150N)"],
        ["", ""],
        ["Specifications fiber [H1]", ""],
        ["Type", "OM4"],
        ["Core diameter", "50µm"],
        ["Cladding diameter", "125µm"],
    ]

@pytest.fixture
def sample_product_data():
    return [
        ["Article code", "Length(m) [H1]"],
        ["RL9752", "0.25M"],
        ["RL9700", "0.50M"],
        ["RL9701", "1.00M"],
        ["RL9702", "2.00M"],
    ]

@pytest.fixture
def sample_svg_file(tmp_path):
    svg_file = tmp_path / "test_drawing.svg"
    svg_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect width="100" height="100" fill="blue"/>
</svg>""")
    return svg_file

@pytest.fixture
def mock_svg_drawing():
    """Create a mock SVG drawing for testing."""
    from reportlab.graphics.shapes import Drawing, Rect
    drawing = Drawing(100, 100)
    drawing.add(Rect(0, 0, 100, 100, fillColor='blue'))
    return drawing

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

@pytest.fixture
def mock_assets_dir(tmp_path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    return assets_dir

@pytest.fixture
def mock_fonts_dir(tmp_path):
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    return fonts_dir

class TestIntegration:
    """Integration tests for the datasheet generator."""
    
    @pytest.mark.integration
    def test_end_to_end_generation(self, sample_specs_data, sample_product_data,
                                  sample_svg_file, temp_dir, mock_assets_dir, mock_fonts_dir,
                                  mock_svg_drawing):
        """Test the entire datasheet generation process."""
        # Arrange
        product_id = "TEST123"

        # Mock the necessary paths
        with patch('datasheet.template_manager.Path') as mock_path_class, \
             patch('svglib.svglib.svg2rlg') as mock_svg2rlg, \
             patch('reportlab.pdfbase.ttfonts.TTFont') as mock_ttfont:
            # Create mock instances
            mock_path = MagicMock()
            mock_path.parent = MagicMock()
            mock_path.parent.parent = MagicMock()
            mock_path_class.return_value = mock_path

            # Set up path resolution
            def mock_truediv(self, other):
                if other == "assets":
                    return mock_assets_dir
                elif other == "fonts":
                    return mock_fonts_dir
                return mock_path

            mock_path.parent.parent.__truediv__ = mock_truediv

            # Mock font loading
            mock_ttfont_instance = MagicMock()
            mock_ttfont.return_value = mock_ttfont_instance

            # Mock SVG loading
            mock_svg2rlg.return_value = mock_svg_drawing

            # Act
            generator = DatasheetGenerator(
                product_id=product_id,
                specs_data=sample_specs_data,
                items_data=sample_product_data,
                image_path=sample_svg_file,
                output_dir=temp_dir
            )
            generator.generate()

            # Assert
            output_file = temp_dir / f"{product_id}_datasheet.pdf"
            assert output_file.exists()
    
    @pytest.mark.skip(reason="Integration test with real data files")
    def test_with_real_data(self):
        """Test with actual data files."""
        pass
    
    @pytest.mark.parametrize("product_id", ["TEST1", "TEST-2", "TEST_3"])
    def test_multiple_product_ids(self, product_id, sample_specs_data, sample_product_data,
                                 sample_svg_file, temp_dir, mock_assets_dir, mock_fonts_dir,
                                 mock_svg_drawing):
        """Test generating datasheets with different product IDs."""
        # Arrange
        with patch('datasheet.template_manager.Path') as mock_path_class, \
             patch('svglib.svglib.svg2rlg') as mock_svg2rlg, \
             patch('reportlab.pdfbase.ttfonts.TTFont') as mock_ttfont:
            # Create mock instances
            mock_path = MagicMock()
            mock_path.parent = MagicMock()
            mock_path.parent.parent = MagicMock()
            mock_path_class.return_value = mock_path

            # Set up path resolution
            def mock_truediv(self, other):
                if other == "assets":
                    return mock_assets_dir
                elif other == "fonts":
                    return mock_fonts_dir
                return mock_path

            mock_path.parent.parent.__truediv__ = mock_truediv

            # Mock font loading
            mock_ttfont_instance = MagicMock()
            mock_ttfont.return_value = mock_ttfont_instance

            # Mock SVG loading
            mock_svg2rlg.return_value = mock_svg_drawing

            # Act
            generator = DatasheetGenerator(
                product_id=product_id,
                specs_data=sample_specs_data,
                items_data=sample_product_data,
                image_path=sample_svg_file,
                output_dir=temp_dir
            )
            generator.generate()

            # Assert
            output_file = temp_dir / f"{product_id}_datasheet.pdf"
            assert output_file.exists() 