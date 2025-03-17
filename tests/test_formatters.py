import pytest
from reportlab.lib import colors
from reportlab.platypus import Table
from datasheet.formatters import TableFormatter

class TestTableFormatter:
    """Tests for the TableFormatter class."""
    
    def test_init(self):
        """Test initialization with default values."""
        # Arrange & Act
        formatter = TableFormatter()
        
        # Assert
        assert formatter.header_color == colors.HexColor('#305496')
        assert formatter.header_text_color == colors.white
        assert formatter.font_name == 'Calibri'
        assert formatter.header_font_size == 10
        assert formatter.body_font_size == 8
    
    def test_create_specification_table_style(self):
        """Test creating a style for specification tables."""
        # Arrange
        formatter = TableFormatter()
        
        # Act
        style = formatter.create_specification_table_style()
        
        # Assert
        assert len(style) > 0
        # Check for essential style commands
        style_commands = [cmd[0] for cmd in style]
        assert 'GRID' in style_commands
        assert 'BACKGROUND' in style_commands
        assert 'TEXTCOLOR' in style_commands
        assert 'FONTNAME' in style_commands
        assert 'FONTSIZE' in style_commands
        assert 'SPAN' in style_commands  # For header spanning
    
    def test_create_product_table_style(self):
        """Test creating a style for product tables."""
        # Arrange
        formatter = TableFormatter()
        
        # Act
        style = formatter.create_product_table_style()
        
        # Assert
        assert len(style) > 0
        # Check for essential style commands
        style_commands = [cmd[0] for cmd in style]
        assert 'GRID' in style_commands
        assert 'BACKGROUND' in style_commands
        assert 'TEXTCOLOR' in style_commands
        assert 'FONTNAME' in style_commands
        assert 'FONTSIZE' in style_commands
        assert 'ALIGN' in style_commands
    
    def test_format_specification_table(self):
        """Test formatting a specification table."""
        # Arrange
        formatter = TableFormatter()
        table_data = [
            ["Section Title", ""],
            ["Property 1", "Value 1"],
            ["Property 2", "Value 2"],
            ["[k1]Special Row", ""],
        ]
        col_width = 100
        
        # Act
        table = formatter.format_specification_table(table_data, col_width)
        
        # Assert
        assert isinstance(table, Table)
        assert table._colWidths == [col_width, col_width]
        
        # Check that the style has been applied
        assert hasattr(table, 'style')
        assert len(table.style) > 0
    
    def test_format_product_table(self):
        """Test formatting a product table."""
        # Arrange
        formatter = TableFormatter()
        table_data = [
            ["Article", "Length", "Article", "Length"],
            ["A1", "1m", "A2", "2m"],
            ["A3", "3m", "A4", "4m"],
        ]
        col_width = 50
        
        # Act
        table = formatter.format_product_table(table_data, col_width)
        
        # Assert
        assert isinstance(table, Table)
        assert table._colWidths == [col_width] * 4
        
        # Check that the style has been applied
        assert hasattr(table, 'style')
        assert len(table.style) > 0
    
    def test_detect_merged_rows(self):
        """Test detection of rows that should be merged."""
        # Arrange
        formatter = TableFormatter()
        table_data = [
            ["Header", ""],
            ["Regular Row", "Value"],
            ["[k1]Merged Row", ""],
            ["Another Regular", "Value"],
        ]
        
        # Act
        style = formatter.create_specification_table_style()
        merged_rows = formatter.detect_merged_rows(table_data, style)
        
        # Assert
        assert len(merged_rows) == 1
        assert merged_rows[0] == 2  # Third row (index 2) should be merged 