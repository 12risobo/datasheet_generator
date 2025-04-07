#!/usr/bin/env python3
# /// script
# dependencies = [
#     "pytest==7.4.0",
#     "pytest-cov==4.1.0"
# ]
# ///

import pytest
from pathlib import Path
import tempfile
import shutil
import csv
import os
from reportlab.graphics.shapes import Drawing, Rect

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
        ["Type", "OM4"],
        ["Core diameter", "50µm"],
        ["Cladding diameter", "125µm"],
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
def sample_svg_file(tmp_path):
    svg_file = tmp_path / "test_drawing.svg"
    svg_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect width="100" height="100" fill="blue"/>
</svg>""")
    return svg_file

@pytest.fixture
def mock_svg_drawing():
    """Create a mock SVG drawing for testing."""
    drawing = Drawing(100, 100)
    drawing.add(Rect(0, 0, 100, 100, fillColor='blue'))
    return drawing

@pytest.fixture
def mock_assets_dir(tmp_path):
    """Create a mock assets directory with necessary files."""
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    
    # Create a simple drawn_by.svg file without text to avoid font issues
    drawn_by_svg = assets_dir / "drawn_by.svg"
    drawn_by_svg.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="45">
    <rect width="120" height="45" fill="#305496"/>
    <rect x="5" y="5" width="110" height="35" fill="#ffffff" fill-opacity="0.9"/>
</svg>""")
    
    return assets_dir

@pytest.fixture
def mock_fonts_dir(tmp_path):
    """Create a mock fonts directory."""
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    return fonts_dir 