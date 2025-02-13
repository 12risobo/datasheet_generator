import os
from utils.csv_reader import read_csv
from datasheet.datasheet_generator import DatasheetGenerator

def main():
    # Read CSV files
    specs_data = read_csv('data/specs.csv')
    items_data = read_csv('data/productrange.csv')
    
    image_path = os.path.join('assets', 'cable_drawing.svg')
    
    # Create generated_datasheets directory if it doesn't exist
    output_dir = 'generated_datasheets'
    os.makedirs(output_dir, exist_ok=True)

    # Use the product codes from productrange.csv and generate a datasheet per product
    for product in items_data[2:]:
        product_id = product[0]  # e.g., RL9752
        if product_id:
            generator = DatasheetGenerator(
                product_id=product_id,
                specs_data=specs_data,
                items_data=items_data,
                image_path=image_path,
                output_dir=output_dir
            )
            generator.generate()

if __name__ == "__main__":
    main()