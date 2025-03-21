import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Image, Table, Paragraph,
                               PageBreak, Spacer, KeepTogether, NextPageTemplate)
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from utils.image_utils import resize_image
from utils.pdf_utils import add_watermark_to_pdf
from PIL import Image

class DatasheetGenerator:
    DEFAULT_IMAGE_SIZE = (10.5 * inch, 5.25 * inch)
    TABLE_WIDTH_RATIO = 0.73
    NUM_PRODUCT_COLUMNS = 4
    
    def __init__(self, product_id, specs_data, items_data, image_path, output_dir):
        self.product_id = product_id
        self.specs_data = specs_data
        self.items_data = items_data
        self.image_path = Path(image_path)
        self.output_dir = Path(output_dir)
        self.styles = getSampleStyleSheet()
        self.story = []
        self.doc = self._init_doc()
        self.table_width = self.doc.width * self.TABLE_WIDTH_RATIO
        self.register_fonts()

    def _init_doc(self):
        file_path = self.output_dir / f"{self.product_id}_datasheet.pdf"

        doc = SimpleDocTemplate(
            str(file_path),  # Convert Path to string for ReportLab
            pagesize=(A4[1], A4[0]),  # Landscape orientation
            defaultStyle={'wordWrap': 'CJK'},
        )

        # First page template with no top margin
        first_page_frame = Frame(
            25 * mm,  # left margin
            25 * mm,  # bottom margin
            doc.width,  # width
            doc.height,  # full height for first page
            leftPadding=0,
            topPadding=-15*mm,
            rightPadding=0,
            bottomPadding=0
        )

        # Other pages template with normal margins
        other_pages_frame = Frame(
            25 * mm,
            25 * mm,
            doc.width,
            doc.height - 50 * mm,
            leftPadding=0,
            topPadding=0,
            rightPadding=0,
            bottomPadding=0
        )

        # Create templates with common onPage function
        doc.addPageTemplates(PageTemplate(id='FirstPage', frames=first_page_frame, onPage=self.add_drawn_by))
        doc.addPageTemplates(PageTemplate(id='OtherPages', frames=other_pages_frame, onPage=self.add_drawn_by))

        return doc

    def add_drawn_by(self, canvas, doc):
        canvas.saveState()
        # Add drawn_by SVG to bottom right of every page
        drawn_by_path = Path(__file__).parent.parent / 'assets' / 'drawn_by.svg'
        # Convert SVG to ReportLab drawing
        from svglib.svglib import svg2rlg
        drawing = svg2rlg(str(drawn_by_path))  # Convert Path to string
        
        # Desired final dimensions
        target_width = 120*mm  # Increased by 300% (40mm → 120mm)
        target_height = 45*mm  # Increased by 300% (15mm → 45mm)
        
        # Calculate scale factors
        width_scale = target_width / drawing.width
        height_scale = target_height / drawing.height
        scale = min(width_scale, height_scale)
        
        # Calculate position
        page_width, page_height = doc.pagesize
        x = page_width - (drawing.width * scale) - 11*mm  # Keep 11mm right margin
        y = 11*mm  # Keep 11mm bottom margin
        
        # Apply transformations
        canvas.translate(x, y)
        canvas.scale(scale, scale)
        
        # Draw the SVG
        from reportlab.graphics import renderPDF
        renderPDF.draw(drawing, canvas, 0, 0)
        canvas.restoreState()

    def register_fonts(self):
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        # Use font files from the fonts directory (relative to project root)
        font_dir = Path(__file__).parent.parent / 'fonts'
        calibri_regular = font_dir / 'calibri.ttf'
        calibri_bold = font_dir / 'calibrib.ttf'
        pdfmetrics.registerFont(TTFont('Calibri', str(calibri_regular)))
        pdfmetrics.registerFont(TTFont('Calibri-Bold', str(calibri_bold)))

    def generate(self):
        self._build_story()
        # Use the same template for all pages
        self.story.insert(0, NextPageTemplate('FirstPage'))
        # Generate temporary PDF without watermark
        temp_pdf_path = self.output_dir / f"temp_{self.product_id}_datasheet.pdf"
        final_pdf_path = self.output_dir / f"{self.product_id}_datasheet.pdf"
        
        # Build the initial PDF
        self.doc.filename = str(temp_pdf_path)  # Convert Path to string
        self.doc.build(self.story, onFirstPage=self.add_drawn_by, onLaterPages=self.add_drawn_by)
        
        # Add watermark
        watermark_path = Path(__file__).parent.parent / 'assets' / 'Watermerk.pdf'
        add_watermark_to_pdf(str(temp_pdf_path), str(watermark_path), str(final_pdf_path))
        
        # Clean up temporary file
        temp_pdf_path.unlink()

    def _build_story(self):
        self._add_technical_drawing()
        self._add_specifications_section()
        self._add_product_info_section()

    def _add_technical_drawing(self):
        # First add the technical drawing
        try:
            if self.image_path.suffix.lower() == '.svg':
                from svglib.svglib import svg2rlg
                drawing = svg2rlg(str(self.image_path))  # Convert Path to string
                if drawing:
                    drawing.width *= 1.5  # Slightly smaller to fit better
                    drawing.height *= 1.5
                    self.story.append(drawing)
                    self.story.append(Spacer(1, 5))  # Minimal space after image
            else:
                # Calculate new image size
                img_width, img_height = resize_image(str(self.image_path), 10.5 * inch, 5.25 * inch)
                tech_drawing = Image(str(self.image_path), width=img_width, height=img_height)
                self.story.append(tech_drawing)
                self.story.append(Spacer(1, 5))  # Minimal space after image
        except Exception as e:
            print(f"Error loading technical drawing: {e}")

    def _add_specifications_section(self):
        """Improved section grouping with helper methods"""
        sections = self._group_specs_by_section()
        if not sections:
            print("Warning: No specification sections found!")
            return

        self.story.append(Paragraph("Technical Specifications", self.styles['Heading2']))
        self.story.append(Spacer(1, 10))

        col_width = self.table_width / 2.0

        table_style = [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Calibri'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 1.7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.7),
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#305496')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (1, 0), 'Calibri'),
            ('FONTSIZE', (0, 0), (1, 0), 10),
            ('FONTWEIGHT', (0, 0), (1, 0), 'BOLD'),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
        ]

        for section_title, section_data in sections.items():
            if section_data:
                table_data = [[section_title, '']]
                # Process each row to check for [k1] marker
                for row in section_data:
                    if len(row) >= 1 and '[k1]' in row[0].lower():
                        # Remove [k1] marker and add as merged cell
                        clean_text = row[0].replace('[k1]', '').replace('[K1]', '').strip()
                        table_data.append([clean_text, ''])
                        # Add span for this row
                        row_index = len(table_data) - 1
                        table_style.append(('SPAN', (0, row_index), (1, row_index)))
                        # Center align the merged cell
                        table_style.append(('ALIGN', (0, row_index), (1, row_index), 'CENTER'))
                    else:
                        table_data.append(row)

                section_table = Table(
                    table_data,
                    colWidths=[col_width, col_width],
                    spaceBefore=5,
                    spaceAfter=5
                )
                section_table.setStyle(table_style)
                self.story.append(KeepTogether([section_table, Spacer(1, 5)]))

    def _group_specs_by_section(self):
        """Helper method to group specifications by section"""
        sections = {}
        current_section = None
        
        for row in self.specs_data:
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

    def _add_product_info_section(self):
        """Improved column splitting logic"""
        products = [row for row in self.items_data[1:] if any(row)]  # Skip only header row
        table_data = self._create_product_table_data(products)
        # Get header from first row, removing [H1] marker if present
        header = self.items_data[0]
        # Process both header columns
        article_code_header = header[0]  # First column is Article code
        length_header = header[1]  # Second column is Length(m)
        if '[H1]' in length_header.upper():  # Check for marker case-insensitively
            length_header = length_header.split('[H1]')[0].strip()  # Keep original case

        self.story.append(Paragraph("Product Information", self.styles['Heading2']))
        self.story.append(Spacer(1, 10))

        all_products = [row for row in self.items_data[1:] if any(row)]
        num_column_pairs = 4
        total_columns = num_column_pairs * 2

        table_data = []
        # Add header rows repeated for each column pair
        header_row = []
        for _ in range(num_column_pairs):
            header_row.extend([article_code_header, length_header])  # Use both header columns
        table_data.append(header_row)

        products_per_column = (len(all_products) + num_column_pairs - 1) // num_column_pairs

        for row_idx in range(products_per_column):
            row_data = []
            for col_idx in range(num_column_pairs):
                product_idx = row_idx + (col_idx * products_per_column)
                if product_idx < len(all_products):
                    row_data.extend(all_products[product_idx])
                else:
                    row_data.extend(['', ''])  # Padding for empty cells
            table_data.append(row_data)

        col_width = self.table_width / total_columns

        items_table = Table(
            table_data,
            colWidths=[col_width] * total_columns,
            spaceBefore=5,
            spaceAfter=5
        )

        table_style_items = [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Calibri'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 1.7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#305496')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Calibri'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTWEIGHT', (0, 0), (-1, 0), 'BOLD'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ]
        items_table.setStyle(table_style_items)

        product_info_section = [items_table, Spacer(1, 5)]
        try:
            self.story.append(KeepTogether(product_info_section))
        except Exception as e:
            self.story.append(PageBreak())
            self.story.extend(product_info_section)

    def _create_product_table_data(self, products):
        """Helper method for product table creation"""
        products_per_column = (len(products) + self.NUM_PRODUCT_COLUMNS - 1) // self.NUM_PRODUCT_COLUMNS
        return [
            products[i*products_per_column:(i+1)*products_per_column] 
            for i in range(self.NUM_PRODUCT_COLUMNS)
        ]
