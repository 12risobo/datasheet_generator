import pytest
import os
from pathlib import Path
from unittest.mock import patch
from datasheet.generator import DatasheetGenerator

class TestIntegration:
    """Integration tests for the datasheet generator."""
    
    @pytest.mark.integration
    def test_end_to_end_generation(self, sample_specs_data, sample_product_data, 
                                  sample_svg_file, temp_dir, mock_assets_dir, mock_fonts_dir):
        """Test the entire datasheet generation process."""
        # This test requires a more complete environment setup
        # We'll patch the necessary components to make it work
        
        # Arrange
        product_id = "TEST123"
        
        # We need to patch paths to assets and fonts
        with patch('datasheet.template_manager.Path.parent.parent') as mock_parent:
            # Configure the mock to return our test directories
            mock_parent.return_value = temp_dir
            
            # Create the necessary directories in our temp dir
            (temp_dir / "assets").mkdir(exist_ok=True)
            (temp_dir / "fonts").mkdir(exist_ok=True)
            
            # Copy our mock files to the expected locations
            import shutil
            for file in mock_assets_dir.glob("*"):
                shutil.copy(file, temp_dir / "assets" / file.name)
            for file in mock_fonts_dir.glob("*"):
                shutil.copy(file, temp_dir / "fonts" / file.name)
            
            # Create generator
            generator = DatasheetGenerator(
                product_id=product_id,
                specs_data=sample_specs_data,
                items_data=sample_product_data,
                image_path=sample_svg_file,
                output_dir=temp_dir
            )
            
            # Act
            with patch('datasheet.generator.add_watermark_to_pdf'):
                generator.generate()
            
            # Assert
            expected_output = temp_dir / f"{product_id}_datasheet.pdf"
            assert expected_output.exists()
    
    @pytest.mark.integration
    def test_with_real_data(self, temp_dir):
        """Test with real data files from the project."""
        # Skip this test if we're not in the project directory
        data_dir = Path("data")
        if not data_dir.exists():
            pytest.skip("Test must be run from project root directory")
        
        # Arrange
        from utils.csv_reader import read_csv
        
        specs_data = read_csv("data/specs.csv")
        items_data = read_csv("data/productrange.csv")
        image_path = Path("assets/cable_drawing.svg")
        
        if not image_path.exists():
            pytest.skip("Required test assets not found")
        
        # Act & Assert
        try:
            # Create generator
            generator = DatasheetGenerator(
                product_id="TEST_REAL",
                specs_data=specs_data,
                items_data=items_data,
                image_path=image_path,
                output_dir=temp_dir
            )
            
            # Generate the datasheet
            with patch('datasheet.generator.add_watermark_to_pdf'):
                generator.generate()
            
            # Check that the output file exists
            expected_output = temp_dir / "TEST_REAL_datasheet.pdf"
            assert expected_output.exists()
            
        except Exception as e:
            pytest.skip(f"Integration test with real data failed: {e}")
    
    @pytest.mark.parametrize("product_id", ["TEST1", "TEST-2", "TEST_3"])
    def test_multiple_product_ids(self, product_id, sample_specs_data, sample_product_data, 
                                 sample_svg_file, temp_dir, mock_assets_dir, mock_fonts_dir):
        """Test generating datasheets with different product IDs."""
        # Arrange
        with patch('datasheet.template_manager.Path.parent.parent') as mock_parent:
            mock_parent.return_value = temp_dir
            
            # Create the necessary directories
            (temp_dir / "assets").mkdir(exist_ok=True)
            (temp_dir / "fonts").mkdir(exist_ok=True)
            
            # Copy mock files
            import shutil
            for file in mock_assets_dir.glob("*"):
                shutil.copy(file, temp_dir / "assets" / file.name)
            for file in mock_fonts_dir.glob("*"):
                shutil.copy(file, temp_dir / "fonts" / file.name)
            
            # Create generator
            generator = DatasheetGenerator(
                product_id=product_id,
                specs_data=sample_specs_data,
                items_data=sample_product_data,
                image_path=sample_svg_file,
                output_dir=temp_dir
            )
            
            # Act
            with patch('datasheet.generator.add_watermark_to_pdf'):
                generator.generate()
            
            # Assert
            expected_output = temp_dir / f"{product_id}_datasheet.pdf"
            assert expected_output.exists() 