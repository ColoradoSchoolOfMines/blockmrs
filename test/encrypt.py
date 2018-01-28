from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import *
# from cryptography.hazmat.primitives.serialization.Encoding import PEM
# from cryptography.hazmat.primitives.serialization.PrivateFormat import PKCS8



def store_record(data_bytes, user_password_hash):

    # Key generation and serialization

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )

    serialized_private_key = private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        BestAvailableEncryption(user_password_hash),
    )
 
    public_key = private_key.public_key()

    serialized_public_key = public_key.public_bytes(
        Encoding.PEM,
        PublicFormat.SubjectPublicKeyInfo,
    )

    ciphertext = public_key.encrypt(
        data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )

    with open('/tmp/encrypted.txt', 'wb') as encrypted_file:
        encrypted_file.write(ciphertext)



    return (serialized_)