from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
import logging
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class TableFormatter:
    """Handles table formatting and styling for the datasheet."""
    
    def __init__(self):
        """Initialize the table formatter with default styles."""
        self.header_color = '#305496'  # Dark blue
        self.header_text_color = '#FFFFFF'  # White
        self.font_name = 'Helvetica'  # Default font
        self.font_size = 8
        self.header_font_size = 9
        self.styles = getSampleStyleSheet()
        
        # Try to register Calibri fonts
        try:
            fonts_dir = Path(__file__).parent / 'fonts'
            if (fonts_dir / 'calibri.ttf').exists() and (fonts_dir / 'calibrib.ttf').exists():
                pdfmetrics.registerFont(TTFont('Calibri', str(fonts_dir / 'calibri.ttf')))
                pdfmetrics.registerFont(TTFont('Calibri-Bold', str(fonts_dir / 'calibrib.ttf')))
                self.font_name = 'Calibri'
            else:
                logging.getLogger(__name__).warning(
                    "Calibri fonts not found in fonts directory. Using Helvetica as fallback."
                )
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"Failed to load Calibri fonts: {e}. Using Helvetica as fallback."
            )
    
    def create_specification_table_style(self):
        """Create a style for specification tables.
        
        Returns:
            list: Table style commands
        """
        return [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -1), self.font_size),
            ('TOPPADDING', (0, 0), (-1, -1), 1.7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.7),
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), self.header_color),
            ('TEXTCOLOR', (0, 0), (1, 0), self.header_text_color),
            ('FONTNAME', (0, 0), (1, 0), self.font_name),
            ('FONTSIZE', (0, 0), (1, 0), self.header_font_size),
            ('FONTWEIGHT', (0, 0), (1, 0), 'BOLD'),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
        ]
    
    def create_product_table_style(self):
        """Create a style for product tables.
        
        Returns:
            list: Table style commands
        """
        return [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -1), self.font_size),
            ('TOPPADDING', (0, 0), (-1, -1), 1.7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.7),
            ('BACKGROUND', (0, 0), (-1, 0), self.header_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.header_text_color),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name),
            ('FONTSIZE', (0, 0), (-1, 0), self.header_font_size),
            ('FONTWEIGHT', (0, 0), (-1, 0), 'BOLD'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ]
    
    def format_specification_table(self, table_data, col_width):
        """Format a specification table.
        
        Args:
            table_data: The data for the table
            col_width: The width of each column
            
        Returns:
            Table: The formatted table
        """
        style = self.create_specification_table_style()
        
        # Process special rows (with [k1] marker)
        self.process_special_rows(table_data, style)
        
        # Create the table
        table = Table(
            table_data,
            colWidths=[col_width, col_width],
            spaceBefore=5,
            spaceAfter=5
        )
        table.setStyle(style)
        table._style = style  # Store the style as an attribute
        
        return table
    
    def format_product_table(self, table_data, col_width):
        """Format a product table.
        
        Args:
            table_data: The data for the table
            col_width: The width of each column
            
        Returns:
            Table: The formatted table
        """
        style = self.create_product_table_style()
        
        # Create the table
        table = Table(
            table_data,
            colWidths=[col_width] * len(table_data[0]),
            spaceBefore=5,
            spaceAfter=5
        )
        table.setStyle(style)
        table._style = style  # Store the style as an attribute
        
        return table
    
    def process_special_rows(self, table_data, style):
        """Process special rows in the table data.
        
        Args:
            table_data: The data for the table
            style: The table style to modify
        """
        merged_rows = self.detect_merged_rows(table_data, style)
        
        # Process each merged row
        for row_index in merged_rows:
            # Clean the text by removing the marker
            clean_text = table_data[row_index][0]
            clean_text = clean_text.replace('[k1]', '').replace('[K1]', '').strip()
            table_data[row_index][0] = clean_text
            
            # Add span for this row
            style.append(('SPAN', (0, row_index), (1, row_index)))
            # Center align the merged cell
            style.append(('ALIGN', (0, row_index), (1, row_index), 'CENTER'))
    
    def detect_merged_rows(self, table_data, style):
        """Detect rows that should be merged.
        
        Args:
            table_data: The data for the table
            style: The table style
            
        Returns:
            list: Indices of rows to be merged
        """
        merged_rows = []
        
        for i, row in enumerate(table_data):
            if len(row) >= 1 and isinstance(row[0], str) and '[k1]' in row[0].lower():
                merged_rows.append(i)
                
        return merged_rows 