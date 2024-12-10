import os
import re

def parse_rest_file(file_path, base_url):
    """
    Parsi rest-tiedostosta moduulikommentti sekä pyyntöjen tyypit, urlit ja kommentit.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    variables = {"baseUrl": base_url}
    requests = []
    file_comment = ""  # Moduulidokumentaatio
    current_comment = ""  # Kommenttivarasto
    file_comment_set = False  # Onko tiedoston kommentti jo asetettu

    # Poistetaan alkuosa baseUrlista regexpillä (esimerkiksi http://localhost:8088)
    base_url = re.sub(r'^https?://[^/]+', '', base_url)

    for line in lines:
        line = line.strip()

        # Muuttujat
        if line.startswith("@"):
            key, value = line[1:].split(" = ", 1)
            variables[key] = value

        # Moduulikommentti (#)
        if line.startswith("#") and not file_comment_set:
            file_comment += line.strip("# ").strip() + "\n"
            file_comment_set = True  # Tallennetaan vain ensimmäinen

        # Pyyntöjen kommentit (###)
        elif line.startswith("###"):
            current_comment = line.strip("# ").strip()

        # HTTP-pyynnöt
        elif line.startswith(("GET", "POST", "PUT", "DELETE")):
            method, url = line.split(" ", 1)            
            # Poistetaan urlista localhost-osoite
            url = re.sub(r'^https?://[^/]+', '', url)
            # Korvataan viittaukset baseUrliin base_urlilla, josta on poistettu localhost-osoite
            url = url.replace("{{baseUrl}}", base_url)  
            url = re.sub(r"\{\{(\w+)\}\}", r"{\1}", url)  # Korvataan {{}} -> {}
            requests.append({
                "method": method,
                "url": url,
                "description": current_comment,
            })
            current_comment = ""  # Nollaa kommentti seuraavaa pyyntöä varten

    return file_comment, requests


def generate_combined_markdown(directory, base_url):
    """
    Luo markdown-tiedosto ja yhdistä siihen .rest-tiedostoista parsitut tiedot.
    """
    combined_md = "# REST API Dokumentaatio\n\n"
    combined_md += "Tämä dokumentaatio sisältää yleiskuvauksen .rest-testitiedostoista. Tarkempi Swagger-dokumentaatio löytyy [täältä](http://localhost:8088/docs).\n\n"
    for file_name in sorted(os.listdir(directory)):
        if file_name.endswith(".rest"):
            file_path = os.path.join(directory, file_name)
            file_comment, requests = parse_rest_file(file_path, base_url)

            combined_md += f"## {file_name}\n\n"
            combined_md += f"{file_comment}\n"
            combined_md += "| Pyyntö | Kuvaus |\n"
            combined_md += "|---|---|\n"
            for request in requests:                
                combined_md += f"| {request['method']} ```{request['url']}``` | {request['description']} |\n"
            combined_md += "\n"
    return combined_md



if __name__ == "__main__":
    input_directory = "requests"                # .rest-tiedostojen hakemisto
    output_file = "docs/rest_tests.md"          # Tulostiedosto
    base_url = "http://localhost:8088/api/v1"   # Base URL

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    combined_markdown = generate_combined_markdown(input_directory, base_url)

    # Tallennetaan Markdown-dokumentti
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(combined_markdown)