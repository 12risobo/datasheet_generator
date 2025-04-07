import pytest
from pathlib import Path
from reportlab.platypus import Table, Paragraph, KeepTogether
from datasheet.content_builder import ContentBuilder

class TestContentBuilder:
    """Tests for the ContentBuilder class."""
    
    def test_init(self):
        """Test initialization with correct default values."""
        # Arrange & Act
        builder = ContentBuilder()
        
        # Assert
        assert builder.table_width_ratio == 0.73
        assert builder.num_product_columns == 4
    
    def test_group_specs_by_section(self, sample_specs_data):
        """Test grouping specifications by section."""
        # Arrange
        builder = ContentBuilder()
        
        # Act
        sections = builder.group_specs_by_section(sample_specs_data)
        
        # Assert
        assert len(sections) == 2
        assert "SPECIFICATIONS CABLE (A)" in sections
        assert "SPECIFICATIONS FIBER" in sections
        
        # Check content of sections
        cable_section = sections["SPECIFICATIONS CABLE (A)"]
        # Filter out empty rows before checking length
        cable_section = [row for row in cable_section if any(cell.strip() for cell in row)]
        assert len(cable_section) == 3
        assert cable_section[0][0] == "Type"
        assert cable_section[0][1] == "Patchcord - Duplex"
        
        fiber_section = sections["SPECIFICATIONS FIBER"]
        # Filter out empty rows before checking length
        fiber_section = [row for row in fiber_section if any(cell.strip() for cell in row)]
        assert len(fiber_section) == 3
        assert fiber_section[0][0] == "Type"
        assert fiber_section[0][1] == "OM4"
        assert fiber_section[1][0] == "Core diameter"
        assert fiber_section[1][1] == "50µm"
    
    def test_create_specifications_section(self, sample_specs_data):
        """Test creating the specifications section."""
        # Arrange
        builder = ContentBuilder()
        doc_width = 500  # Mock document width
        builder.table_width = doc_width * builder.table_width_ratio
        
        # Act
        story_elements = builder.create_specifications_section(sample_specs_data)
        
        # Assert
        assert len(story_elements) >= 3  # Heading, spacer, and at least one table
        
        # Check that we have a heading
        assert isinstance(story_elements[0], Paragraph)
        assert "Technical Specifications" in story_elements[0].text
        
        # Find tables in the story
        tables = [elem for elem in story_elements if isinstance(elem, KeepTogether)]
        assert len(tables) >= 2  # At least one table for each section
    
    def test_create_product_table_data(self, sample_product_data):
        """Test creating product table data with correct column distribution."""
        # Arrange
        builder = ContentBuilder()
        products = sample_product_data[1:]  # Skip header row
        
        # Act
        table_data = builder.create_product_table_data(products)
        
        # Assert
        # With 4 products and 4 columns, we should have 1 product per column
        assert len(table_data) == builder.num_product_columns
        
        # Test with more products
        more_products = products * 3  # 12 products
        table_data = builder.create_product_table_data(more_products)
        
        # With 12 products and 4 columns, we should have 3 products per column
        assert len(table_data) == builder.num_product_columns
        assert len(table_data[0]) == 3  # 3 products in first column
    
    def test_create_product_info_section(self, sample_product_data):
        """Test creating the product information section."""
        # Arrange
        builder = ContentBuilder()
        doc_width = 500  # Mock document width
        builder.table_width = doc_width * builder.table_width_ratio
        
        # Act
        story_elements = builder.create_product_info_section(sample_product_data)
        
        # Assert
        assert len(story_elements) >= 3  # Heading, spacer, and table
        
        # Check that we have a heading
        assert isinstance(story_elements[0], Paragraph)
        assert "Product Information" in story_elements[0].text
        
        # Find tables in the story
        tables = []
        for elem in story_elements:
            if isinstance(elem, Table):
                tables.append(elem)
            elif isinstance(elem, KeepTogether):
                for sub_elem in elem._content:
                    if isinstance(sub_elem, Table):
                        tables.append(sub_elem)
        
        assert len(tables) >= 1  # At least one table
        table = tables[0]
        assert isinstance(table, Table)
        assert len(table._cellvalues) > 1  # Should have header and at least one data row
        assert len(table._cellvalues[0]) == 8  # Should have 8 columns (4 pairs) 