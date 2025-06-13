import time
import re
import os
from itertools import zip_longest

class PRNG:
    def __init__(self, x, y, counter=0):
        self.x = x
        self.y = y
        self.counter = counter

    def rand(self):
        t = (self.x^(self.x<<10)) & 0xffffffff
        self.x = self.y
        self.y = ((self.y ^ (self.y>>10)) ^ (t ^ (t>>13))) & 0xffffffff
        self.counter = (self.counter + 362437) & 0xffffffff
        return (self.y + self.counter) & 0xffffffff



class Encryptor:
    def __init__(self, prng):
        self.prng = prng

    def encrypt(self, file):
        enc_data = bytearray()
        with open(file, "rb") as f:
            data = f.read()
            chunks = [data[i:i + 4] for i in range(0, len(data), 4)]
            for i, chunk in enumerate(chunks):
                key_int = self.prng.rand()
                key_bytes = key_int.to_bytes(4, 'little')  
                encrypted = bytearray(b ^ k for b, k in zip(chunk, key_bytes))
                enc_data += encrypted
        with open(file + ".enc", "wb") as f_enc:
            f_enc.write(enc_data)


TARGET_DIR = "./files/"
IGNORE_PATTERN = r".*\.enc$"


p = PRNG(os.urandom(4), os.urandom(4))
e = Encryptor(p)


for subdir, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        if not re.match(IGNORE_PATTERN, file):
            print(f"[+] Encrypted {file}")
            e.encrypt(TARGET_DIR + file)

