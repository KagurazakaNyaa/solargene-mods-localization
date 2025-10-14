#!/usr/bin/env python3
"""
Script to generate Weblate-compatible CSV files from original localization files.
This script traverses the 'original' directory, converts the header of all CSV files
from 'Key,SourceString,Comment' to 'source,target,developer_comments', and outputs
the files to the 'weblate' directory maintaining the original directory structure.
If target files exist, it updates/inserts based on 'source' column.
"""

import os
import csv
import shutil
from pathlib import Path


def read_csv_to_dict(file_path):
    """Read CSV file and return a dictionary with 'source' as key"""
    data = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row.get("source", "")
                if source:  # Only include non-empty source entries
                    data[source] = {
                        "source": source,
                        "target": row.get("target", ""),
                        "developer_comments": row.get("developer_comments", ""),
                    }
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return data


def update_or_insert_existing_file(input_file_path, output_file_path):
    """
    Update existing file with new data, preserving existing entries for keys that don't exist
    """
    # Read existing data if file exists
    existing_data = read_csv_to_dict(output_file_path)

    # Read new data from input file
    new_data = {}
    try:
        with open(input_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row.get("Key", "")
                if not source:  # Skip rows with empty Key
                    continue

                target = row.get("SourceString", "")
                comment = row.get("Comment", "")

                new_data[source] = {
                    "source": source,
                    "target": target,
                    "developer_comments": comment,
                }
    except Exception as e:
        print(f"Error reading input file {input_file_path}: {e}")
        return

    # Merge: Update existing with new data, add new entries
    for key, new_row in new_data.items():
        if key in existing_data:
            # Update existing entry
            if not existing_data[key]["target"]:
                existing_data[key]["target"] = new_row["target"]
            if not existing_data[key]["developer_comments"]:
                existing_data[key]["developer_comments"] = new_row["developer_comments"]
        else:
            # Add new entry
            existing_data[key] = {
                "source": new_row["source"],
                "target": new_row["target"],
                "developer_comments": new_row["developer_comments"],
            }

    # Write back to output file
    try:
        with open(output_file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["source", "target", "developer_comments"]
            )
            writer.writeheader()
            for row in existing_data.values():
                if row["source"]:  # Only write rows with non-empty source
                    writer.writerow(row)
        print(f"Updated existing file: {output_file_path}")
    except Exception as e:
        print(f"Error writing to {output_file_path}: {e}")


def create_new_file(input_file_path, output_file_path):
    """
    Create a new file with converted headers and data
    """
    try:
        with open(input_file_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = []
            for row in reader:
                # Skip rows with empty Key
                if not row.get("Key", ""):
                    continue

                new_row = {
                    "source": row.get("Key", ""),
                    "target": row.get("SourceString", ""),
                    "developer_comments": row.get("Comment", ""),
                }
                rows.append(new_row)

        if not rows:
            return

        # Create directory structure if needed
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to output file
        with open(output_file_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(
                outfile, fieldnames=["source", "target", "developer_comments"]
            )
            writer.writeheader()
            writer.writerows(rows)

        print(f"Created new file: {output_file_path}")
    except Exception as e:
        print(f"Error processing {input_file_path}: {e}")


def process_all_csv_files():
    """
    Process all CSV files in the original directory and output to weblate directory
    """
    original_dir = Path("original")
    weblate_dir = Path("weblate")

    # Create weblate directory if it doesn't exist
    weblate_dir.mkdir(exist_ok=True)

    # Traverse all CSV files in original directory
    csv_files = list(original_dir.rglob("*.csv"))

    if not csv_files:
        print("No CSV files found in original directory")
        return

    print(f"Found {len(csv_files)} CSV files to process")

    for csv_file in csv_files:
        # Get relative path from original directory
        relative_path = csv_file.relative_to(original_dir)

        # Construct output file path
        output_file_path = weblate_dir / relative_path

        print(f"Processing {csv_file}")

        # Check if output file already exists
        if output_file_path.exists():
            update_or_insert_existing_file(csv_file, output_file_path)
        else:
            create_new_file(csv_file, output_file_path)


def main():
    """
    Main function to run the CSV conversion process
    """
    print("Starting CSV conversion process...")
    process_all_csv_files()
    print("CSV conversion completed!")


if __name__ == "__main__":
    main()
