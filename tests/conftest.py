import pytest
from pathlib import Path
import tempfile
import shutil
import csv
import os

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def sample_specs_data():
    """Sample specification data for testing."""
    return [
        ["Specifications cable (A) [H1]", ""],
        ["Type", "Patchcord - Duplex"],
        ["Outer diameter", "1.8mm"],
        ["Tensile strength", "90N (short time 150N)"],
        ["", ""],
        ["Specifications fiber [H1]", ""],
        ["Fiber type", "Multimode"],
        ["Fiber class", "OM4"],
        ["Diameter core / cladding", "50/125"],
    ]

@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return [
        ["Article code", "Length(m) [H1]"],
        ["RL9752", "0.25M"],
        ["RL9700", "0.50M"],
        ["RL9701", "1.00M"],
        ["RL9702", "2.00M"],
    ]

@pytest.fixture
def sample_csv_files(temp_dir, sample_specs_data, sample_product_data):
    """Create sample CSV files for testing."""
    specs_path = temp_dir / "specs.csv"
    products_path = temp_dir / "products.csv"
    
    # Write specs CSV
    with open(specs_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sample_specs_data)
    
    # Write products CSV
    with open(products_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sample_product_data)
    
    return {"specs": specs_path, "products": products_path}

@pytest.fixture
def sample_svg_file(temp_dir):
    """Create a sample SVG file for testing."""
    svg_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect width="100" height="100" fill="blue" />
        <text x="10" y="50" font-family="Arial" font-size="20" fill="white">Test</text>
    </svg>"""
    
    svg_path = temp_dir / "test_drawing.svg"
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    
    return svg_path

@pytest.fixture
def mock_assets_dir(temp_dir):
    """Create a mock assets directory with necessary files."""
    assets_dir = temp_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create a simple watermark PDF
    watermark_path = assets_dir / "Watermerk.pdf"
    # This is just a placeholder - in a real test we'd create a valid PDF
    with open(watermark_path, 'w') as f:
        f.write("Mock PDF content")
    
    # Create a drawn_by SVG
    drawn_by_path = assets_dir / "drawn_by.svg"
    svg_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <svg width="100" height="50" xmlns="http://www.w3.org/2000/svg">
        <text x="10" y="30" font-family="Arial" font-size="12" fill="black">Drawn By Test</text>
    </svg>"""
    with open(drawn_by_path, 'w') as f:
        f.write(svg_content)
    
    return assets_dir

@pytest.fixture
def mock_fonts_dir(temp_dir):
    """Create a mock fonts directory with placeholder font files."""
    fonts_dir = temp_dir / "fonts"
    fonts_dir.mkdir(exist_ok=True)
    
    # Create placeholder font files
    (fonts_dir / "calibri.ttf").touch()
    (fonts_dir / "calibrib.ttf").touch()
    
    return fonts_dir 