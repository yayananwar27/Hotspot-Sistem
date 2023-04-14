from flask import current_app
from authlib.jose import jwt
import secrets
import random
import string

class create_token2():
    def __init__(self, panjang):
        self.panjang = int(panjang)
        self.karakter = string.ascii_letters+string.digits     
    def __str__(self):
        return ''.join(random.choices(self.karakter, k=self.panjang))


class create_token_jwt():
    def __init__(self, payload):
        self.payload = payload
    
    def get_token(self):
        header = {'alg':'HS256'}
        return jwt.encode(
        header, self.payload, current_app.config['SECRET_KEY']
        #header, self.payload, secrets.token_urlsafe(32)
    ).decode()