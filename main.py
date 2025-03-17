from pathlib import Path
import os
import logging
from utils.csv_reader import read_csv
from datasheet.generator import DatasheetGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Generate a datasheet for the product."""
    # Read CSV files
    specs_data = read_csv('data/specs.csv')
    items_data = read_csv('data/productrange.csv')
    
    image_path = Path('assets') / 'cable_drawing.svg'
    
    # Create generated_datasheets directory if it doesn't exist
    output_dir = Path('generated_datasheets')
    output_dir.mkdir(exist_ok=True)

    # Generate a single datasheet with all products
    logger.info(f"Generating datasheet for product RL97xx")
    generator = DatasheetGenerator(
        product_id="RL97xx",  # Generic product ID for the series
        specs_data=specs_data,
        items_data=items_data,
        image_path=image_path,
        output_dir=output_dir
    )
    generator.generate()
    logger.info(f"Datasheet generation complete")

if __name__ == "__main__":
    main()