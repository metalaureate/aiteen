import os
import json
import csv
import argparse

# Function to recursively find JSON files
def find_json_files(base_directory):
    json_files = []
    for root, _, files in os.walk(base_directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files

# Function to recursively extract keys and their values, including subkeys
def extract_keys(data, json_file, parent_key=''):
    keys = {}
    for key, value in data.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            # Recursively extract subkeys
            keys.update(extract_keys(value, json_file, full_key))
        else:
            # Store the key-value pair
            keys[(full_key, json_file)] = value
    return keys

# Function to load English keys and values from the English JSON files
def load_english_data(en_json_files):
    en_data = {}
    for en_file in en_json_files:
        json_data, json_file = load_json(en_file)
        en_data.update(extract_keys(json_data, json_file))  # Extract subkeys as well
    return en_data

# Function to load translations for all locales
def load_locale_data(locale_files):
    locale_data = {}
    for locale_file in locale_files:
        json_data, json_file = load_json(locale_file)
        locale_data.update(extract_keys(json_data, json_file))  # Extract subkeys as well
    return locale_data

# Function to load a JSON file and return its content along with the file name
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f), os.path.basename(file_path)

# Function to create the CSV for QA purposes with json_file as the first column
def write_translation_comparison_csv(en_data, all_locale_data, output_file):
    # Prepare the header: json_file, key, English, and one column for each language
    locales = sorted(all_locale_data.keys())
    header = ["json_file", "key", "english"] + locales

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(header)

        # Iterate through the English data and write translations for each locale
        for (key, json_file), en_value in en_data.items():
            row = [json_file, key, en_value]
            for locale in locales:
                locale_translations = all_locale_data.get(locale, {})
                locale_translation_value = locale_translations.get((key, json_file), '')
                row.append(locale_translation_value)
            writer.writerow(row)

# Main function to extract data and generate the CSV
def generate_translation_comparison(base_path, en_locale_path, output_dir):
    # Load English data
    en_json_files = find_json_files(en_locale_path)
    en_data = load_english_data(en_json_files)

    # Load translations for all locales
    all_locale_data = {}
    other_locales = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d != 'en']

    for locale in other_locales:
        locale_path = os.path.join(base_path, locale)
        locale_files = find_json_files(locale_path)
        locale_data = load_locale_data(locale_files)
        all_locale_data[locale] = locale_data

    # Output the CSV file
    output_file = os.path.join(output_dir, 'locale_translation_comparison.csv')
    write_translation_comparison_csv(en_data, all_locale_data, output_file)
    print(f"Translation comparison CSV written to {output_file}")

# Main function to parse arguments and invoke appropriate functions
def main():
    parser = argparse.ArgumentParser(description="Script to output translations across locales for QA.")
    parser.add_argument("--en-locale-path", required=True, help="Path to the English locale directory.")
    parser.add_argument("--base-path", required=True, help="Base path for all locales (for comparison).")
    parser.add_argument("--output-dir", required=True, help="Directory to store the output CSV file.")

    args = parser.parse_args()

    generate_translation_comparison(args.base_path, args.en_locale_path, args.output_dir)

if __name__ == "__main__":
    main()

# Example usage:
# python i18n_qa.py --en-locale-path /path/to/en --base-path /path/to/locales --output-dir /path/to/output

# python i18n_qa.py  --en-locale-path /Users/possum/Projects/tari/universe/public/locales/en --base-path /Users/possum/Projects/tari/universe/public/locales --output-dir locale_comparison