blockchain = []


def add_blockchain_entry(ipfs_hash, user_sig, user_public_key,
                         recipient_public_key):
    # with open('chain.dat', 'ab') as chain_file:
    #     chain_file.write(ipfs_hash)
    #     chain_file.write(user_sig)
    #     chain_file.write(user_public_key)
    #     chain_file.write(recipient_public_key)
    blockchain.append([ipfs_hash, user_sig, user_public_key,
                       recipient_public_key])
