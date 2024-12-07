#!/bin/bash

# Tarkista, että MkDocs on asennettu
if ! command -v mkdocs &> /dev/null
then
    echo "MkDocs ei ole asennettu. Asenna se ensin komennolla: pip install mkdocs mkdocs-material mkdocstrings tai käynnistä docker-kontti"
    exit
fi

# Aja Python-skripti
echo "Valmistellaan rest-tiedostojen dokumentaatiota..."
python generate_rest_docs.py

# Buildaa dokumentaation MkDocsilla
echo "Rakennetaan dokumentaatiota..."
mkdocs build

# Tarkista onnistuiko 
if [ $? -eq 0 ]; then
    echo "Dokumentaatio rakennettu"

else
    echo "Dokumentaation rakennus epäonnistui."
    exit 1
fi

mkdocs serve