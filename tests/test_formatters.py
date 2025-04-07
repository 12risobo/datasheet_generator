import pytest
from reportlab.lib import colors
from reportlab.platypus import Table
from datasheet.formatters import TableFormatter

class TestTableFormatter:
    """Tests for the TableFormatter class."""
    
    def test_init(self):
        """Test initialization with correct default values."""
        # Arrange & Act
        formatter = TableFormatter()
        
        # Assert
        assert formatter.header_color == '#305496'  # Dark blue
        assert formatter.header_text_color == '#FFFFFF'  # White
        assert formatter.font_name in ['Calibri', 'Helvetica']  # Can be either font
        assert formatter.font_size == 8
        assert formatter.header_font_size == 9
    
    def test_create_specification_table_style(self):
        """Test creating a specification table style."""
        # Arrange
        formatter = TableFormatter()
        
        # Act
        style = formatter.create_specification_table_style()
        
        # Assert
        assert isinstance(style, list)
        assert len(style) > 0
        assert any(cmd[0] == 'GRID' for cmd in style)
        assert any(cmd[0] == 'BACKGROUND' for cmd in style)
    
    def test_create_product_table_style(self):
        """Test creating a product table style."""
        # Arrange
        formatter = TableFormatter()
        
        # Act
        style = formatter.create_product_table_style()
        
        # Assert
        assert isinstance(style, list)
        assert len(style) > 0
        assert any(cmd[0] == 'GRID' for cmd in style)
        assert any(cmd[0] == 'BACKGROUND' for cmd in style)
    
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
        assert hasattr(table, '_style')
        assert len(table._style) > 0
    
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
        assert hasattr(table, '_style')
        assert len(table._style) > 0
    
    def test_detect_merged_rows(self):
        """Test detecting merged rows in a table."""
        # Arrange
        formatter = TableFormatter()
        table_data = [
            ["Section Title", ""],
            ["Property 1", "Value 1"],
            ["[k1]Special Row", ""],
        ]
        style = []

        # Act
        merged_rows = formatter.detect_merged_rows(table_data, style)

        # Assert
        assert len(merged_rows) == 1
        assert merged_rows[0] == 2 