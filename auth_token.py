from flask import current_app
from authlib.jose import jwt

class create_token():
    def __init__(self, payload):
        self.payload = payload
    
    def get_token(self):
        header = {'alg':'HS256'}
        return jwt.encode(
        header, self.payload, current_app.config['SECRET_KEY']
    ).decode()