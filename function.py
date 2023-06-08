import hashlib


def encrypt_password(password):
    # Convertir le mot de passe en bytes
    password_bytes = password.encode('utf-8')

    # Calculer le hachage SHA-256 du mot de passe
    sha256_hash = hashlib.sha256(password_bytes)

    # Convertir le hachage en une chaîne hexadécimale
    encrypted_password = sha256_hash.hexdigest()

    return encrypted_password

def check_password(password, encrypted_password):
    
    return encrypted_password == encrypt_password(password)
