"""
RepoRousku API -rajapinta toteutettuna FastAPI-sovelluksena, joka tarjoaa pääsyn PalikkaPalveluiden dataan.

Tässä tiedostossa määritellään API:n perustoiminnot.
"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """
    Tarkistaa API:n tilan.

    Returns:
        dict: API:n tilan ilmoittava viesti.
    """
    return {"status": "ok", "message": "Hyvä Liisa! API wörkkii oikein!"}
