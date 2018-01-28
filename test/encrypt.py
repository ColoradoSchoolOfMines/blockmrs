from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import *
# from cryptography.hazmat.primitives.serialization.Encoding import PEM
# from cryptography.hazmat.primitives.serialization.PrivateFormat import PKCS8

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend()
)

with open('private_key.pem', 'wb') as key_file:
    serialized_private_key = private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        BestAvailableEncryption(b'test')
    )
    key_file.write(serialized_private_key)

public_key = private_key.public_key()

with open('public_key.pub', 'wb') as key_file:
    serialized_public_key = public_key.public_bytes(
        Encoding.PEM,
        PublicFormat.SubjectPublicKeyInfo,
    )
    key_file.write(serialized_public_key)

with open('data.txt', 'rb') as data_file:
    message = data_file.read()

ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA1()),
        algorithm=hashes.SHA1(),
        label=None
    )
)

with open('encrypted.txt', 'wb') as encrypted_file:
    encrypted_file.write(ciphertext)
