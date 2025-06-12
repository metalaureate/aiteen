# Internationalization (i18n) Management Workflow

This repository contains a suite of tools for managing internationalization (i18n) in projects. The workflow consists of four main steps:

## Workflow Overview

### 1. Audit Strings (Check for Missing Translations)
First, run the checker to identify missing translations and generate comparison files:

```bash
python i18n_checker.py compare \
  --en-locale-path /Users/possum/Projects/tari/universe/public/locales/en \
  --base-path /Users/possum/Projects/tari/universe/public/locales \
  --output-dir locale_comparison
```

This will:
- Create empty directories for new languages if they don't exist
- Generate CSV files comparing English keys with other locales
- Identify missing or untranslated strings

### 2. Translate Missing Strings
Run the translator to automatically translate missing strings using AI:

```bash
python i18n_translator.py \
  --input-dir locale_comparison \
  --output-dir locale_comparison
```

This will:
- Read the comparison files from step 1
- Use OpenAI to translate missing strings
- Generate updated CSV files with translations

### 3. Patch Locale Files
Apply the translations to your local locale directory:

```bash
python i18n_patch_locales.py \
  --source-locale-path /Users/possum/Projects/tari/universe/public/locales \
  --target-locale-path locales \
  --csv-file locale_comparison/translated_locale_key_comparison_consolidated.csv
```

This will:
- Copy source locale files to a local directory
- Apply all translations from the CSV file
- Ensure all locales have the same key structure as English

### 4. Quality Assurance Check
Generate a QA matrix to review translations:

```bash
python i18n_qa.py \
  --en-locale-path /Users/possum/Projects/tari/universe/public/locales/en \
  --base-path /Users/possum/Projects/tari/universe/public/locales \
  --output-dir locale_comparison
```

This will generate reports showing translation coverage and quality metrics.

## Example: WXTM Bridge Project

For the WXTM Bridge project, use these commands:

```bash
# 1. Check for missing translations
python i18n_checker.py compare \
  --en-locale-path /Users/possum/Projects/tari/wxtm-bridge/wxtm-bridge-frontend/public/locales/en \
  --base-path /Users/possum/Projects/tari/wxtm-bridge/wxtm-bridge-frontend/public/locales \
  --output-dir locale_comparison_wxtm

# 2. Translate missing strings
python i18n_translator.py \
  --input-dir locale_comparison_wxtm \
  --output-dir locale_comparison_wxtm

# 3. Patch locale files
python i18n_patch_locales.py \
  --source-locale-path /Users/possum/Projects/tari/wxtm-bridge/wxtm-bridge-frontend/public/locales \
  --target-locale-path locales \
  --csv-file locale_comparison_wxtm/translated_locale_key_comparison_consolidated.csv

# 4. Copy to project (omit the en folder)
After running the workflow, copy the updated locale files from the `locales` directory back to your project:

```bash
cp -r locales/* /path/to/your/project/public/locales/
```

# 5. QA check final repo
```bash
python i18n_qa.py \
  --en-locale-path /Users/possum/Projects/tari/wxtm-bridge/wxtm-bridge-frontend/public/locales/en \
  --base-path /Users/possum/Projects/tari/wxtm-bridge/wxtm-bridge-frontend/public/locales \
  --output-dir locale_comparison_wxtm
```



## Requirements

- Python 3.x
- Required packages: `pandas`, `openai`, `python-dotenv`
- OpenAI API key (set in `.env` file as `OPENAI_API_KEY`)

## Output Files

The workflow generates several CSV files for analysis:
- `english_labels.csv` - All English strings
- `locale_key_comparison_consolidated.csv` - Missing translation comparison
- `translated_locale_key_comparison_consolidated.csv` - With AI translations
- `locale_translation_comparison.csv` - QA matrix