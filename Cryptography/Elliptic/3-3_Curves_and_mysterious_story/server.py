import socketserver
import random
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def modinv(a, p):
    return pow(a, p - 2, p)

class EllipticCurve:
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b

    def is_on_curve(self, x, y):
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def point(self, x, y):
        if not self.is_on_curve(x, y):
            raise ValueError("The point is not on the curve.")
        return ECPoint(x, y, self)

    def infinity(self):
        return ECPoint(None, None, self)

class ECPoint:
    def __init__(self, x, y, curve):
        self.x = x
        self.y = y
        self.curve = curve

    def is_infinity(self):
        return self.x is None and self.y is None

    def __neg__(self):
        if self.is_infinity():
            return self
        return ECPoint(self.x, (-self.y) % self.curve.p, self.curve)

    def __add__(self, other):
        if self.curve != other.curve:
            raise ValueError("Can't add points on different curves.")
        p = self.curve.p

        if self.is_infinity():
            return other
        if other.is_infinity():
            return self

        if self.x == other.x:
            if (self.y - other.y) % p == 0:
                if self.y == 0:
                    return self.curve.infinity()
                m = (3 * self.x * self.x + self.curve.a) * modinv(2 * self.y, p)
            else:
                return self.curve.infinity()
        else:
            m = (other.y - self.y) * modinv(other.x - self.x, p)

        m %= p
        x3 = (m * m - self.x - other.x) % p
        y3 = (m * (self.x - x3) - self.y) % p
        return ECPoint(x3, y3, self.curve)

    def __rmul__(self, n):
        result = self.curve.infinity()
        addend = self
        while n:
            if n & 1:
                result = result + addend
            addend = addend + addend
            n //= 2
        return result

    def __str__(self):
        if self.is_infinity():
            return "Infinity"
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.curve == other.curve

E1 = EllipticCurve(
    p=221967046828044394711140236713523917903,
    a=65658963385979676651840182697743045469,
    b=84983839731806025530466837176590714802
)

E2 = EllipticCurve(
    p=304976163582561072712882643919358657903,
    a=178942576641362013096198577367493407586,
    b=135070218427063732846149197221737213566
)

E3 = EllipticCurve(
    p=260513061321772526368859868673058683903,
    a=125788353697851741353605717637937028517,
    b=206616519683095875870469145870134340888
)

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            self.request.sendall(b"Welcome to ECC Oracle!\n")
            self.request.sendall(b"Send g.x:\n")
            gx = int(self.request.recv(4096).strip())

            self.request.sendall(b"Send g.y:\n")
            gy = int(self.request.recv(4096).strip())

            G1 = E1.point(gx, gy)
            G2 = E2.point(gx, gy)
            G3 = E3.point(gx, gy)

            # generate private key
            d = random.randint(
                221967046828044394694688089238337659792,
                440883567264567553887820221359293838912320528316331486261350931519268084925699580001476273968159118924129968558327
            )

            Q1 = d * G1
            Q2 = d * G2
            Q3 = d * G3

            self.request.sendall(b"\nQ1 = " + str(Q1).encode() + b"\n")
            self.request.sendall(b"Q2 = " + str(Q2).encode() + b"\n")
            self.request.sendall(b"Q3 = " + str(Q3).encode() + b"\n")

            with open("story.txt", "rb") as f:
                data = f.read()

            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()
            iv = 16 * b'\x00'
            key = hashlib.sha256(str(d).encode()).digest()

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

            self.request.sendall(b"\nEncrypted story:\n")
            self.request.sendall(encrypted_data + b"\n")
        except Exception as e:
            self.request.sendall(b"Error: " + str(e).encode() + b"\n")

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 11337
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as server:
        print(f"[+] Server listening on {HOST}:{PORT}")
        server.serve_forever()

