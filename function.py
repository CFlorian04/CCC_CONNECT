import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from datetime import datetime


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


###########################################################
# Fonctions de sécurité


def create_private_key() :
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    return private_key


def create_public_key(private_key) :
    public_key = private_key.public_key()

    return public_key


def bytes_private_key(private_key) :

    """
    private_hex = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).hex()
    """
    return "0" #private_hex

def bytes_public_key(public_key) :
    """
    public_hex = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).hex()
    """
    return "0" #public_hex

def crypted_message(message, public_key) :
    encrypted_message = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hash.SHA256()),
            algorithm=hash.SHA256(),
            label=None
        )
    )

    return encrypted_message


def decrypted_message(encrypted_message, private_key) :
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hash.SHA256()),
            algorithm=hash.SHA256(),
            label=None
        )
    )

    return decrypted_message



##############################
# Fonction de date


def get_current_date():
    return datetime.now()

def compare_dates(date1, date2, intervalMinutes):
    difference = date1 - date2
    difference_minutes = difference.total_seconds() / 60

    if difference_minutes > intervalMinutes:
        return False
    else:
        return True