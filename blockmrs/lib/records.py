import ipfsapi
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from blockchain import Blockchain
from cryptography.hazmat.primitives import serialization as serial


def store_record(data_bytes, user_password_hash):

    # Key generation and serialization

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )

    serialized_private_key = private_key.private_bytes(
        serial.Encoding.PEM,
        serial.PrivateFormat.PKCS8,
        serial.BestAvailableEncryption(user_password_hash),
    )

    public_key = private_key.public_key()

    serialized_public_key = public_key.public_bytes(
        serial.Encoding.PEM,
        serial.PublicFormat.SubjectPublicKeyInfo,
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

    ipfs_api = ipfsapi.connect('127.0.0.1', 5001)
    ipfs_file_handle = ipfs_api.add('/tmp/encrypted.txt')
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

    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


    blockchain = Blockchain('chain.dat')
    blockchain_id = blockchain.add_blockchain_entry(ipfs_hash_bytes, hash_signature,
                                                    public_key_bytes, public_key_bytes)

    os.remove('/tmp/encrypted.txt')
    return (serialized_private_key, blockchain_id)


def retrieve_record(blockchain_id, serialized_private_key, user_password_hash):

    blockchain = Blockchain('chain.dat')
    blockchain_entry = blockchain.lookup_blockchain_entry(blockchain_id)
    ipfs_hash = blockchain_entry[0].decode(encoding='UTF-8')

    ipfs_api = ipfsapi.connect('127.0.0.1', 5001)

    encrypted_file = ipfs_api.cat(ipfs_hash)

    private_key = serialization.load_pem_private_key(
        serialized_private_key,
        password=user_password_hash,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    public_key.verify(
        blockchain_entry[1],
        blockchain_entry[0],
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return private_key.decrypt(
        encrypted_file,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )

