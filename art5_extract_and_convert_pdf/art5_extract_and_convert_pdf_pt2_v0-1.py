import os
import camelot
import pandas as pd

# Script: Extract Tables from PDF into Separate CSVs with Combined Report
# By: Johannes Renders (j.a.m.renders@minfin.nl)
# Creation Date: 2024-08-28

# This script extracts tables from a PDF using both stream and lattice methods in camelot.
# The extracted tables are saved into separate folders, one for each method.
# Additionally, it generates a combined CSV report for all extracted tables.

# Get the directory where the .py script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define file paths relative to the script's location
pdf_path = os.path.join(script_dir, "Maandrapportage december 2023.pdf")
stream_table_output_dir = os.path.join(script_dir, "extracted_tables_stream")
lattice_table_output_dir = os.path.join(script_dir, "extracted_tables_lattice")
report_csv_path = os.path.join(script_dir, "table_extraction_report.csv")

# Create directories for output if they don't exist
os.makedirs(stream_table_output_dir, exist_ok=True)
os.makedirs(lattice_table_output_dir, exist_ok=True)

# Function to extract tables using a specific Camelot flavor (stream or lattice)
def extract_tables_with_flavor(pdf_path, flavor, output_dir, report_data):
    try:
        # Ensure Ghostscript is available for lattice method
        if flavor == 'lattice':
            try:
                import ghostscript
            except ImportError:
                raise RuntimeError("Ghostscript is required for the lattice flavor but not found.")

        tables = camelot.read_pdf(pdf_path, pages="all", flavor=flavor)
        
        if isinstance(tables, camelot.core.TableList) and len(tables) > 0:
            for idx, table in enumerate(tables):
                if isinstance(table.df, pd.DataFrame) and not table.df.empty:
                    # Use the page number and table index for the filename
                    page_num = table.page
                    table_filename = os.path.join(output_dir, f"tbl_p{page_num}_table_{idx + 1}.csv")
                    table.to_csv(table_filename, index=False)

                    # Append table report data to report_data list
                    report_data.append({
                        "page": page_num,
                        "table_index": idx + 1,
                        "method": flavor,
                        "accuracy": table.accuracy,
                        "whitespace": table.parsing_report.get('whitespace', 'N/A'),
                        "order": table.parsing_report.get('order', 'N/A'),
                        "text_size": table.parsing_report.get('text size', 'N/A'),
                        "text_density": table.parsing_report.get('text density', 'N/A')
                    })
                    print(f"Table from page {page_num} extracted using {flavor} and saved to {table_filename}")
                else:
                    print(f"No valid tables found on page {table.page} using {flavor}.")
        else:
            print(f"No valid tables found or Camelot did not return a TableList object using {flavor}.")
    except Exception as e:
        print(f"Error extracting tables using {flavor}: {e}")

# Main execution
report_data = []

# Extract tables using both stream and lattice methods
extract_tables_with_flavor(pdf_path, 'stream', stream_table_output_dir, report_data)
extract_tables_with_flavor(pdf_path, 'lattice', lattice_table_output_dir, report_data)

# Convert report_data to a DataFrame and save it to CSV
df_report = pd.DataFrame(report_data)
df_report.to_csv(report_csv_path, index=False)
print(f"Combined table extraction report saved to {report_csv_path}")

print("Table extraction completed.")
