import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Image, Table, Paragraph,
                               PageBreak, Spacer, KeepTogether, NextPageTemplate)
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from utils.image_utils import resize_image

class DatasheetGenerator:
    DEFAULT_IMAGE_SIZE = (10.5 * inch, 5.25 * inch)
    TABLE_WIDTH_RATIO = 0.73
    NUM_PRODUCT_COLUMNS = 4
    
    def __init__(self, product_id, specs_data, items_data, image_path, output_dir):
        self.product_id = product_id
        self.specs_data = specs_data
        self.items_data = items_data
        self.image_path = image_path
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self.story = []
        self.doc = self._init_doc()
        self.table_width = self.doc.width * self.TABLE_WIDTH_RATIO
        self.register_fonts()

    def _init_doc(self):
        file_path = os.path.join(self.output_dir, f"{self.product_id}_datasheet.pdf")
        # Define page templates with different margins
        doc = SimpleDocTemplate(
            file_path,
            pagesize=(A4[1], A4[0]),  # Landscape orientation
        )

        # First page template with no top margin
        first_page_frame = Frame(
            25 * mm,  # left margin
            25 * mm,  # bottom margin
            doc.width,  # width
            doc.height,  # full height for first page
            leftPadding=0,
            topPadding=0,
            rightPadding=0,
            bottomPadding=0
        )

        # Other pages template with normal margins
        other_pages_frame = Frame(
            25 * mm,  # left margin
            25 * mm,  # bottom margin
            doc.width,  # width
            doc.height - 50 * mm,  # height (subtracting top and bottom margins)
            leftPadding=0,
            topPadding=0,
            rightPadding=0,
            bottomPadding=0
        )

        doc.addPageTemplates([
            PageTemplate(id='FirstPage', frames=first_page_frame),
            PageTemplate(id='OtherPages', frames=other_pages_frame)
        ])

        return doc

    def register_fonts(self):
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        # Use font files from the fonts directory (relative to project root)
        font_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')
        calibri_regular = os.path.join(font_dir, 'calibri.ttf')
        calibri_bold = os.path.join(font_dir, 'calibrib.ttf')
        pdfmetrics.registerFont(TTFont('Calibri', calibri_regular))
        pdfmetrics.registerFont(TTFont('Calibri-Bold', calibri_bold))

    def generate(self):
        self._build_story()
        # Set first page template and switch for subsequent pages
        self.story.insert(0, NextPageTemplate(['FirstPage', 'OtherPages']))
        self.doc.build(self.story)

    def _build_story(self):
        self._add_technical_drawing()
        self._add_specifications_section()
        self._add_product_info_section()
        self._add_footer()

    def _add_technical_drawing(self):
        try:
            if self.image_path.lower().endswith('.svg'):
                from svglib.svglib import svg2rlg
                drawing = svg2rlg(self.image_path)
                if drawing:
                    drawing.width *= 1.5  # Slightly smaller to fit better
                    drawing.height *= 1.5
                    self.story.append(drawing)
                    self.story.append(Spacer(1, 5))  # Minimal space after image
            else:
                # Calculate new image size
                img_width, img_height = resize_image(self.image_path, 10.5 * inch, 5.25 * inch)
                tech_drawing = Image(self.image_path, width=img_width, height=img_height)
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
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
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
                table_data.extend(section_data)
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
        self.story.append(Paragraph("Product Information", self.styles['Heading2']))
        self.story.append(Spacer(1, 10))

        header = self.items_data[0]
        all_products = [row for row in self.items_data[1:] if any(row)]  # Skip only header row
        num_column_pairs = 4
        total_columns = num_column_pairs * 2  # Each pair has 2 columns

        table_data = []
        # Add header rows repeated for each column pair
        header_row = []
        for _ in range(num_column_pairs):
            header_row.extend(header)
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
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
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

    def _add_footer(self):
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Italic'],
            fontSize=8,
            textColor=colors.grey
        )
        footer = Paragraph(
            f"Revision: 1.0 | Date: {datetime.now().strftime('%Y-%m-%d')} | Author: Your Name",
            footer_style
        )
        self.story.append(Spacer(1, 20))
        self.story.append(footer)
