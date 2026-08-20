import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class CryptoUtils:
    
    @staticmethod
    def generate_key():
        return Fernet.generate_key()
    
    @staticmethod
    def encrypt_data(data, key):
        f = Fernet(key)
        if isinstance(data, str):
            data = data.encode()
        return f.encrypt(data)
    
    @staticmethod
    def decrypt_data(encrypted_data, key):
        f = Fernet(key)
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return f.decrypt(encrypted_data)
    
    @staticmethod
    def derive_key_from_codeword(codeword, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(codeword.encode())
        return base64.urlsafe_b64encode(key)
    
    @staticmethod
    def encrypt_click_points(points):
        key = Fernet.generate_key()
        f = Fernet(key)
        points_json = json.dumps(points)
        encrypted = f.encrypt(points_json.encode())
        return encrypted.decode(), key.decode()
    
    @staticmethod
    def decrypt_click_points(encrypted_points, key):
        f = Fernet(key.encode())
        decrypted = f.decrypt(encrypted_points.encode())
        return json.loads(decrypted.decode())
    
    @staticmethod
    def encrypt_file_with_codeword(file_data, codeword):
        salt = os.urandom(16)
        key = CryptoUtils.derive_key_from_codeword(codeword, salt)
        f = Fernet(key)
        encrypted_data = f.encrypt(file_data)
        return encrypted_data, base64.b64encode(salt).decode()
    
    @staticmethod
    def decrypt_file_with_codeword(encrypted_data, codeword, salt_b64):
        salt = base64.b64decode(salt_b64)
        key = CryptoUtils.derive_key_from_codeword(codeword, salt)
        f = Fernet(key)
        return f.decrypt(encrypted_data)
