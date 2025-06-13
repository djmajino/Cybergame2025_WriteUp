# Zadanie

EN: We have gained access to a service that provides encryption and signature validation using an elliptic curve with a very large prime. The service is also guarding something very secret, and you must pass its signature test to get its secrets.

SK: Získali sme prístup k službe, ktorá poskytuje šifrovanie a overovanie podpisov pomocou eliptickej krivky s veľmi veľkým prvočíslom. Táto služba zároveň stráži niečo veľmi tajné a musíš prejsť jej testom podpisu, aby si získal jej tajomstvá.

`exp.cybergame.sk:7005`

**Súbory:**

- server.py

```python
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


```

## Riešenie

Server nám na začiatku prezradí jeho verejný kľúč a následne dá možnosti 

```
Welcome to the ECC server!
Server public key (x,y): 3708936759920297893113666595250669084848919096599913511011 4211346964075380057962393427601661226958324073436011127037

Menu:
1) Submit client pubkey
2) Encrypt message
3) Submit signed document
(Ctrl+C or close connection to exit)
Choice:
```

Môžeme zadať náš public key, ktorý si server uloží a keď použijeme možnosť 2 a zadáme ľubovoľnú správu, tak server pomocou aj nášho zadaného kľúča vypočíta šifrovací kľúč a ním zašifruje správu a hex výstup pošle na klienta. Ak vieme privátny kľúč servera, vieme si vypočítať podpis pre správu, ktorú od nás vypýta (min 256 bajtov) a keď zadáme spravny podpis, tak nám server pošle vlajku...

Zo zadaného skriptu je však jasné, že tam chýba overenie, či bod, ktorý mu zadám aj reálne leží na krivke, ktorú ma server definovanú. Chýba tam niečo takéto

```python
def is_on_curve(self, P):
    if P is None:
        return True  # bod v nekonečne sa považuje za platný
    x, y = P
    return (y * y) % self.p == (x * x * x + self.a * x + curve_192.b()) % self.p

```

A to znamená, že serveru môžeme podsunúť súradnice akejkoľvej krivky a server aj tak robí ec_multiply aj keď ten bod nemá rád n. Kde je problém? Server vynásobí mnou podvrhnutý bod so svojím private key a výsledok je hodnota priv_key modulo rád. Čo to znamená? Ak pošlem pošlem bod rádu 2, výsledok bude len 0 alebo 1, to sú možné zvyšky po delení dvomi. Ak je kľúč párny, zvyšok je nula, shared point bude None, AES kľúč aj IV bude tým pádom null bajtový a viem dopredu aký bude výsledok po zašifrovaní mojej správy. Ak výseldok bude neznámy ciphertext, viem, že kľúč je nepárny.. Týmto zistím len paritu kľúča. Ako ale zistým zvyšky po delení ďalšími prvočíslami? A prečo potrebujem prvočísla a koľko ich potrebujem? Keďže ide o 192 bitový kľúč, pre využitie CRT (Chinese remainder theorem) v sage na výpočet takého veľkého kľúča potrebujem zvyšky po delení prvočíslami od 2 do 151. Ako ale získam zvyšky po delení väčšími prvočíslami? No pri bode každého rádu výjde šifrovací kľúč podľa zvyšku po delení tým prvočíslom, ktorého rádu je bod na krivke, čo som poslal a tým pádom mám aj obmedzenú množninu ciphertextov. Takže keď si zostrojím skript, ktorý mi pošle na server bod rádu napri 7, dostanem od servera nejakú odpoveď na cipher text správy "hello", ale tých výsledných ciphertextov bude pre daný mnou zadaný bod a pre daný rád vždy len 7 a to aký bude záleží len od toho čo je privátny kľúč servera delitelný 7 alebo podľa toho aký je zvyšok po delení 7. Najprv ale potrebujem nájsť aspoň po jednom bode rádov 2 - 151.  To vieme pomocou správneho sage skriptu a použitím malých hodnot pre `b`.

```python
from datetime import datetime
import json

p = 6277101735386680763835789423207666416083908700390324961279
Fp = GF(p)
a = -3
target_orders = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151]
max_b_search = 1000
output_filename = "bodymalychradov.json"

results = {}

for r in target_orders:
    found = False
    print(f"\n[{datetime.now()}] Hľadám bod rádu {r}...")
    for b in range(max_b_search):
        try:
            E = EllipticCurve(Fp, [a, b])
            if E.is_singular():
                continue

            if E.count_points() % r != 0:
                continue

            for attempt in range(20):
                P = E.random_point()
                Q = (E.order() // r) * P
                if Q != E(0) and (r * Q) == E(0):
                    x, y = Q.xy()
                    print(f"Order {r}: nájdený bod pre b={b}")
                    print(f"Point {int(x)} {int(y)}\n")
                    results[str(r)] = f"{int(x)} {int(y)}"
                    found = True
                    break

            if found:
                break

        except Exception as e:
            continue

    if not found:
        print(f"Nenájdený bod rádu {r} pre b do {max_b_search}")
        results[str(r)] = "Not found"

with open(output_filename, 'w') as jsonfile:
    json.dump(results, jsonfile, indent=2)

print("\nFinito!")

```

Tento skript mi do súboru bodymalychradov.json uloží všetky body rádov 2-151.

```json
{
  "2": "2849578927046012305985497223353059849159585052738548569918 0",
  "3": "1094210748148774040406682605236104878775999313120518109195 1906387580838892495682034466391218832589648744398662771751",
  "5": "828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201",
  "7": "451328293764371047228783128451231145725339827934237834597 4150173776698169972227466101603159996416571760967579451210",
  "11": "5448433494744827098583553640513409437786014893066134261589 4276574704753598815325567001671877550764694701388855294346",
  "13": "4644972655678029260717137018699262693286411721618201863106 2202517178366017551273947789829821527068675646811323009593",
  "17": "560021892084998975194193639075260529661929995099286294628 4271521640559419268184203911700607200881799221631179290437",
  "19": "4258027628585429970953779307403050399700253423346207643866 2053790158472934365071434836122825389106406168448976352756",
  "23": "1161557426736772148744220437125935973026464406418206579500 2942261131569755684548729371254820655792796316235179013435",
  "29": "1102773535547896349706645530831452667270753646280310419544 218270850915338487487645521865798533705377502422315436053",
  "31": "4598503991413126987860867284914198555936832506333597736881 1781896006047563446060625845027964285893796797337986663246",
  "37": "5628673717942500867285965165111276418287745885433521103636 4058581466474081268560214156408828963395968523970495280854",
  "41": "3070033404161510007540975664345419093955303487932065573709 4391317980527997269624696755751498551709420624697909847046",
  "43": "5569754467578378131981418228833429598103935536906828520346 6119058643818389502559510161699129099265409681094160331054",
  "47": "4237560991826804787732185080084268740450748519179136449215 4395204072674992898184448838630727559373154377243305068612",
  "53": "2616034258870028022819215050992963207242372935692265427168 2530304504429101914062793393361334916449046045990128671018",
  "59": "3704109876584276152441189935733861651432604153804123592365 4656500067304005814195589718981943932137364205401402069432",
  "61": "5689787329966037988302362696155792746665302546175218688636 1329084801550075454316722278898711933894693104532165708205",
  "67": "4776339692690246365645156201867996738365810172905840537139 5308234546219698393020260020385943958478440292504545453042",
  "71": "5841544013397267822938234401923672333676064620073326888640 4236120018413384610058610073974682548383525770699674035961",
  "73": "3677056982333523330705675187028496680140986162536561034599 5823291158763749693254216877634307632309150355244579074845",
  "79": "2613272500594298539507890817950827306569987695195879378204 1585852019729988151297727565743976215719720599516904098611",
  "83": "268871687395680748714591893371334766177405324411908635959 482457188222463181721240000030671910611242743251447345356",
  "89": "3210428526144567101928666111992814773131942820865944332673 4772382840801575993369739388347750598874654638886494553307",
  "97": "1743409825549438094006036211382887254489299873868369013719 977504862830156904712528558473940901182067187483424011045",
  "101": "6226734405553988361382371523240374267458259894729394419928 4382109723556893008227217179090166168676451342989821768628",
  "103": "716166430890444360574499163191460168356635636352166329244 530285313070764813748391764108413074328433088254304658737",
  "107": "4292302513768751358626901636138319054666508630129645339143 1278608508236973634567845946561132954967509760508035671142",
  "109": "1593999202885511397549080213743525465493111683874433663192 2676743842751646493529751265565027204322975506901177929453",
  "113": "3385577856087676697811653802908838876498748401788854047014 362519745023078747466278635756522633484183065125827904654",
  "127": "4398287998430878940689706212413768466016665826109240572269 900581763148254285321041693980497767393804055089638613699",
  "131": "3301865213437808552940108181443958994860944313522805553404 1111395993953235067138446513969728481622314064060412210050",
  "137": "5917136120430270270685225813678819170250460939342925763943 4273625549552769897659104333234695952638919749543252812131",
  "139": "5405872235271176040008118563464605249185921753087706450808 2905365057371476456214283522320676651735837800881915504566",
  "149": "3478263632935817528157055314568001831998469265141961709316 1443429172417083084869967598206950637606774480589771385319",
  "151": "2972548050031429506489823816854627450306963717254315944008 5123200163356697659610015119078345948269066957947998929233"
}
```

Pre ilustráciu uvediem bod rádu 5 a privat key na server bude kľuč s hodnotou 1000-1009

```
Order 5: nájdený bod pre b=0
Point 
x: 828196689094034699821974449097524608102877170264026280498
y: 2416848060600067542064423216543795628488400426414426552201
```

```
Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1000
Enter message to encrypt: hello
Ciphertext (hex): 9834ed518cbc8fbe9af3c6ecb75eb8c0

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1001
Enter message to encrypt: hello
Ciphertext (hex): 3134536552effba35943dfbcb7a0cdcb

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1002
Enter message to encrypt: hello
Ciphertext (hex): 51aaed198141f68801f02cab5917aa03

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1003
Enter message to encrypt: hello
Ciphertext (hex): 39dae10c5cb090cee67a604a9ab11d34

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1004
Enter message to encrypt: hello
Ciphertext (hex): 79bb0edc1fe5a04af4e1f48719387b65

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1005
Enter message to encrypt: hello
Ciphertext (hex): 9834ed518cbc8fbe9af3c6ecb75eb8c0

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1006
Enter message to encrypt: hello
Ciphertext (hex): 3134536552effba35943dfbcb7a0cdcb

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1007
Enter message to encrypt: hello
Ciphertext (hex): 51aaed198141f68801f02cab5917aa03

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1008
Enter message to encrypt: hello
Ciphertext (hex): 39dae10c5cb090cee67a604a9ab11d34

Send your client public key as two integers, space-separated: 828196689094034699821974449097524608102877170264026280498 2416848060600067542064423216543795628488400426414426552201
Kluc 1009
Enter message to encrypt: hello
Ciphertext (hex): 79bb0edc1fe5a04af4e1f48719387b65
```

A tu je jasné. že podľa zvyšku po delení sa vytvorí AES kľúč.. A podľa výsledného ciphertextu viem zistiť zvyšok po delení číslom rádu daného bodu.. Počas overovania výstupov servera si viem nasimulovať všeky ciphertexty a porovnať, ktorý výjde a podľa toho zistím modulo. Po získaní všetkých zvyškov po delení a ďalším sage scriptom viem vyderivovať server privat key, ktorým vytvorím aj podpis...

```python
import socket
import sys
import json
import time
from datetime import datetime
import hashlib 
from sage.all import ZZ
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import long_to_bytes

HOST = "exp.cybergame.sk"
PORT = 7005
INPUT_FILE = "bodymalychradov.json"
OUTPUT_FILE = "all_modulos.json"
NULL_KEY_CIPHERTEXT = "9834ed518cbc8fbe9af3c6ecb75eb8c0"
TARGET_MESSAGE = "hello"
TARGET_DOCUMENT = b"A"*256
SOCKET_TIMEOUT = 10
DELAY_BETWEEN_TESTS = float(0.1)

# Parametre krivky a kľúč
p_val = 6277101735386680763835789423207666416083908700390324961279
a_val = -3

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

def to_16_bytes(val):
    try:
        val_int = int(val)
    except (TypeError, ValueError) as e:
        print(f"[!] Chyba: Nepodarilo sa konvertovať hodnotu {val} (typ: {type(val)}) na integer v to_16_bytes: {e}")
        return b"\x00" * 16
    if val_int == 0:
        return b"\x00" * 16
    try:
        byte_len = (val_int.bit_length() + 7) // 8
        raw = val_int.to_bytes(byte_len, "big", signed=False)
    except Exception as e: 
        print(f"[!] Chyba pri konverzii {val_int} na bajty: {e}")
        return b"\x00" * 16

    if len(raw) > 16:
        raw = raw[-16:]
    return raw.rjust(16, b"\x00")

def create_signature(msg: bytes, key) -> str: 
    try:
         key_int = int(key)
    except (TypeError, ValueError) as e:
         print(f"[!] Chyba: Nepodarilo sa konvertovať kľúč {key} (typ: {type(key)}) na integer pre podpis: {e}")
         raise ValueError("Neplatný typ kľúča pre podpis") from e
    
    try:
        priv_bytes = long_to_bytes(key_int)
    except Exception as e:
        print(f"[!] Chyba pri konverzii kľúča {key_int} na bajty: {e}")
        raise ValueError("Nepodarilo sa konvertovať kľúč na bajty pre podpis") from e
    
    if not isinstance(msg, bytes):
         print(f"[!] Chyba: Správa pre podpis nie je typu bytes (typ: {type(msg)}).")
         raise TypeError("Správa pre podpis musí byť typu bytes")

    signature = hashlib.sha256(priv_bytes + msg).digest()
    print(f"[*] Vytvorený podpis (SHA256(key_bytes + msg)): {signature.hex()}")
    return signature.hex()

class C:
    def __init__(
        self, p, a, G_tuple=None, n=None, priv=None
    ):
        self.p = p
        self.a = a
        self.G = G_tuple
        self.n = n
        # self.private_key = ...

    def mod_inv(self, x):
        p_sage = ZZ(self.p)
        x_sage = ZZ(x) % p_sage
        if x_sage == 0:
            raise ZeroDivisionError(f"Mod inverzia 0 mod {p_sage}")
        return pow(x_sage, p_sage - 2, p_sage)

    def ec_add(self, P, Q):
        if P is None: return Q
        if Q is None: return P

        try:
             p_sage = ZZ(self.p)
             a_sage = ZZ(self.a)
             x1 = ZZ(P[0])
             y1 = ZZ(P[1])
             x2 = ZZ(Q[0])
             y2 = ZZ(Q[1])
        except (TypeError, ValueError) as e:
             print(f"[!] Chyba pri konverzii súradníc P={P}, Q={Q} na Sage Integer: {e}")
             return None 

        xp1 = x1 % p_sage
        yp1 = y1 % p_sage
        xp2 = x2 % p_sage
        yp2 = y2 % p_sage

        if xp1 == xp2 and (yp1 + yp2) % p_sage == 0:
            return None # Bod v nekonečne

        if P == Q: # Zdvojenie
            if yp1 == 0: return None
            num = (3 * pow(xp1, 2, p_sage) + a_sage) % p_sage
            den = (2 * yp1) % p_sage
        else: # Sčítanie
            if xp1 == xp2: return None # Vertikálna línia (už overené P != -Q)
            num = (yp2 - yp1) % p_sage
            den = (xp2 - xp1) % p_sage

        try:
            lam = (num * self.mod_inv(den)) % p_sage
        except ZeroDivisionError:
             return None

        x3 = (pow(lam, 2, p_sage) - xp1 - xp2) % p_sage
        y3 = (lam * (xp1 - x3) - yp1) % p_sage

        try:
            x3_int = int(x3)
            y3_int = int(y3)
            return (x3_int, y3_int)
        except (TypeError, ValueError) as e:
            print(f"[!] Chyba pri konverzii výsledku ec_add ({x3}, {y3}) na Python int: {e}")
            return None

    def ec_multiply(self, P, k):
        try:
             k_sage = ZZ(k) 
             if P is None or P[0] is None or P[1] is None:
                  print("[!] Varovanie: ec_multiply dostal neplatný bod P.")
                  return None
             P_sage = (ZZ(P[0]), ZZ(P[1]))
             p_sage = ZZ(self.p) 
        except (TypeError, ValueError) as e:
             print(f"[!] Chyba pri konverzii vstupov v ec_multiply P={P}, k={k}: {e}")
             return None

        if k_sage == 0:
            return None 

        result = None
        addend = P_sage

        if k_sage < 0:
            k_sage = -k_sage
            addend = (addend[0], -addend[1] % p_sage)

        k_temp = k_sage
        while k_temp > 0:
            if k_temp % 2 == 1:
                result = self.ec_add(result, addend)
                if result is None and addend is not None :
                     pass
            addend = self.ec_add(addend, addend)
            if addend is None:
                 pass

            k_temp //= 2

        if result is None:
             return None
        else:
             try:
                  res_x_int = int(result[0])
                  res_y_int = int(result[1])
                  return (res_x_int, res_y_int)
             except (TypeError, ValueError) as e:
                  print(f"[!] Chyba pri konverzii výsledku ec_multiply ({result[0]}, {result[1]}) na Python int: {e}")
                  return None


    def encrypt_data(self, shared_point, plaintext_str):
        if shared_point is None:
            x, y = 0, 0
            print("[!] Varovanie: encrypt_data dostal shared_point=None, použije sa nulový kľúč/iv.")
        else:
            x, y = shared_point

        key = to_16_bytes(x)
        iv = to_16_bytes(y)

        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_message = pad(plaintext_str.encode("utf-8"), AES.block_size)
            return cipher.encrypt(padded_message)
        except Exception as e:
            print(f"[!] Chyba pri AES šifrovaní: {e}")
            return None


print("[*] Inicializácia ECC simulátora pomocou triedy C...")
try:
    ecc_simulator = C(p=p_val, a=a_val)
    print("[*] ECC simulátor pripravený.")
except Exception as e:
    print(f"[!] Fatálna chyba pri inicializácii ECC simulátora: {e}")
    sys.exit(1)

print(f"[*] Načítavam body zo súboru: {INPUT_FILE}")
points_to_test = []
try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        for order_str, coords_str in json_data.items():
            try:
                order = int(order_str)
                parts = coords_str.split()
                if len(parts) != 2:
                    raise ValueError("Očakávané dve súradnice")
                x = int(parts[0])
                y = int(parts[1])
                points_to_test.append({"order": order, "x": x, "y": y})
            except (ValueError, TypeError) as parse_err:
                print(
                    f"   Chyba pri parsovaní záznamu pre rád '{order_str}': {parse_err} - data: {coords_str}"
                )
except FileNotFoundError:
    print(f"[!] Chyba: Súbor {INPUT_FILE} nebol nájdený.")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"[!] Chyba: Neplatný formát JSON v súbore {INPUT_FILE}: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[!] Chyba pri čítaní súboru {INPUT_FILE}: {e}")
    sys.exit(1)

if not points_to_test:
    print("[!] Chyba: Zo súboru neboli načítané žiadne body na testovanie.")
    sys.exit(1)

print(f"[*] Načítaných {len(points_to_test)} bodov na testovanie.")
points_to_test.sort(key=lambda item: item["order"]) 
print("-" * 40)

results = {}
reconstructed_key_k_S = None

try:
    print(f"[*] Pripájam sa na {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print("[*] Spojenie so serverom nadviazané.")
        try:
            _ = recv_until(sock, "Choice: ")
        except Exception as e_recv:
            print(f"[!] Chyba pri čítaní úvodnej správy: {e_recv}")
            sys.exit(1)
            
        for point_data in points_to_test:
            order = point_data["order"]
            x = point_data["x"]
            y = point_data["y"]
            P_C_tuple = (x, y)

            order_str = str(order)
            if order_str in results:
                continue

            print(f"\n[*] Testujem Order {order} s bodom ({str(x)[:10]}..., {str(y)[:10]}...)")

            try:
                # 1. Submit key
                sock.sendall(b"1\n")
                _ = recv_until(sock, ": ")
                coords_str_send = f"{x} {y}\n"
                sock.sendall(coords_str_send.encode('utf-8'))
                stored_menu = recv_until(sock, "Choice: ")
                if "Client pubkey stored." not in stored_menu:
                    print("   Chyba: Server nepotvrdil uloženie kľúča.")
                    results[order_str] = "ERROR - Key not stored"
                    continue

                # 2. Encrypt
                sock.sendall(b"2\n")
                _ = recv_until(sock, ": ")
                sock.sendall(TARGET_MESSAGE.encode('utf-8') + b"\n")

                # 3. Receive response
                response_block = recv_until(sock, "Choice: ")

                # 4. Extract ciphertext
                hex_ciphertext = None
                prefix = "Ciphertext (hex): "
                for line in response_block.splitlines():
                    if line.startswith(prefix):
                        hex_ciphertext = line[len(prefix):].strip()
                        break

                if hex_ciphertext is None:
                    print(f"   Chyba: Ciphertext nenájdený v odpovedi servera:\n{response_block[:200]}...")
                    results[order_str] = "ERROR - Ciphertext not found"
                    continue

                print(f"   Server vrátil ciphertext: {hex_ciphertext[:20]}...")

                # 5. Evaluate
                is_null_key = hex_ciphertext == NULL_KEY_CIPHERTEXT

                if is_null_key:
                    print(f"   -> k_S mod {order} = 0 (nulový kľúč)")
                    results[order_str] = 0
                else:
                    print(f"   -> k_S mod {order} != 0. Hľadám presný zvyšok lokálnou simuláciou...")
                    found_remainder = -1
                    try:
                        for k_prime in range(1, order):
                            P_k = ecc_simulator.ec_multiply(P_C_tuple, k_prime)
                            if P_k is None:
                                continue

                            # --- Simulácia šifrovania ---
                            expected_ciphertext_k_bytes = ecc_simulator.encrypt_data(P_k, TARGET_MESSAGE)

                            if expected_ciphertext_k_bytes is None:
                                continue

                            expected_ciphertext_k_hex = expected_ciphertext_k_bytes.hex()

                            # --- Porovnanie ---
                            if hex_ciphertext == expected_ciphertext_k_hex:
                                print(f"   -> Zhoda nájdená! k_S mod {order} = {k_prime}")
                                results[order_str] = k_prime
                                found_remainder = k_prime
                                break # Našli sme zvyšok pre tento rád

                        if found_remainder == -1:
                            print(f"   [!] Chyba: Nenájdená zhoda pre nenulový ciphertext rádu {order}! Skontroluj NULL_KEY_CIPHERTEXT alebo logiku.")
                            results[order_str] = "ERROR - No match found"

                    except Exception as e_sim:
                        print(f"   [!] Chyba počas lokálnej simulácie pre rád {order}: {type(e_sim).__name__} - {e_sim}")
                        results[order_str] = f"ERROR - Simulation failed ({type(e_sim).__name__})"


            except (ConnectionRefusedError, ConnectionAbortedError, TimeoutError, OSError) as e:
                print(f"   Chyba spojenia pri testovaní rádu {order}: {e}")
                results[order_str] = f"ERROR - Connection failed ({type(e).__name__})"
                print("[!] Spojenie stratené, ukončujem testovanie.")
                break
            except Exception as e:
                print(f"   Neočakávaná chyba pri testovaní rádu {order}: {type(e).__name__} - {e}")
                results[order_str] = f"ERROR - Unexpected ({type(e).__name__})"

            time.sleep(DELAY_BETWEEN_TESTS)

        print("\n[*] Testovanie dokončené.")

        valid_results = {k: v for k, v in results.items() if isinstance(v, int)}
        if not valid_results:
             print("[!] Neboli získané žiadne platné zvyšky pre CRT.")
        else:
             print("\n[*] Rekonštrukcia privátneho kľúča pomocou CRT...")
             try:
                 # --- SageMath importy pre CRT ---
                 from sage.all import CRT, Integer, prod, ZZ, ceil, log, pari

                 remainders = []
                 moduli = []
                 print("[*] Pripravujem dáta pre Čínsku zvyškovú vetu (CRT)...")

                 for r_str in sorted(valid_results.keys(), key=int):
                     r = int(r_str)
                     v = valid_results[r_str]
                     print(f"   k_S \u2261 {v} (mod {r})") # \u2261 je ≡
                     remainders.append(v)
                     moduli.append(r)

                 remainders_sage = [ZZ(rem) for rem in remainders]
                 moduli_sage = [ZZ(mod) for mod in moduli]

                 reconstructed_key_k_S = CRT(remainders_sage, moduli_sage)

                 print("\n" + "="*50)
                 print(" VÝSLEDOK - Rekonštruovaný privátny kľúč:")
                 print("="*50)
                 print(f"\n   k_S (dekadicky) = {reconstructed_key_k_S}")
                 print(f"\n   k_S (hex)       = 0x{reconstructed_key_k_S:x}")
                 print(f"\n   Počet bitov kľúča: {reconstructed_key_k_S.nbits()}")

                 # --- Overenie ---
                 print("\n[*] Overujem výsledok...")
                 # Rád grupy bodov eliptickej krivky secp192r1 (NIST P-192)
                 n_secp192r1 = Integer(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFF)

                 R_product = prod(moduli_sage)
                 print(f"     (Súčin modulov R = {R_product.nbits()} bitov)")
                 print(f"     (Rád krivky n    = {n_secp192r1.nbits()} bitov)")

                 valid_key = True
                 if not (0 < reconstructed_key_k_S < n_secp192r1):
                     print(f"[!!!] Varovanie: Vypočítaný kľúč k_S je mimo očakávaného rozsahu (1 až n-1).")
                     valid_key = False

                 print("     Overujem vstupné kongruencie:")
                 all_congruences_met = True
                 for i in range(len(moduli)):
                     r = moduli_sage[i]
                     v = remainders_sage[i]
                     if reconstructed_key_k_S % r != v:
                         print(f"     [!!!] CHYBA: k_S mod {r} = {reconstructed_key_k_S % r}, ale očakávalo sa {v}")
                         all_congruences_met = False

                 if all_congruences_met:
                     print("     Všetky vstupné kongruencie sú splnené.")
                 else:
                     print("     [!!!] Niektoré vstupné kongruencie NIE SÚ splnené vypočítaným k_S!")
                     valid_key = False

                 if valid_key and all_congruences_met:
                     print("\n[✓] Privátny kľúč bol úspešne zrekonštruovaný (modulo R) a spĺňa vstupné kongruencie!")
                     if R_product < n_secp192r1:
                          print("   [!] Varovanie: Súčin modulov R je menší ako rád krivky n.")
                          print("       Výsledok k_S je správny modulo R, ale nemusí byť unikátny modulo n.")
                     elif not (0 < reconstructed_key_k_S < n_secp192r1):
                          print("   [!] Poznámka: Kľúč je však mimo štandardného rozsahu [1, n-1] pre secp192r1.")
                     else:
                          print("   Kľúč je aj v správnom rozsahu [1, n-1].")

                 else:
                     print("\n[!] Rekonštrukcia kľúča zlyhala, alebo vstupné dáta boli nekonzistentné, alebo kľúč nespĺňa podmienky.")
                     reconstructed_key_k_S = None


             except NameError as e:
                 print(f"\n[!] Chyba pri CRT výpočte: {e}. Uistite sa, že skript beží v SageMath.")
                 reconstructed_key_k_S = None
             except Exception as e:
                 print(f"\n[!] Nastala chyba pri výpočte CRT alebo pri overovaní: {e}")
                 reconstructed_key_k_S = None


        # --- Podpísanie dokumentu (ak bol kľúč úspešne rekonštruovaný) ---
        if reconstructed_key_k_S is not None:
            print("\n[*] Pokus o podpísanie dokumentu pomocou rekonštruovaného kľúča...")
            try:
                # 3. Sign
                sock.sendall(b"3\n")
                _ = recv_until(sock, ": ") # Prompt pre dokument
                # Dokument na odoslanie a podpísanie (vrátane \n)
                document_to_send = TARGET_DOCUMENT + b"\n"
                sock.sendall(document_to_send)
                _ = recv_until(sock, ": ") # Prompt pre podpis

                # Vytvorenie podpisu pre presne odoslané dáta
                signature_hex = create_signature(document_to_send, reconstructed_key_k_S)

                # Odoslanie podpisu (hex reťazec kódovaný ako latin-1/ascii)
                sock.sendall(signature_hex.encode('latin-1') + b"\n")

                # Prijatie finálnej odpovede
                response_block = recv_until(sock, "Choice: ")
                print("[*] Odpoveď servera po odoslaní podpisu:")
                print(response_block)

            except (ConnectionRefusedError, ConnectionAbortedError, TimeoutError, OSError) as e:
                print(f"[!] Chyba spojenia počas podpisovania: {e}")
            except Exception as e:
                print(f"[!] Neočakávaná chyba počas podpisovania: {type(e).__name__} - {e}")
        else:
             print("\n[!] Privátny kľúč nebol úspešne rekonštruovaný, podpisovanie sa preskakuje.")


except (ConnectionRefusedError, ConnectionAbortedError, TimeoutError, OSError) as e:
     print(f"[!] Kritická chyba spojenia hneď na začiatku alebo počas testovania: {e}")
except Exception as e:
    print(f"[!] Fatálna chyba pri práci so socketom alebo hlavnej slučke: {type(e).__name__} - {e}")
    import traceback
    traceback.print_exc()
finally:
    if "sock" in locals() and isinstance(sock, socket.socket):
         try:
              if sock.fileno() != -1:
                   print("[*] Zatváram spojenie so serverom.")
                   sock.close()
         except Exception as e_close:
              print(f"[!] Chyba pri zatváraní socketu: {e_close}")

print("\n[*] Skript dokončený.")


```

Výsledok

```
(sage) majino@majino:~$ sage elliptic2final.sage
[*] Inicializácia ECC simulátora pomocou triedy C...
[*] ECC simulátor pripravený.
[*] Načítavam body zo súboru: bodymalychradov.json
[*] Načítaných 36 bodov na testovanie.
----------------------------------------
[*] Pripájam sa na exp.cybergame.sk:7005...
[*] Spojenie so serverom nadviazané.

[*] Testujem Order 2 s bodom (2849578927..., 0...)
   Server vrátil ciphertext: 9d8063f930bc6dd5e786...
   -> k_S mod 2 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 2 = 1

[*] Testujem Order 3 s bodom (1094210748..., 1906387580...)
   Server vrátil ciphertext: cc6ce11a540dedd8e58f...
   -> k_S mod 3 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 3 = 1

[*] Testujem Order 5 s bodom (8281966890..., 2416848060...)
   Server vrátil ciphertext: 51aaed198141f68801f0...
   -> k_S mod 5 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 5 = 2

[*] Testujem Order 7 s bodom (4513282937..., 4150173776...)
   Server vrátil ciphertext: 91d7d852abff8a4564d5...
   -> k_S mod 7 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 7 = 6

[*] Testujem Order 11 s bodom (5448433494..., 4276574704...)
   Server vrátil ciphertext: ca2b0e786686273b1ac8...
   -> k_S mod 11 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 11 = 4

[*] Testujem Order 13 s bodom (4644972655..., 2202517178...)
   Server vrátil ciphertext: 29d37e672f4dd8b79668...
   -> k_S mod 13 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 13 = 5

[*] Testujem Order 17 s bodom (5600218920..., 4271521640...)
   Server vrátil ciphertext: 2d7347bffaa6d716ff24...
   -> k_S mod 17 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 17 = 4

[*] Testujem Order 19 s bodom (4258027628..., 2053790158...)
   Server vrátil ciphertext: 03b7cdc9713c48235c8b...
   -> k_S mod 19 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 19 = 6

[*] Testujem Order 23 s bodom (1161557426..., 2942261131...)
   Server vrátil ciphertext: d4165ad5feed5f33bb32...
   -> k_S mod 23 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 23 = 19

[*] Testujem Order 29 s bodom (1102773535..., 2182708509...)
   Server vrátil ciphertext: 3b42069336783773a7b4...
   -> k_S mod 29 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 29 = 13

[*] Testujem Order 31 s bodom (4598503991..., 1781896006...)
   Server vrátil ciphertext: 51ca4eba3ca79aace732...
   -> k_S mod 31 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 31 = 3

[*] Testujem Order 37 s bodom (5628673717..., 4058581466...)
   Server vrátil ciphertext: 59f8979b4f5a79a3c606...
   -> k_S mod 37 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 37 = 2

[*] Testujem Order 41 s bodom (3070033404..., 4391317980...)
   Server vrátil ciphertext: b970f981c28ffba115e0...
   -> k_S mod 41 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 41 = 6

[*] Testujem Order 43 s bodom (5569754467..., 6119058643...)
   Server vrátil ciphertext: 9370079b57a11af56ac7...
   -> k_S mod 43 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 43 = 32

[*] Testujem Order 47 s bodom (4237560991..., 4395204072...)
   Server vrátil ciphertext: 4b069cf3e93087085255...
   -> k_S mod 47 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 47 = 43

[*] Testujem Order 53 s bodom (2616034258..., 2530304504...)
   Server vrátil ciphertext: b905a6c1ecb7c53ef9ac...
   -> k_S mod 53 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 53 = 32

[*] Testujem Order 59 s bodom (3704109876..., 4656500067...)
   Server vrátil ciphertext: 8c8946d71950d6c7adeb...
   -> k_S mod 59 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 59 = 47

[*] Testujem Order 61 s bodom (5689787329..., 1329084801...)
   Server vrátil ciphertext: 9d802731f6590eae56ee...
   -> k_S mod 61 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 61 = 47

[*] Testujem Order 67 s bodom (4776339692..., 5308234546...)
   Server vrátil ciphertext: 95a0228d7c6f9d477364...
   -> k_S mod 67 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 67 = 61

[*] Testujem Order 71 s bodom (5841544013..., 4236120018...)
   Server vrátil ciphertext: 39eb5e213ed270576789...
   -> k_S mod 71 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 71 = 26

[*] Testujem Order 73 s bodom (3677056982..., 5823291158...)
   Server vrátil ciphertext: eca5231f4939a8361fb4...
   -> k_S mod 73 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 73 = 60

[*] Testujem Order 79 s bodom (2613272500..., 1585852019...)
   Server vrátil ciphertext: 5017a529e2a175ede518...
   -> k_S mod 79 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 79 = 64

[*] Testujem Order 83 s bodom (2688716873..., 4824571882...)
   Server vrátil ciphertext: 3646eb1ee28e3914c9b5...
   -> k_S mod 83 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 83 = 42

[*] Testujem Order 89 s bodom (3210428526..., 4772382840...)
   Server vrátil ciphertext: cc49d991ae01d961fc20...
   -> k_S mod 89 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 89 = 86

[*] Testujem Order 97 s bodom (1743409825..., 9775048628...)
   Server vrátil ciphertext: 1688f0b391aee4ea51cb...
   -> k_S mod 97 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 97 = 8

[*] Testujem Order 101 s bodom (6226734405..., 4382109723...)
   Server vrátil ciphertext: 8a824619a8056c3ceacd...
   -> k_S mod 101 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 101 = 1

[*] Testujem Order 103 s bodom (7161664308..., 5302853130...)
   Server vrátil ciphertext: a69e5720ff4ef3dd7654...
   -> k_S mod 103 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 103 = 35

[*] Testujem Order 107 s bodom (4292302513..., 1278608508...)
   Server vrátil ciphertext: 18cf149899f205965ce1...
   -> k_S mod 107 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 107 = 26

[*] Testujem Order 109 s bodom (1593999202..., 2676743842...)
   Server vrátil ciphertext: a9ed15a302cb43a9b5ba...
   -> k_S mod 109 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 109 = 76

[*] Testujem Order 113 s bodom (3385577856..., 3625197450...)
   Server vrátil ciphertext: 1755752a7c1332623726...
   -> k_S mod 113 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 113 = 23

[*] Testujem Order 127 s bodom (4398287998..., 9005817631...)
   Server vrátil ciphertext: 734cf68646797c3184fb...
   -> k_S mod 127 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 127 = 82

[*] Testujem Order 131 s bodom (3301865213..., 1111395993...)
   Server vrátil ciphertext: 78609a6f941e3cca9c68...
   -> k_S mod 131 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 131 = 61

[*] Testujem Order 137 s bodom (5917136120..., 4273625549...)
   Server vrátil ciphertext: 6c56d73f9094b2559194...
   -> k_S mod 137 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 137 = 4

[*] Testujem Order 139 s bodom (5405872235..., 2905365057...)
   Server vrátil ciphertext: 772634cfeec114adf5cd...
   -> k_S mod 139 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 139 = 69

[*] Testujem Order 149 s bodom (3478263632..., 1443429172...)
   Server vrátil ciphertext: 6922bc77d22683c446d7...
   -> k_S mod 149 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 149 = 64

[*] Testujem Order 151 s bodom (2972548050..., 5123200163...)
   Server vrátil ciphertext: 041b8a43eac1825ffeb4...
   -> k_S mod 151 != 0. Hľadám presný zvyšok lokálnou simuláciou...
   -> Zhoda nájdená! k_S mod 151 = 30

[*] Testovanie dokončené.

[*] Rekonštrukcia privátneho kľúča pomocou CRT...
[*] Pripravujem dáta pre Čínsku zvyškovú vetu (CRT)...
   k_S ≡ 1 (mod 2)
   k_S ≡ 1 (mod 3)
   k_S ≡ 2 (mod 5)
   k_S ≡ 6 (mod 7)
   k_S ≡ 4 (mod 11)
   k_S ≡ 5 (mod 13)
   k_S ≡ 4 (mod 17)
   k_S ≡ 6 (mod 19)
   k_S ≡ 19 (mod 23)
   k_S ≡ 13 (mod 29)
   k_S ≡ 3 (mod 31)
   k_S ≡ 2 (mod 37)
   k_S ≡ 6 (mod 41)
   k_S ≡ 32 (mod 43)
   k_S ≡ 43 (mod 47)
   k_S ≡ 32 (mod 53)
   k_S ≡ 47 (mod 59)
   k_S ≡ 47 (mod 61)
   k_S ≡ 61 (mod 67)
   k_S ≡ 26 (mod 71)
   k_S ≡ 60 (mod 73)
   k_S ≡ 64 (mod 79)
   k_S ≡ 42 (mod 83)
   k_S ≡ 86 (mod 89)
   k_S ≡ 8 (mod 97)
   k_S ≡ 1 (mod 101)
   k_S ≡ 35 (mod 103)
   k_S ≡ 26 (mod 107)
   k_S ≡ 76 (mod 109)
   k_S ≡ 23 (mod 113)
   k_S ≡ 82 (mod 127)
   k_S ≡ 61 (mod 131)
   k_S ≡ 4 (mod 137)
   k_S ≡ 69 (mod 139)
   k_S ≡ 64 (mod 149)
   k_S ≡ 30 (mod 151)

==================================================
 VÝSLEDOK - Rekonštruovaný privátny kľúč:
==================================================

   k_S (dekadicky) = 3091796379617811793175999080165857890159327736367820343547

   k_S (hex)       = 0x7e17dc41156f008bf60be7cbed76f78b92b5dc65e84488fb

   Počet bitov kľúča: 191

[*] Overujem výsledok...
     (Súčin modulov R = 198 bitov)
     (Rád krivky n    = 192 bitov)
     Overujem vstupné kongruencie:
     Všetky vstupné kongruencie sú splnené.

[✓] Privátny kľúč bol úspešne zrekonštruovaný (modulo R) a spĺňa vstupné kongruencie!
   Kľúč je aj v správnom rozsahu [1, n-1].

[*] Pokus o podpísanie dokumentu pomocou rekonštruovaného kľúča...
[*] Vytvorený podpis (SHA256(key_bytes + msg)): a9f0dded6acbb24f2f6e2a67f8e04cb6049cd48ab5673238a5e83329c236bcb7
[*] Odpoveď servera po odoslaní podpisu:
Signature verified.
SK-CERT{wh3r3_15_7h47_p01n7}

Menu:
1) Submit client pubkey
2) Encrypt message
3) Submit signed document
(Ctrl+C or close connection to exit)
Choice:

[*] Skript dokončený.
```





## Vlajka

```
SK-CERT{wh3r3_15_7h47_p01n7}
```
