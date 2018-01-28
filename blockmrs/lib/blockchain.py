import os


class Blockchain:
    def __init__(self, file_name):
        self.blockchain = []
        self.file_name = file_name

    def add_blockchain_entry(self, ipfs_hash, user_sig, user_public_key,
                             recipient_public_key):

        with open(self.file_name, 'ab') as chain_file:
            chain_file.write(ipfs_hash)
            chain_file.write(user_sig)
            chain_file.write(user_public_key)
            chain_file.write(recipient_public_key)

        with open(self.file_name, 'rb') as chain_file:
            return int(os.path.getsize('/tmp/bullshit.dat'))//1658 - 1




    def lookup_blockchain_entry(self, index):

        with open(self.file_name, 'rb') as chain_file:
            seek_index = index * 1658
            chain_file.seek(seek_index)

            ipfs_hash = chain_file.read(46)
            user_sig = chain_file.read(512)
            user_public_key = chain_file.read(550)
            recipient_public_key = chain_file.read(550)


        return ipfs_hash, user_sig, user_public_key, recipient_public_key
