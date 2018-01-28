import ipfsapi
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import *
# from cryptography.hazmat.primitives.serialization.Encoding import PEM
# from cryptography.hazmat.primitives.serialization.PrivateFormat import PKCS8
from blockchain import Blockchain


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

    ##############
    # IPFS setup #
    ##############

    api = ipfsapi.connect('127.0.0.1', 5001)
    ipfs_file_handle = api.add('/tmp/encrypted.txt')
    ipfs_hash = ipfs_file_handle['Hash']
    ipfs_hash_bytes = ipfs_hash.encode(encoding='UTF-8')

    # Signature calculation

    hash_signature = private_key.sign(
        ipfs_hash_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    public_key_bytes = public_key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo)

    add_blockchain_entry(ipfs_hash_bytes, hash_signature, public_key_bytes, public_key_bytes)    

    os.remove('/tmp/encrypted.txt')

    return (serialized_private_key, blockchain_id)

    