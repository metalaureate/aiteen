import os
import pandas as pd
import json
import re
import math

# Paths to locales and CSV file
csv_file_path = 'locale_comparison/translated_locale_key_comparison_consolidated.csv'
locale_dir_path = 'locales'  # The directory where locale JSON files are stored

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

def update_nested_dict(d, keys, value):
    """Update a nested dictionary given a list of keys."""
    for key in keys[:-1]:
        # If the current key exists but is a string, convert it to a dictionary
        if key in d and isinstance(d[key], str):
            d[key] = {}  # Replace the string with an empty dictionary
        d = d.setdefault(key, {})  # Move deeper into the dictionary, create if not exists
    d[keys[-1]] = value  # Set the final key to the translated value

def convert_to_valid_json(value):
    """Attempt to convert a string with single quotes to valid JSON."""
    if isinstance(value, str):
        # Replace single quotes with double quotes
        # Also, ensure that True, False, and None are converted to their JSON equivalents
        value = re.sub(r"'", '"', value)  # Replace single quotes with double quotes
        value = value.replace('True', 'true').replace('False', 'false').replace('None', 'null')
    
    try:
        # Attempt to load the string as a JSON object
        return json.loads(value)
    except (ValueError, TypeError):
        # If it fails, return the original value (likely a plain string)
        return value

def handle_invalid_value(value):
    """Check for invalid values like NaN and replace with None (which becomes null in JSON)."""
    if isinstance(value, float) and math.isnan(value):
        return None  # Return None for NaN values
    return value

def update_locale_json(locale, json_file, label_key, translated_value):
    """Update a JSON file with the new translation."""
    # Construct the path to the locale's JSON file
    locale_folder_path = os.path.join(locale_dir_path, locale)
    locale_json_path = os.path.join(locale_folder_path, json_file)

    # Ensure the locale folder exists
    create_directory_if_missing(locale_folder_path)

    # Load the existing JSON data (if the file exists)
    json_data = load_json(locale_json_path)

    # Handle nested keys (e.g., 'tabs.general')
    keys = label_key.split('.')  # Split label_key by '.' to handle nested keys

    # Ensure the translated value is in valid JSON format
    translated_value = convert_to_valid_json(translated_value)

    # Handle NaN values and replace them with None
    translated_value = handle_invalid_value(translated_value)

    # Update the JSON data with the new translation
    update_nested_dict(json_data, keys, translated_value)

    # Save the updated JSON file
    save_json(locale_json_path, json_data)

def main():
    # Load the translation CSV
    df = load_csv(csv_file_path)

    # Iterate over each row in the CSV
    for _, row in df.iterrows():
        locale = row['locale']
        json_file = row['json_file']
        label_key = row['label_key']
        translated_value = row['translated_value']

        # Only update if translated_value is not NaN or empty
        if pd.notna(translated_value) and translated_value.strip() != "":
            # Update the locale's JSON file with the translated value
            print(f"Updating {locale}/{json_file}: {label_key} -> {translated_value}")
            update_locale_json(locale, json_file, label_key, translated_value)

if __name__ == "__main__":
    main()
