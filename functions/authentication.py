import jwt

encoded_jwt = jwt.encode({'username':'philippe'}, 'secret')
print(encoded_jwt)


decoded_jwt = jwt.decode(encoded_jwt, 'secret')
print(decoded_jwt)


# TODO Implement PyJWT-Authorization - vielleicht auch über eine def

def authenticate_user(token):
    return jwt.decode(token, 'secret')