import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization as serial
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


class Blockchain:
    def __init__(self, file_name):
        self.blockchain = []
        self.file_name = file_name

    @staticmethod
    def verify_ipfs_hash(ipfs_hash, user_sig, user_public_key):
        public_key = serial.load_der_public_key(user_public_key,
                                                backend=default_backend())
        try:
            public_key.verify(
                user_sig,
                ipfs_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def add_blockchain_entry(self, ipfs_hash, user_sig, user_public_key,
                             recipient_public_key):
        if not Blockchain.verify_ipfs_hash(ipfs_hash,
                                           user_sig,
                                           user_public_key):
            return False

        with open(self.file_name, 'ab') as chain_file:
            chain_file.write(ipfs_hash)
            chain_file.write(user_sig)
            chain_file.write(user_public_key)
            chain_file.write(recipient_public_key)

        with open(self.file_name, 'rb') as chain_file:
            return int(os.path.getsize(self.file_name))//1658 - 1

    def lookup_blockchain_entry(self, index):

        with open(self.file_name, 'rb') as chain_file:
            seek_index = index * 1658
            chain_file.seek(seek_index)

            ipfs_hash = chain_file.read(46)
            user_sig = chain_file.read(512)
            user_public_key = chain_file.read(550)
            recipient_public_key = chain_file.read(550)

        return {
            'ipfs_hash': ipfs_hash,
            'user_sig': user_sig,
            'user_public_key': user_public_key,
            'recipient_public_key': recipient_public_key
        }
