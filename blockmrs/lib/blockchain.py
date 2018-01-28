import csv


class Blockchain:
    def __init__(self, file_name):
        self.blockchain = []
        self.file_name = file_name

        try:
            with open(self.file_name + '.len', 'r', newline='') as len_file:
                reader = csv.reader(len_file, delimiter=',')
                self.lengths = []
                for row in reader:
                    for elem in row:
                        self.lengths.append(elem)
        except OSError:
            self.lengths = []

    def add_blockchain_entry(self, ipfs_hash, user_sig, user_public_key,
                             recipient_public_key):
        if len(self.lengths) == 0:
            self.lengths = [len(x) for x in (ipfs_hash,
                                             user_sig,
                                             user_public_key,
                                             recipient_public_key)]
            with open(self.file_name + '.len', 'w', newline='') as len_file:
                writer = csv.writer(len_file, delimiter=',')
                writer.writerow(self.lengths)

        with open(self.file_name, 'ab') as chain_file:
            chain_file.write(ipfs_hash)
            chain_file.write(user_sig)
            chain_file.write(user_public_key)
            chain_file.write(recipient_public_key)

        self.blockchain.append((ipfs_hash, user_sig, user_public_key,
                                recipient_public_key))
        self.lengths.append((len(ipfs_hash), len(user_sig),
                             len(user_public_key), len(recipient_public_key)))

        return len(self.blockchain) - 1

    def lookup_blockchain_entry(self, index):
        '''
        Returns ipfs_hash, user_sig, user_public_key,
        recipient_public_key
        '''

        with open(self.file_name, 'rb') as chain_file:
            ipfs_hash = chain_file.read(self.lengths[index][0])
            user_sig = chain_file.read(self.lengths[index][1])
            user_public_key = chain_file.read(self.lengths[index][2])
            recipient_public_key = chain_file.read(self.lengths[index][3])

        if (ipfs_hash != self.blockchain[index][0] or
                user_sig != self.blockchain[index][1] or
                user_public_key != self.blockchain[index][2] or
                recipient_public_key != self.blockchain[index][3]):
            raise Exception('Blockchain in memory does '
                            'not match blockchain file')

        return ipfs_hash, user_sig, user_public_key, recipient_public_key
