# Scholarly Abstract Builder
This script will take a DBLP link and build a PDF book compiling all the abstracts of the conference proceedings.

# How to use
1. pip install -r requirements.txt
2. ```python scholarly_abstract_builder.py --link <DBLP Link> --title <Book Title> --notrack <Bool> --dump <Bool>```

# Example
```python scholarly_abstract_builder.py --link "https://dblp.org/db/conf/simbig/simbig2018.html" --title "SIMBig'2018" --notrack "True" --dump "False" --makebook "True" --makedata "False"```