import os

TARGET_DIR = "./files/"

def rotate_left(byte, bits):
    return ((byte << bits) & 0xff) | (byte >> (8 - bits))

def rotate_right(byte, bits):
    return ((byte >> bits) & 0xff) | ((byte << (8 - bits)) & 0xff)

def encrypt(filename, key):
    block_size = len(key)
    with open(TARGET_DIR + filename, "rb") as f:
        print(f"Reading from {TARGET_DIR + filename}")
        data = f.read()

    encrypted = bytearray()
    num_blocks = (len(data) + block_size - 1) // block_size

    for i in range(num_blocks):
        block = data[i * block_size : (i + 1) * block_size]
        if i == 0:
            enc_block = bytearray()
            for j, b in enumerate(block):
                t = b ^ key[j]
                random_lower = os.urandom(1)[0] & 0x01
                new_val = (t & 0xFE) | random_lower
                enc_block.append(new_val)
        else:
            offset = i % block_size
            rotated_key = key[offset:] + key[:offset]
            xor_result = bytes(b ^ k for b, k in zip(block, rotated_key))
            enc_block = bytes(rotate_left(b, 3) for b in xor_result)
        encrypted.extend(enc_block)

    out_filename = TARGET_DIR + filename + ".enc"
    with open(out_filename, "wb") as f:
        f.write(encrypted)
    print(f"[+] Encrypted file written to {out_filename}")


if __name__ == "__main__":
    key = os.urandom(16)
    print(bytes(key).hex())
    for subdir, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            encrypt(file, key)
