import csv

def read_csv(file_path):
    """Read CSV file with proper encoding handling"""
    rows = []
    try:
        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:  # Handle BOM
            reader = csv.reader(csvfile)
            for row in reader:
                # Strip whitespace from all cells and filter empty rows
                cleaned_row = [cell.strip() for cell in row]
                if any(cleaned_row):  # Skip completely empty rows
                    rows.append(cleaned_row)
    except UnicodeDecodeError:
        with open(file_path, newline='', encoding='latin-1') as csvfile:  # Fallback encoding
            reader = csv.reader(csvfile)
            for row in reader:
                cleaned_row = [cell.strip() for cell in row]
                if any(cleaned_row):
                    rows.append(cleaned_row)
    return rows
