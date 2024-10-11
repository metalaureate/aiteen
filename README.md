First run to audit strings (add empty dir if language is new)

python i18n_checker.py compare --en-locale-path /Users/possum/Projects/tari/universe/public/locales/en --base-path /Users/possum/Projects/tari/universe/public/locales --output-dir locale_comparison

then run to translate missing 

python i18n_translator.py

then run to update locale dir (copy from local dir to project)

python i18n_patch_locales.py 
then copy to project

then to output a qa matrix
python i18n_qa.py  --en-locale-path /Users/possum/Projects/tari/universe/public/locales/en --base-path /Users/possum/Projects/tari/universe/public/locales --output-dir locale_comparison

# aiteen
