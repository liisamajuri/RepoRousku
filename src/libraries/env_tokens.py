"""
Moduuli tarjoaa apufunktioita ympäristömuuttujatiedoston käsittelyyn.
Se sisältää toiminnallisuudet access tokenien tallentamiseen, poistamiseen ja noutamiseen
ympäristötiedostosta.
"""
import os
from dotenv import load_dotenv

token_file= ".env"
key_gitlab_token = "GITLAB_TOKEN"
key_clockify_token = "CLOCKIFY_TOKEN"


def remove_tokens_from_env_file():
    """
    Poistaa ympäristötiedostosta tokenit
    """
    if os.path.exists(token_file):
        with open(token_file, "r") as file:
            lines = file.readlines()

        # Kirjoitetaan takaisin kaikki muut rivit paitsi poistettavat muuttujat
        with open(token_file, "w") as file:
            for line in lines:
                if not any(line.startswith(f"{var_name}=") for var_name in [key_gitlab_token, key_clockify_token]):
                    file.write(line)


def get_env_tokens():
    """
    Palauttaa ympäristöön tallennetut tokenit
    """
    os.environ.pop(key_gitlab_token, None)
    os.environ.pop(key_clockify_token, None)
    load_dotenv(override=True)
    env_gitlab_token = os.getenv(key_gitlab_token,"")
    env_clockify_token = os.getenv(key_clockify_token,"")

    return env_gitlab_token, env_clockify_token


def save_tokens_to_env(gitlab_token_value, clockify_token_value):
    """
    Tallentaa tokenit ympäristötiedostoon
    """
    with open(token_file, "w") as f:
        if gitlab_token_value:
            f.write(f"{key_gitlab_token}={gitlab_token_value}\n")

        if clockify_token_value:
            f.write(f"{key_clockify_token}={clockify_token_value}\n")