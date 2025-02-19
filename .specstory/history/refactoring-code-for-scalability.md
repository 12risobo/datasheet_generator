## SpecStory

## Refactoring Code for Scalability (2/13/2025, 3:18:38 PM)

_**User**_

I want to refactor this code, in the future it will be used for other datasheets so it should be scalable and easily changeable. The current main.py is quit large, perhaps split it up? 

---

_**Assistant**_

Below is one way to refactor your code so that it’s more modular and more easily extended in the future. The idea is to separate concerns into different modules/packages. For example, you can:

- **Move CSV reading and image utilities to a “utils” package.**
- **Place the datasheet-generation logic into its own module (or even a class in a package) so that new datasheet types can inherit or extend the base functionality.**
- **Keep the main entry point (main.py) very thin.**

Below is an example refactoring with the following structure:

```
your_project/
├── main.py
├── datasheet
│   ├── __init__.py
│   └── datasheet_generator.py
├── utils
│   ├── __init__.py
│   ├── csv_reader.py
│   └── image_utils.py
└── fonts
    ├── calibrib.ttf
    └── calibri.ttf
```

---

### 1. **Entry Point: main.py**

This file now just reads CSV data and instantiates your datasheet generator.

```python:main.py
import os
from utils.csv_reader import read_csv
from datasheet.datasheet_generator import DatasheetGenerator

def main():
    specs_data = read_csv('data/specs.csv')
    items_data = read_csv('data/productrange.csv')
    output_dir = 'generated_datasheets'
    os.makedirs(output_dir, exist_ok=True)

    # Use the product codes from productrange.csv and generate a datasheet per product.
    for product in items_data[2:]:
        product_id = product[0]  # e.g., RL9752
        if product_id:
            generator = DatasheetGenerator(
                product_id=product_id,
                specs_data=specs_data,
                items_data=items_data,
                image_path='assets/cable_drawing.png',
                output_dir=output_dir
            )
            generator.generate()

if __name__ == "__main__":
    main()
```

---

### 2. **Datasheet Generation: datasheet/datasheet_generator.py**

Here we encapsulate all the PDF-generation logic into a class. You can later extend this class (or write alternatives) for different datasheet types if needed.

```python:datasheet/datasheet_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Image, Table, Paragraph,
                                PageBreak, Spacer, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib import colors

class DatasheetGenerator:
    def __init__(self, product_id, specs_data, items_data, image_path, output_dir):
        self.product_id = product_id
        self.specs_data = specs_data
        self.items_data = items_data
        self.image_path = image_path
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self.story = []
        self.doc = self._init_doc()
        # Calculate table width (73% of available width)
        self.table_width = self.doc.width * 0.73
        self.register_fonts()

    def _init_doc(self):
        file_path = os.path.join(self.output_dir, f"{self.product_id}_datasheet.pdf")
        doc = SimpleDocTemplate(
            file_path,
            pagesize=(A4[1], A4[0]),  # Landscape orientation
            leftMargin=25 * mm,
            rightMargin=25 * mm,
            topMargin=25 * mm,
            bottomMargin=25 * mm,
        )
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
        self.doc.build(self.story)

    def _build_story(self):
        self._add_technical_drawing()
        self._add_specifications_section()
        self._add_product_info_section()
        self._add_footer()

    def _add_technical_drawing(self):
        # Add technical drawing with proper format handling
        self.story.append(Spacer(1, 20))
        try:
            if self.image_path.lower().endswith('.svg'):
                from svglib.svglib import svg2rlg
                drawing = svg2rlg(self.image_path)
                if drawing:
                    drawing.width *= 1.75
                    drawing.height *= 1.75
                    self.story.append(drawing)
                    self.story.append(Spacer(1, 20))
            else:
                from utils.image_utils import resize_image
                # Calculate new image size
                img_width, img_height = resize_image(self.image_path, 10.5 * inch, 5.25 * inch)
                tech_drawing = Image(self.image_path, width=img_width, height=img_height)
                self.story.append(tech_drawing)
                self.story.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error loading technical drawing: {e}")

    def _add_specifications_section(self):
        # Group specifications data by sections
        section_headers = [
            'Specifications cable (A)',
            'Specifications Connector (B, C)',
            'Specifications fiber',
            'Specifications optical performance',
            'Standard compliances'
        ]
        current_section = None
        sections = {}
        for row in self.specs_data:
            if not any(row):
                continue
            if row[0] in section_headers:
                current_section = row[0]
                sections[current_section] = []
            elif current_section and len(row) == 2:
                sections[current_section].append(row)

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
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#104861')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (1, 0), 'Calibri'),
            ('FONTSIZE', (0, 0), (1, 0), 10),
            ('FONTWEIGHT', (0, 0), (1, 0), 'BOLD'),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
        ]

        for section_title, section_data in sections.items():
            if section_data:  # Only create table if there’s data
                table_data = [[section_title, '']]  # Header row (the header spans two columns)
                table_data.extend(section_data)
                section_table = Table(
                    table_data,
                    colWidths=[col_width, col_width],
                    spaceBefore=5,
                    spaceAfter=5
                )
                section_table.setStyle(table_style)
                self.story.append(KeepTogether([section_table, Spacer(1, 5)]))

    def _add_product_info_section(self):
        self.story.append(Paragraph("Product Information", self.styles['Heading2']))
        self.story.append(Spacer(1, 10))

        header = self.items_data[0]
        all_products = [row for row in self.items_data[2:] if any(row)]
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#104861')),
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
```

---

### 3. **CSV Utilities: utils/csv_reader.py**

A simple CSV reader utility, which can now be reused across your project.

```python:utils/csv_reader.py
import csv

def read_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader]
```

---

### 4. **Image Utilities: utils/image_utils.py**

This module is responsible for handling image resizing.

```python:utils/image_utils.py
from PIL import Image as PILImage

def resize_image(image_path, max_width, max_height):
    with PILImage.open(image_path) as img:
        img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
        return img.size
```

---

## Summary

- **`main.py`** is now very lean and only orchestrates the work.
- **`datasheet/datasheet_generator.py`** contains a `DatasheetGenerator` class with helper methods for adding different sections to the PDF. This makes it easier to add alternative layouts or datasheet types in the future (e.g., by subclassing or adding new methods).
- **`utils/`** contains helper functions for tasks like reading CSVs and resizing images, keeping your core logic clean and focused.

This modular structure makes your code more scalable and maintainable as your project grows.

---



---

