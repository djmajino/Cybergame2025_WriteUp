import socket
import re
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

p1 = 221967046828044394711140236713523917903
a1 = 65658963385979676651840182697743045469
b1 = 84983839731806025530466837176590714802

p2 = 304976163582561072712882643919358657903
a2 = 178942576641362013096198577367493407586
b2 = 135070218427063732846149197221737213566

p3 = 260513061321772526368859868673058683903
a3 = 125788353697851741353605717637937028517
b3 = 206616519683095875870469145870134340888

print("[*] Hľadám gx také, aby y^2 = gx^3 + a*gx + b malo riešenie na všetkých 3 krivkách...")

found_gx = None
found_gy = None
search_limit = 1000 

R1 = GF(p1)
R2 = GF(p2)
R3 = GF(p3)

# Iterujme cez 0, 1, -1, 2, -2, ...
for i in range(search_limit + 1):
    gx_candidates = [i] if i == 0 else [i, -i]

    for gx in gx_candidates:
        #print(f"[*] Skúšam gx = {gx}...")

        try:
            rhs1 = R1(gx^3 + a1*gx + b1)
            rhs2 = R2(gx^3 + a2*gx + b2)
            rhs3 = R3(gx^3 + a3*gx + b3)

            if rhs1.is_square() and rhs2.is_square() and rhs3.is_square():
                print(f"[+] Nájdené vhodné gx = {gx}!")

                # Vypočítaj modulárne odmocniny
                y1_mod = rhs1.sqrt()
                y2_mod = rhs2.sqrt()
                y3_mod = rhs3.sqrt()

                # Konvertuj na celé čísla
                y1 = Integer(y1_mod)
                y2 = Integer(y2_mod)
                y3 = Integer(y3_mod)
                print(f"    sqrt(rhs1) mod p1 = {y1}")
                print(f"    sqrt(rhs2) mod p2 = {y2}")
                print(f"    sqrt(rhs3) mod p3 = {y3}")

                # Vyrieš systém pomocou CRT
                print(f"[*] Riešim systém pomocou CRT...")
                gy = crt([y1, y2, y3], [p1, p2, p3])

                found_gx = gx
                found_gy = gy
                break

        except Exception as e:
             print(f"    Chyba pri spracovaní gx = {gx}: {e}")
             continue

    if found_gx is not None:
        break 

if found_gx is not None:
    print(f"\n[+] Nájdené súradnice spoločného bodu:")
    print(f"    gx = {found_gx}")
    print(f"    gy = {found_gy}")

    print(f"\n[*] Overujem, či bod ({found_gx}, {found_gy}) leží na krivkách:")
    # Overenie pre E1
    on_E1 = mod(found_gy^2 - (found_gx^3 + a1*found_gx + b1), p1) == 0
    print(f"    Leží bod na E1? {on_E1}")
    # Overenie pre E2
    on_E2 = mod(found_gy^2 - (found_gx^3 + a2*found_gx + b2), p2) == 0
    print(f"    Leží bod na E2? {on_E2}")
    # Overenie pre E3
    on_E3 = mod(found_gy^2 - (found_gx^3 + a3*found_gx + b3), p3) == 0
    print(f"    Leží bod na E3? {on_E3}")

    if on_E1 and on_E2 and on_E3:
        print("[+] Overenie úspešné! Bod leží na všetkých troch krivkách.")
    else:
        print("[!] Chyba pri overení! Bod neleží na všetkých krivkách.")

else:
    print(f"\n[-] Nepodarilo sa nájsť vhodné gx v rozsahu +/- {search_limit}. Skúste zvýšiť limit.")


import socket

HOST = "exp.cybergame.sk"
PORT = 7006
SOCKET_TIMEOUT = 10

def recv_until(sock, suffix):
    sock.settimeout(SOCKET_TIMEOUT)
    message = ""
    try:
        while not message.endswith(suffix):
            chunk = sock.recv(4096).decode("utf-8", errors="ignore")
            if not chunk:
                raise ConnectionAbortedError(
                    f"Server zatvoril spojenie počas čakania na '{suffix}'"
                )
            message += chunk
    except socket.timeout:
        raise TimeoutError(
            f"Timeout pri čakaní na '{suffix}'. Prijaté doteraz: '{message[:100]}...'"
        )
    except OSError as e:
        raise ConnectionAbortedError(f"Chyba socketu pri čakaní na '{suffix}': {e}")
    finally:
        sock.settimeout(None)
    return message

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print("[*] Spojenie so serverom nadviazané.")
    print("[*] Posielam získané hodnoty na server.")

    recv_until(sock, "Send g.x:\n")
    sock.sendall((str(found_gx) + "\n").encode('utf-8'))

    recv_until(sock, "Send g.y:\n")
    sock.sendall((str(found_gy) + "\n").encode('utf-8'))

    full_output = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            full_output += chunk
        except socket.timeout:
            break
    # Oddelenie hlavičky (data) a ciphertextu
    header, ciphertext = full_output.split(b"Encrypted story:\n", 1)
    data = header.decode('utf-8')

pattern = r"Q1 = \((\d+), (\d+)\).*Q2 = \((\d+), (\d+)\).*Q3 = \((\d+), (\d+)\)"
matches = re.findall(pattern, data, re.DOTALL)[0]

print("[*] Získané Q")
print("    Q1: ", int(matches[0]), int(matches[1]))
print("    Q2: ", int(matches[2]), int(matches[3]))
print("    Q3: ", int(matches[4]), int(matches[5]))

print("[*] Získaná zašifrovaná správa")
print("    \"" + ciphertext[:50].hex() + "...\"")

print("[*] Derivujem privátný kľúč")
E1 = EllipticCurve(GF(p1), [a1, b1])
E2 = EllipticCurve(GF(p2), [a2, b2])
E3 = EllipticCurve(GF(p3), [a3, b3])

Q1 = E1(int(matches[0]), int(matches[1]))
Q2 = E2(int(matches[2]), int(matches[3]))
Q3 = E3(int(matches[4]), int(matches[5]))

G1 = E1(found_gx, found_gy % p1)
G2 = E2(found_gx, found_gy % p2)
G3 = E3(found_gx, found_gy % p3)

# Výpočet diskrétnych logaritmov
d1 = Q1.log(G1)
d2 = Q2.log(G2)
d3 = Q3.log(G3)

# CRT pre nájdenie d
d = crt([d1,d2,d3], [G1.order(),G2.order(),G3.order()])
print("[*] Privátny kľúč derivovaný")
print("    private key: : ", d)

# Dešifrovanie AES
key = hashlib.sha256(str(d).encode()).digest()
print("[*] Vyrobený dešifrovací kľúč")
print("    AES Key: ", key.hex())
iv = b'\x00' * 16
print("    AES  IV: ", iv.hex())
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
decryptor = cipher.decryptor()
padded = decryptor.update(ciphertext[:-1]) + decryptor.finalize()

unpadder = padding.PKCS7(128).unpadder()
plaintext = unpadder.update(padded) + unpadder.finalize()

print("\n\n*** Dešifrovaná správa:" + "*"*100 + "\n\n")
print(plaintext.decode('utf-8'))
