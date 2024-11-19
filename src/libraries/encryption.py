from cryptography.fernet import Fernet
import base64
import os

# Vain ensimmäisellä kerralla pitää kutsua tämä funktio 
def generate_key():
    """Generoi salausavaimen ja tallenna se tiedostoon."""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Lataa salausavain tiedostosta
def load_key():
    """Lataa salausavain tiedostosta."""
    return open("secret.key", "rb").read()

# Salauksen suorittaminen
def encrypt_message(message: str) -> str:
    """Salataan viesti (esim. token) ja palautetaan se Base64-muodossa."""
    key = load_key()  # Ladataan avain
    encoded_message = message.encode()  # Muutetaan merkkijono byteiksi
    fernet = Fernet(key)  # Alustetaan salausobjekti
    encrypted_message = fernet.encrypt(encoded_message)  # Salataan viesti
    return base64.urlsafe_b64encode(encrypted_message).decode()  # Palautetaan salattu viesti base64-muodossa

# Viestin purkaminen
def decrypt_message(encrypted_message: str) -> str:
    """Puretaan aiemmin salattu viesti."""
    key = load_key()  # Ladataan avain
    encrypted_message = base64.urlsafe_b64decode(encrypted_message.encode())  # Puretaan Base64
    fernet = Fernet(key)  # Alustetaan salausobjekti
    decrypted_message = fernet.decrypt(encrypted_message)  # Puretaan salaus
    return decrypted_message.decode()  # Palautetaan alkuperäinen viesti
