# Datasheet Generator

A Python application for generating product datasheets in PDF format.

## Features

- Generates professional PDF datasheets from product specifications
- Supports multiple product types and configurations
- Customizable templates with company branding
- Automatic handling of technical drawings and images
- Robust error handling and fallback mechanisms

## Recent Changes

### Font Handling
- Improved font loading with graceful fallback to Helvetica when Calibri is unavailable
- Added support for both Calibri and Helvetica fonts in table formatting
- Enhanced error logging for font-related issues

### SVG Handling
- Updated SVG file format to be self-contained without external dependencies
- Improved error handling in SVG loading with fallback drawing
- Enhanced logging for SVG-related issues

### Code Improvements
- Refactored table formatter for better maintainability
- Updated test suite to handle font fallbacks
- Added comprehensive error handling throughout the application
- Improved logging with detailed error messages

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/datasheet_generator.git
cd datasheet_generator
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your product specifications in the appropriate format
2. Run the generator:
```bash
python main.py
```

The generated datasheets will be saved in the `generated_datasheets` directory.

## Project Structure

```
datasheet_generator/
├── datasheet/
│   ├── assets/
│   │   └── drawn_by.svg
│   ├── fonts/
│   │   ├── calibri.ttf
│   │   └── calibrib.ttf
│   ├── content_builder.py
│   ├── formatters.py
│   ├── generator.py
│   ├── image_handler.py
│   └── template_manager.py
├── tests/
│   ├── test_content_builder.py
│   ├── test_formatters.py
│   ├── test_generator.py
│   ├── test_image_handler.py
│   ├── test_integration.py
│   └── test_template_manager.py
├── generated_datasheets/
├── main.py
├── requirements.txt
└── README.md
```

## Dependencies

- Python 3.12+
- ReportLab
- svglib
- PyPDF2
- pytest (for testing)

## Testing

Run the test suite:
```bash
pytest -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License

## Third-Party Licenses  
This software uses components governed by the following licenses:  
- [LGPL-3.0](LICENSES/LGPL-3.0.txt) (svglib)  
- [BSD-3-Clause](LICENSES/BSD-3-Clause-reportlab.txt) (reportlab)  
- [BSD-3-Clause](LICENSES/BSD-3-Clause-PyPDF2.txt) (PyPDF2)
