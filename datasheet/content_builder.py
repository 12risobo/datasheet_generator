from reportlab.platypus import Table, Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
import logging
from .formatters import TableFormatter

logger = logging.getLogger(__name__)

class ContentBuilder:
    """Builds content sections for the datasheet."""
    
    def __init__(self):
        """Initialize the content builder with default settings."""
        self.table_width_ratio = 0.73
        self.num_product_columns = 4
        self.styles = getSampleStyleSheet()
        self.formatter = TableFormatter()
        self.table_width = None  # Will be set when doc width is known
    
    def set_document_width(self, doc_width):
        """Set the document width and calculate table width.
        
        Args:
            doc_width: The width of the document
        """
        self.table_width = doc_width * self.table_width_ratio
    
    def create_specifications_section(self, specs_data):
        """Create the specifications section.
        
        Args:
            specs_data: The specifications data
            
        Returns:
            list: Story elements for the specifications section
        """
        story_elements = []
        
        # Add section heading
        story_elements.append(Paragraph("Technical Specifications", self.styles['Heading2']))
        story_elements.append(Spacer(1, 10))
        
        # Group specifications by section
        sections = self.group_specs_by_section(specs_data)
        
        if not sections:
            logger.warning("No specification sections found!")
            return story_elements
        
        # Calculate column width
        col_width = self.table_width / 2.0
        
        # Create tables for each section
        for section_title, section_data in sections.items():
            if section_data:
                # Create table data with section title as header
                table_data = [[section_title, '']]
                table_data.extend(section_data)
                
                # Format the table
                section_table = self.formatter.format_specification_table(table_data, col_width)
                
                # Add to story with keep together
                story_elements.append(KeepTogether([section_table, Spacer(1, 5)]))
        
        return story_elements
    
    def create_product_info_section(self, items_data):
        """Create the product information section.
        
        Args:
            items_data: The product data
            
        Returns:
            list: Story elements for the product information section
        """
        story_elements = []
        
        # Add section heading
        story_elements.append(Paragraph("Product Information", self.styles['Heading2']))
        story_elements.append(Spacer(1, 10))
        
        # Skip header row for processing
        header = items_data[0]
        products = [row for row in items_data[1:] if any(row)]
        
        # Process header columns
        article_code_header = header[0]  # First column is Article code
        length_header = header[1]  # Second column is Length(m)
        
        # Remove [H1] marker if present
        if '[H1]' in length_header.upper():
            length_header = length_header.split('[H1]')[0].strip()
        
        # Create table data
        num_column_pairs = self.num_product_columns
        total_columns = num_column_pairs * 2
        
        # Create header row
        header_row = []
        for _ in range(num_column_pairs):
            header_row.extend([article_code_header, length_header])
        
        # Initialize table data with header
        table_data = [header_row]
        
        # Calculate products per column
        products_per_column = (len(products) + num_column_pairs - 1) // num_column_pairs
        
        # Fill table data
        for row_idx in range(products_per_column):
            row_data = []
            for col_idx in range(num_column_pairs):
                product_idx = row_idx + (col_idx * products_per_column)
                if product_idx < len(products):
                    # Add product data (first two columns only)
                    row_data.extend(products[product_idx][:2])
                else:
                    # Add empty cells for padding
                    row_data.extend(['', ''])
            table_data.append(row_data)
        
        # Calculate column width
        col_width = self.table_width / total_columns
        
        # Format the table
        items_table = self.formatter.format_product_table(table_data, col_width)
        
        # Add to story with keep together
        try:
            story_elements.append(KeepTogether([items_table, Spacer(1, 5)]))
        except Exception as e:
            # If table is too large to keep together, add page break
            logger.warning(f"Product table too large to keep together: {e}")
            story_elements.append(PageBreak())
            story_elements.append(items_table)
            story_elements.append(Spacer(1, 5))
        
        return story_elements
    
    def group_specs_by_section(self, specs_data):
        """Group specifications by section.
        
        Args:
            specs_data: The specifications data
            
        Returns:
            dict: Sections with their data
        """
        sections = {}
        current_section = None
        
        for row in specs_data:
            if len(row) < 1:
                continue
            
            # Improved header detection with case-insensitive check
            header_candidate = row[0].upper()
            if '[H1]' in header_candidate:
                current_section = row[0].upper().split('[H1]')[0].strip()
                sections[current_section] = []
            elif current_section and len(row) >= 2:
                # Take first two columns only
                sections[current_section].append(row[:2])
        
        return sections
    
    def create_product_table_data(self, products):
        """Create product table data with correct column distribution.
        
        Args:
            products: The product data
            
        Returns:
            list: Columns of product data
        """
        products_per_column = (len(products) + self.num_product_columns - 1) // self.num_product_columns
        
        columns = []
        for i in range(self.num_product_columns):
            start_idx = i * products_per_column
            end_idx = min((i + 1) * products_per_column, len(products))
            column_data = products[start_idx:end_idx]
            columns.append(column_data)
        
        return columns 