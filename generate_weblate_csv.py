#!/usr/bin/env python3
"""
Script to generate Weblate-compatible CSV files from original localization files.
This script traverses the 'original' directory, converts the header of all CSV files
from 'Key,SourceString,Comment' to 'source,target,developer_comments', and outputs
the files to the 'weblate' directory maintaining the original directory structure.
"""

import os
import csv
import shutil
from pathlib import Path


def convert_csv_header(input_file_path, output_file_path):
    """
    Convert CSV file header from 'Key,SourceString,Comment' to 'source,target,developer_comments'
    """
    with open(input_file_path, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    if not rows:
        return

    # Check if the header matches the expected format
    header = rows[0]
    if header == ["Key", "SourceString", "Comment"]:
        # Replace the header
        rows[0] = ["source", "target", "developer_comments"]
    else:
        print(f"Warning: Header doesn't match expected format in {input_file_path}")
        print(f"Header found: {header}")

    # Write to output file
    with open(output_file_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)


def process_all_csv_files():
    """
    Process all CSV files in the original directory and output to weblate directory
    """
    original_dir = Path("original")
    weblate_dir = Path("weblate")

    # Create weblate directory if it doesn't exist
    weblate_dir.mkdir(exist_ok=True)

    # Traverse all CSV files in original directory
    for csv_file in original_dir.rglob("*.csv"):
        # Get relative path from original directory
        relative_path = csv_file.relative_to(original_dir)

        # Construct output file path
        output_file_path = weblate_dir / relative_path

        # Create subdirectories if needed
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Processing {csv_file} -> {output_file_path}")

        # Convert the CSV file
        try:
            convert_csv_header(csv_file, output_file_path)
            print(f"Successfully processed: {output_file_path}")
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")


def main():
    """
    Main function to run the CSV conversion process
    """
    print("Starting CSV conversion process...")
    process_all_csv_files()
    print("CSV conversion completed!")


if __name__ == "__main__":
    main()
