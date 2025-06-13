# Zadanie

EN:I am using a very good and secure messaging system, but I found logs that are not from my communications. Because it is so secure, I need your help to decrypt the messages so I can find out what was going on.

SK: Používam veľmi dobrý a bezpečný komunikačný systém, ale našiel som záznamy, ktoré nepochádzajú z mojej komunikácie. Keďže je to taký bezpečný systém, potrebujem tvoju pomoc na dešifrovanie správ, aby som zistil, čo sa dialo.

**Súbory:**

- server_data.zip
  - [cache]
    - cache_recv.jsonl
    - cache_send.jsonl
    - cache.json
  - main.py

*main.py*

```python
import socket
import json
import threading
import sys
import random
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

b = 0
p = 298211241770542957242152607176537420651
a = p - 1
G = (107989946880060598496111354154766727733, 36482365930938266418306259893267327070)

def modinv(a, p):
    if a == 0:
        raise ZeroDivisionError("Inverse does not exist")
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        ratio = high // low
        nm = hm - lm * ratio
        new = high - low * ratio
        lm, low, hm, high = nm, new, lm, low
    return lm % p

def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and y1 == y2:
        if y1 == 0:
            return None
        s = (3 * x1 * x1 + a) * modinv(2 * y1, p) % p
    else:
        if x1 == x2:
            return None
        s = (y2 - y1) * modinv(x2 - x1, p) % p

    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_scalar_mult(k, P, a, p):
    result = None
    addend = P

    while k:
        if k & 1:
            result = ec_add(result, addend, a, p)
        addend = ec_add(addend, addend, a, p)
        k >>= 1
    return result

def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8 or 1, 'big')

def aes_encrypt(plaintext: bytes, key: bytes) -> bytes:
    key = key[:32]
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return iv + ciphertext

def aes_decrypt(ciphered: bytes, key: bytes) -> bytes:
    key = key[:32]
    iv = ciphered[:16]
    ciphertext = ciphered[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext

def send_point(sock, point):
    if point is None:
        s = "None"
    else:
        s = f"{point[0]},{point[1]}"
    sock.sendall(s.encode())

def recv_point(sock):
    data = sock.recv(1024).decode().strip()
    if data == "None":
        return None
    x_str, y_str = data.split(",")
    return (int(x_str), int(y_str))

def send_messages(sock, key):
    try:
        while True:
            msg = input()
            if msg.lower() == "exit":
                break
            cipher = aes_encrypt(msg.encode(), key)
            with open("cache_send.jsonl", "a") as f:
                f.write(json.dumps({
                        "send": cipher.hex()
                    }))
                f.write("\n")
            sock.sendall(cipher)
    except Exception as e:
        print("Send error:", e)
    finally:
        sock.close()

def receive_messages(sock, key):
    try:
        while True:
            data = sock.recv(4096)  
            if not data:
                break
            with open("cache_recv.jsonl", "a") as f:
                f.write(json.dumps({
                        "recv": data.hex()
                    }))
                f.write("\n")
            plain = aes_decrypt(data, key)
            print("Peer:", plain.decode())
    except Exception as e:
        print("Receive error:", e)
    finally:
        sock.close()

def run_server():
    server_priv = random.randint(p // 2, p - 1)
    server_pub = ec_scalar_mult(server_priv, G, a, p)

    HOST = "0.0.0.0"
    PORT = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            send_point(conn, server_pub)
            client_pub = recv_point(conn)
            with open("cache.jsonl", "a") as f:
                f.write(json.dumps({
                        "server_pub": server_pub,
                        "client_pub": client_pub
                    }))
                f.write("\n")
            shared_point = ec_scalar_mult(server_priv, client_pub, a, p)
            if shared_point is None:
                return
            shared_key = int_to_bytes(shared_point[0])

            send_thread = threading.Thread(target=send_messages, args=(conn, shared_key))
            recv_thread = threading.Thread(target=receive_messages, args=(conn, shared_key))
            send_thread.start()
            recv_thread.start()
            send_thread.join()
            recv_thread.join()

def run_client():
    client_priv = random.randint(p//2, p - 1)
    client_pub = ec_scalar_mult(client_priv, G, a, p)

    HOST = "127.0.0.1"
    PORT = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        server_pub = recv_point(s)
        send_point(s, client_pub)

        shared_point = ec_scalar_mult(client_priv, server_pub, a, p)
        if shared_point is None:
            return
        shared_key = int_to_bytes(shared_point[0])

        send_thread = threading.Thread(target=send_messages, args=(s, shared_key))
        recv_thread = threading.Thread(target=receive_messages, args=(s, shared_key))
        send_thread.start()
        recv_thread.start()
        send_thread.join()
        recv_thread.join()

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("server", "client"):
        print("Usage: python ecc_network.py [server|client]")
        sys.exit(1)

    if sys.argv[1] == "server":
        run_server()
    else:
        run_client()
```

*cache_recv.jsonl*

```json
{"recv": "955e81123cceced7da5c9fe8c72633a4c971c5c96651f85b5d40f628a48c75f1"}
{"recv": "1f2e0cdfa573b9c4218991336596509c275e9c8b3df4cbae57d820bf6535b117"}
{"recv": "7c037f2d5ed214afefc4cf1c8a8773996d9fc5a8cf69c733e3f75a2b73c43861232d055fe4c76e850c859ebd1d59df14"}
{"recv": "dc32a919810ff9369548077c0c6e68c1dad12c5c10cbba0a4eb2603b60a4dd47da3603e3c7b8cd561386fcd5031bed6a"}
{"recv": "8217705cc9fbef141c613da12dd87885121d30ac9ebb656146fc1cd17f00d261"}
```

*cache_send.jsonl*

```json
{"send": "ad8b7366954de6f2ff7883f4e613b842e28a13d166561107a5a7be4a95e30e23"}
{"send": "713d50c67c44424b994079b93c6758704396f91da61cd88cbb183990f6436ecf"}
{"send": "dd787a50dba65e5768942a007a468665baea39dc89c3a10a316be663c4a70dd9"}
{"send": "3f7d6fa83f46d035418416bd5596ce5f757cc6f1487eb8fda53535c9d04a0b04"}
```

*cache.jsonl*

```json
{
 "server_pub": [72947667249607227642932393260968830921, 261432642373021661017738970173175343657], 
 "client_pub": [291216048318375702409990419027018106946, 219380392381458352976435257541531938506]
}
```

## **Riešenie**

Kód implementuje čistý ECDH bez podpisov, takže kto vie urobiť MITM alebo poslať neplatný bod, môže budúcu komunikáciu kompromitovať. Kľúčová slabina je však voľba supersingulárnej krivky E:y2=x3−x s poradím n=p+1. Toto poradie sa rozkladá na veľmi malé faktory (najväčší má len 239 bitov), takže diskrétny logaritmus vyrieši Pohlig-Hellman a Pollard-Rho za pár sekúnd. Tým pádom z dvoch verejných bodov okamžite získame oba privátne kľúče a celé AES šifrovanie padá. (Teoreticky existuje aj MOV útok, ale tu je zbytočný – klasický PH+Rho je už dostatočne rýchly)

Krivka $E:y^2=x^3−x \pmod{p}$ je supersingulárna, takže jej
skupina bodov má poradie n=p+1. To sa rozkladá na veľmi
malé faktory; najväčší má len 239 bitov. Taká skupina je pre ECDLP fatálne slabá – diskrétny logaritmus v nej vyrieši kombinácia *Pohlig–Hellman ➜ Pollard-Rho* v priebehu sekúnd. Na toto bude veľmi vhodné použiť prostredie sage

```python
p  = 298211241770542957242152607176537420651

Gx = 107989946880060598496111354154766727733
Gy = 36482365930938266418306259893267327070

Sx =  72947667249607227642932393260968830921
Sy = 261432642373021661017738970173175343657

Cx = 291216048318375702409990419027018106946
Cy = 219380392381458352976435257541531938506

# Definovanie krivky
F  = GF(p)
E  = EllipticCurve(F, [0,0,0,-1,0]) # y^2 = x^3 - x

G = E(Gx, Gy) # generator
S = E(Sx, Sy) # verejny kluc servera
C = E(Cx, Cy) # verejny kluc klienta

n = p + 1 # rád E(F_p)
#print(f"|E(F_p)| = {n.factor()}")

# Ziskanie privatnych klucov
try:
    k_S = S.discrete_log(G, ord=n)
    k_C = C.discrete_log(G, ord=n)
except TypeError:
    from sage.groups.generic import discrete_log
    k_S = discrete_log(S, G, ord=n, operation='+')
    k_C = discrete_log(C, G, ord=n, operation='+')

print(f"Privatny kluc SERVER: {k_S}")
print(f"Privatny kluc KLIENT: {k_C}")

```

Výstup

```
(sage) majino@majino:~$ sage ell1.sage
Privatny kluc SERVER: 37041828426322252952359931953705367198
Privatny kluc KLIENT: 68963980983032829437710796747317495343
```

Máme privátne kľúče, môžeme dešifrovať.

```python
import json
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

p = 298211241770542957242152607176537420651
a = p - 1 
G = (107989946880060598496111354154766727733,
     36482365930938266418306259893267327070)

# Zo Sagemath:
server_priv = 37041828426322252952359931953705367198
client_priv = 68963980983032829437710796747317495343

# server_pub a client_pub vieme z cache.jsonl alebo kódu, ale nepotrebujeme
# explicitne pri offline výpočte – máme priamo server_priv, client_priv.
# Pre úplnosť:
server_pub = (72947667249607227642932393260968830921,
              261432642373021661017738970173175343657)
client_pub = (291216048318375702409990419027018106946,
              219380392381458352976435257541531938506)

def modinv(a, p):
    if a == 0:
        raise ZeroDivisionError("Inverse does not exist")
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        ratio = high // low
        nm = hm - lm * ratio
        new = high - low * ratio
        lm, low, hm, high = nm, new, lm, low
    return lm % p

def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 == y2:
        if y1 == 0:
            return None
        s = (3 * x1 * x1 + a) * modinv(2 * y1, p) % p
    else:
        if x1 == x2:
            return None
        s = (y2 - y1) * modinv(x2 - x1, p) % p

    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_scalar_mult(k, P, a, p):
    result = None
    addend = P
    while k:
        if k & 1:
            result = ec_add(result, addend, a, p)
        addend = ec_add(addend, addend, a, p)
        k >>= 1
    return result

def int_to_bytes(x):
    # presne ako v original kóde
    return x.to_bytes((x.bit_length() + 7) // 8 or 1, 'big')

def aes_decrypt(ciphered: bytes, key: bytes) -> bytes:
    # presne ako v original kóde
    key = key[:32]
    iv = ciphered[:16]
    ciphertext = ciphered[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext

# 1) Vypočítame zdieľaný bod (toto môžeme urobiť buď server_priv * client_pub
#    alebo client_priv * server_pub – výsledok bude rovnaký)
shared_point = ec_scalar_mult(server_priv, client_pub, a, p)
print("shared_point =", shared_point)

# 2) Kľúč je x-ová súradnica (v bajtovom tvare) -> [:32]
shared_key = int_to_bytes(shared_point[0])
print("shared_key (hex) =", shared_key[:32].hex())

# Teraz môžeme decryptovať všetko, čo v logoch nájdeme.

def decrypt_file(filename, key):
    print(f"\nDešifrujem {filename}:")
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            # v cache_recv.jsonl je "recv": "<hex>"
            # v cache_send.jsonl je "send": "<hex>"
            # buď kľúč "recv" alebo "send"
            if "recv" in obj:
                data_hex = obj["recv"]
            elif "send" in obj:
                data_hex = obj["send"]
            else:
                # neznáma línia
                continue

            ciphered = binascii.unhexlify(data_hex)
            try:
                plain = aes_decrypt(ciphered, key)
                print("  Plaintext:", plain.decode("utf-8"))
            except Exception as e:
                print("  [chyba pri dešifrovaní]", e)

decrypt_file("Crypto3/cache/cache_recv.jsonl", shared_key)
decrypt_file("Crypto3/cache/cache_send.jsonl", shared_key)

```

Výstup

```
shared_point = (219428447293582886882359160395490402868, 14641516907269842583604395548202073672)
shared_key (hex) = a51461b90319a3da6a1a3da090e02234

Dešifrujem Crypto3/cache/cache_recv.jsonl:
  Plaintext: hi
  Plaintext: how are you?
  Plaintext: good, want secret?
  Plaintext: SK-CERT{n33d_70_k33p_m0v1n6}
  Plaintext: bye

Dešifrujem Crypto3/cache/cache_send.jsonl:
  Plaintext: hi
  Plaintext: good, u?
  Plaintext: y
  Plaintext: thx bye
```

## Vlajka

```
SK-CERT{n33d_70_k33p_m0v1n6}
```
