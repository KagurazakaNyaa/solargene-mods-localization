#!/usr/bin/env python3
"""
Script to apply translations from Weblate CSV files to original localization files.
This script reads original CSV files and applies translations from weblate CSV files,
then outputs the result to the target directory maintaining the original structure.
"""

import os
import csv
import shutil
from pathlib import Path


def read_translation_map(file_path):
    """Read translation CSV file and return a dictionary with 'source' as key"""
    translation_map = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row.get("source", "")
                if source:  # Only include non-empty source entries
                    translation_map[source] = {
                        "target": row.get("target", ""),
                        "developer_comments": row.get("developer_comments", ""),
                    }
    except Exception as e:
        print(f"Error reading translation file {file_path}: {e}")
    return translation_map


def apply_translation_to_original(input_file_path, translation_map, output_file_path):
    """
    Apply translations to original file and write to target
    """
    try:
        with open(input_file_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = []
            for row in reader:
                key = row.get("Key", "")
                source_string = row.get("SourceString", "")
                comment = row.get("Comment", "")

                # Apply translation if available
                if key in translation_map:
                    translated_target = translation_map[key]["target"]
                    if translated_target:
                        # Use translated target if available
                        source_string = translated_target

                new_row = {
                    "Key": key,
                    "SourceString": source_string,
                    "Comment": comment,
                }
                rows.append(new_row)

        if not rows:
            return

        # Create directory structure if needed
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to output file with original header format
        with open(output_file_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(
                outfile,
                fieldnames=["Key", "SourceString", "Comment"],
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writeheader()
            writer.writerows(rows)

        print(f"Applied translation to file: {output_file_path}")
    except Exception as e:
        print(f"Error processing {input_file_path}: {e}")


def process_all_csv_files():
    """
    Process all CSV files in the original directory, applying translations,
    and output to the target directory
    """
    original_dir = Path("original")
    weblate_dir = Path("weblate")
    target_dir = Path("target")

    # Create target directory if it doesn't exist
    target_dir.mkdir(exist_ok=True)

    # Get all CSV files from original directory (recursively)
    csv_files = list(original_dir.rglob("*.csv"))

    if not csv_files:
        print("No CSV files found in original directory")
        return

    print(f"Found {len(csv_files)} CSV files to process")

    for csv_file in csv_files:
        # Get relative path from original directory
        relative_path = csv_file.relative_to(original_dir)

        # Construct weblate file path
        weblate_file_path = weblate_dir / relative_path

        # Construct target file path
        target_file_path = target_dir / relative_path

        print(f"Processing {csv_file}")

        # Read translation map if weblate file exists
        translation_map = {}
        if weblate_file_path.exists():
            translation_map = read_translation_map(weblate_file_path)
            print(f"  Loaded translation data from {weblate_file_path}")
        else:
            print(f"  No translation file found at {weblate_file_path}")

        # Apply translation to original file and write to target
        apply_translation_to_original(csv_file, translation_map, target_file_path)


def main():
    """
    Main function to run the translation application process
    """
    print("Starting translation application process...")
    process_all_csv_files()
    print("Translation application completed!")


if __name__ == "__main__":
    main()
