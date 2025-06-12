import os
import shutil
import pandas as pd
import json
import re
import math
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Patch locale files with translations from CSV.')
    parser.add_argument('--source-locale-path', required=True, 
                       help='Path to the source locale directory (e.g., /path/to/project/public/locales)')
    parser.add_argument('--target-locale-path', default='locales',
                       help='Path to the target locale directory where patched files will be stored (default: locales)')
    parser.add_argument('--csv-file', default='locale_comparison/translated_locale_key_comparison_consolidated.csv',
                       help='Path to the CSV file with translations (default: locale_comparison/translated_locale_key_comparison_consolidated.csv)')
    parser.add_argument('--output-dir', default='locale_comparison',
                       help='Output directory for comparison files (default: locale_comparison)')
    return parser.parse_args()

def load_csv(file_path):
    """Load the CSV file and return it as a DataFrame."""
    return pd.read_csv(file_path)

def load_json(file_path):
    """Load a JSON file and return its content as a dictionary."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(file_path, data):
    """Save a dictionary as a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_directory_if_missing(directory_path):
    """Create a directory if it does not exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def copy_source_locales(source_locale_dir_path, locale_dir_path):
    """Copy all locale files from the source repository to the target locale directory."""
    if os.path.exists(source_locale_dir_path):
        shutil.copytree(source_locale_dir_path, locale_dir_path, dirs_exist_ok=True)
        print(f"Copied source locales from {source_locale_dir_path} to {locale_dir_path}")
    else:
        print(f"Source locale directory {source_locale_dir_path} does not exist.")

def find_json_files(base_directory):
    """Recursively find all JSON files in the specified directory."""
    json_files = []
    for root, _, files in os.walk(base_directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files

def update_nested_dict(d, keys, value):
    """Update a nested dictionary given a list of keys."""
    for key in keys[:-1]:
        if key in d and isinstance(d[key], str):
            d[key] = {}
        d = d.setdefault(key, {})
    d[keys[-1]] = value

def convert_to_valid_json(value):
    """Convert a string with single quotes to valid JSON."""
    if isinstance(value, str):
        value = re.sub(r"'", '"', value)
        value = value.replace('True', 'true').replace('False', 'false').replace('None', 'null')
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value

def handle_invalid_value(value):
    """Replace NaN with None."""
    if isinstance(value, float) and math.isnan(value):
        return None
    return value

def update_locale_json(locale, json_file, label_key, translated_value, locale_dir_path):
    """Update a JSON file with the new translation."""
    locale_folder_path = os.path.join(locale_dir_path, locale)
    locale_json_path = os.path.join(locale_folder_path, json_file)

    create_directory_if_missing(locale_folder_path)
    json_data = load_json(locale_json_path)

    keys = label_key.split('.')
    translated_value = convert_to_valid_json(translated_value)
    translated_value = handle_invalid_value(translated_value)

    update_nested_dict(json_data, keys, translated_value)
    save_json(locale_json_path, json_data)

def ensure_all_keys_present(locale, all_en_keys, locale_dir_path):
    """Ensure that all English keys are present in the locale JSON files."""
    locale_folder_path = os.path.join(locale_dir_path, locale)
    create_directory_if_missing(locale_folder_path)

    for json_file, keys in all_en_keys.items():
        locale_json_path = os.path.join(locale_folder_path, json_file)
        json_data = load_json(locale_json_path)

        for label_key, en_value in keys.items():
            if label_key not in json_data:
                update_nested_dict(json_data, label_key.split('.'), en_value)
        save_json(locale_json_path, json_data)

def load_all_en_keys(en_locale_dir_path):
    """Load all English keys to ensure consistency across locales."""
    all_en_keys = {}

    for json_file in find_json_files(en_locale_dir_path):
        file_basename = os.path.basename(json_file)
        en_data = load_json(json_file)
        all_en_keys[file_basename] = en_data

    return all_en_keys

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up paths from arguments
    source_locale_dir_path = args.source_locale_path
    locale_dir_path = args.target_locale_path
    csv_file_path = args.csv_file
    en_locale_dir_path = os.path.join(locale_dir_path, 'en')
    
    # Step 1: Copy the source locales to the target directory
    copy_source_locales(source_locale_dir_path, locale_dir_path)

    # Step 2: Load all English keys to use as a reference
    all_en_keys = load_all_en_keys(en_locale_dir_path)

    # Step 3: Ensure all locales have the necessary keys from English as a baseline
    for locale in os.listdir(locale_dir_path):
        if os.path.isdir(os.path.join(locale_dir_path, locale)) and locale != 'en':
            ensure_all_keys_present(locale, all_en_keys, locale_dir_path)

    # Step 4: Load the translation CSV
    df = load_csv(csv_file_path)

    # Step 5: Patch the locale files with the translated values
    for _, row in df.iterrows():
        locale = row['locale']
        json_file = row['json_file']
        label_key = row['label_key']
        translated_value = row['translated_value']

        if pd.notna(translated_value) and translated_value.strip() != "":
            print(f"Updating {locale}/{json_file}: {label_key} -> {translated_value}")
            update_locale_json(locale, json_file, label_key, translated_value, locale_dir_path)

if __name__ == "__main__":
    main()
