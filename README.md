# Datasheet Generator

A Python tool for automatically generating PDF datasheets from CSV specification files and SVG technical drawings.

## Overview

This project provides a modular and customizable framework for generating professional-looking datasheets from structured data. It's particularly useful for creating product specification sheets, technical documentation, and standardized reports.

Key features:
- Convert CSV data into formatted tables
- Include SVG technical drawings
- Customize layout and styling
- Generate consistent PDF outputs with watermarks
- Support for multiple page templates

## Project Structure

```
.
├── assets/               # SVG drawings and watermark assets
├── data/                 # Input CSV data files
├── datasheet/            # Core datasheet generation modules
│   ├── generator.py      # Main orchestrator
│   ├── template_manager.py # PDF templates and frames
│   ├── content_builder.py # Content section building
│   ├── image_handler.py  # Technical drawing processing
│   └── formatters.py     # Table and text formatting 
├── fonts/                # Font files
├── tests/                # Test suite
├── utils/                # Utility functions
├── main.py               # Entry point script
└── requirements.txt      # Project dependencies
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/datasheets.git
   cd datasheets
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the main script to generate a datasheet:

```bash
python main.py
```

This will:
1. Read specification data from `data/specs.csv`
2. Read product range data from `data/productrange.csv`
3. Include the technical drawing from `assets/cable_drawing.svg`
4. Generate a PDF datasheet in the `generated_datasheets` directory

### Customization

To create your own datasheet:

1. Prepare your CSV data files with specifications and product information
2. Add your SVG technical drawing to the assets folder
3. Modify the `main.py` file to point to your data files:

```python
specs_data = read_csv('path/to/your/specs.csv')
items_data = read_csv('path/to/your/products.csv')
image_path = Path('assets') / 'your_drawing.svg'
```

4. Change the product ID if needed:
```python
generator = DatasheetGenerator(
    product_id="YOUR_PRODUCT_ID",
    specs_data=specs_data,
    items_data=items_data,
    image_path=image_path,
    output_dir=output_dir
)
```

## CSV Format

### Specifications CSV

The specifications CSV should have the following format:
- Sections with headers marked with [H1]
- Property-value pairs in each section

Example:
```csv
Specifications cable (A) [H1],
Type,Patchcord - Duplex
Outer diameter,1.8mm
Tensile strength,90N (short time 150N)

Specifications fiber [H1],
Fiber type,Multimode
Fiber class,OM4
Diameter core / cladding,50/125
```

### Product Range CSV

The product range CSV should have:
- A header row with column names
- Product data rows

Example:
```csv
Article code,Length(m) [H1]
RL9752,0.25M
RL9700,0.50M
RL9701,1.00M
```

## Testing

The project includes a comprehensive test suite using pytest. To run the tests:

```bash
pytest
```

To run only unit tests (skip integration tests):

```bash
pytest -m "not integration"
```

To run with coverage report:

```bash
pytest --cov=datasheet tests/
```

## Architecture

The datasheet generator uses a modular architecture:

- **Generator**: Main orchestrator that coordinates the generation process
- **Template Manager**: Handles PDF templates, frames, and page decorations
- **Content Builder**: Builds content sections (specifications, products)
- **Image Handler**: Handles technical drawings and SVGs
- **Formatters**: Table and text formatting utilities

## Dependencies

- reportlab: PDF generation
- svglib: SVG processing
- Pillow: Image handling
- PyPDF2: PDF manipulation
- pytest: Testing framework

## License

[Add your chosen license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
