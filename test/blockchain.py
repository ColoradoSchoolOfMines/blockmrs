    
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

        self.blockchain.append((ipfs_hash, user_sig, user_public_key,
                                recipient_public_key))
        
        return len(self.blockchain) - 1

    
    def lookup_blockchain_entry(self, index):
        return self.blockchain[index]