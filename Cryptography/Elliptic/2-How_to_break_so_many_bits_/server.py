#!/usr/bin/env python3
import socket
import threading
import random
from ecdsa.ecdsa import curve_192, generator_192
from Crypto.Util.number import long_to_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES

HOST = "0.0.0.0"
PORT = 10000


def to_16_bytes(val):
    raw = long_to_bytes(val)
    raw = raw[-16:]
    return raw.rjust(16, b"\x00")

class C:
    def __init__(self, p, a, G_tuple, n, priv=None):
        self.p = p
        self.a = a
        self.G = G_tuple  
        self.n = n        
        if priv is None:
            self.private_key = random.randrange(1, n)
        else:
            self.private_key = priv

    def mod_inv(self, x):
        return pow(x, self.p - 2, self.p)

    def ec_add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P

        x1, y1 = P
        x2, y2 = Q

        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None

        if P != Q:
            num = (y2 - y1) % self.p
            den = (x2 - x1) % self.p
            lam = (num * self.mod_inv(den)) % self.p
        else:
            num = (3 * x1 * x1 + self.a) % self.p
            den = (2 * y1) % self.p
            lam = (num * self.mod_inv(den)) % self.p

        x3 = (lam*lam - x1 - x2) % self.p
        y3 = (lam*(x1 - x3) - y1) % self.p
        return (x3, y3)

    def ec_multiply(self, P, k):
        result = None
        addend = P
        while k > 0:
            if k & 1:
                result = self.ec_add(result, addend)
            addend = self.ec_add(addend, addend)
            k >>= 1
        return result

    def encrypt_data(self, shared_point, plaintext):
        if shared_point is None:
            x, y = 0, 0
        else:
            x, y = shared_point

        key = to_16_bytes(x)
        iv = to_16_bytes(y)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(plaintext.encode(), 16))

    def decrypt_data(self, shared_point, ciphertext):
        if shared_point is None:
            x, y = 0, 0
        else:
            x, y = shared_point

        key = to_16_bytes(x)
        iv = to_16_bytes(y)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), 16)

    def verify_signature(self, document: bytes, signature: bytes) -> bool:
        import hashlib
        priv_bytes = long_to_bytes(self.private_key)
        check = hashlib.sha256(priv_bytes + document).digest()
        return (signature == check)


def handle_client(conn, addr):
    print(f"[+] New connection from {addr}")

    gen_obj = generator_192
    G_tuple = (gen_obj.x(), gen_obj.y())
    n = gen_obj.order()

    curve = curve_192
    p = curve.p()
    a = curve.a()

    server_obj = C(p, a, G_tuple, n)
    server_pub = server_obj.ec_multiply(G_tuple, server_obj.private_key)

    greeting = (
        "Welcome to the ECC server!\n"
        f"Server public key (x,y): {server_pub[0]} {server_pub[1]}\n"
    )
    conn.sendall(greeting.encode())

    client_pubkey = None

    try:
        while True:
            menu = (
                "\nMenu:\n"
                "1) Submit client pubkey\n"
                "2) Encrypt message\n"
                "3) Submit signed document\n"
                "(Ctrl+C or close connection to exit)\n"
                "Choice: "
            )
            conn.sendall(menu.encode())

            data = conn.recv(1024)
            if not data:
                break

            choice = data.decode().strip()

            if choice == "1":
                prompt = b"Send your client public key as two integers, space-separated: "
                conn.sendall(prompt)
                data = conn.recv(1024)
                if not data:
                    break
                try:
                    x_str, y_str = data.decode().split()
                    client_pubkey = (int(x_str), int(y_str))
                    conn.sendall(b"Client pubkey stored.\n")
                except:
                    conn.sendall(b"Error parsing input.\n")

            elif choice == "2":
                if client_pubkey is None:
                    conn.sendall(b"Error: you must submit client pubkey first.\n")
                    continue
                conn.sendall(b"Enter message to encrypt: ")
                msg_data = conn.recv(4096)
                if not msg_data:
                    break
                plaintext = msg_data.decode(errors="ignore").strip()

                shared_point = server_obj.ec_multiply(client_pubkey, server_obj.private_key)
                ciphertext = server_obj.encrypt_data(shared_point, plaintext)
                conn.sendall(b"Ciphertext (hex): " + ciphertext.hex().encode() + b"\n")

            elif choice == "3":
                conn.sendall(b"Send your data (must be >= 256 bytes): ")
                doc_data = conn.recv(4096)
                if len(doc_data) < 256:
                    conn.sendall(b"Error: document must be at least 256 bytes.\n")
                    continue

                conn.sendall(b"Send signature (in hex): ")
                sig_hex = conn.recv(4096).strip()
                try:
                    signature = bytes.fromhex(sig_hex.decode())
                except:
                    conn.sendall(b"Error parsing signature hex.\n")
                    continue

                if server_obj.verify_signature(doc_data, signature):
                    with open("sig_verified.txt", "rb") as f:
                        conn.sendall(b"Signature verified.\n")
                        conn.sendall(f.read())
                else:
                    conn.sendall(b"Invalid signature.\n")

            else:
                conn.sendall(b"Invalid choice.\n")

    except Exception as e:
        print(f"[!] Exception in connection {addr}: {e}")

    conn.close()
    print(f"[-] Connection closed: {addr}")


def main():
    print(f"[*] Listening on {HOST}:{PORT}")
    import sys
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


if __name__ == "__main__":
    main()

