# Zadanie

EN: The script for the final episode is encrypted with a completely different ransomware. It’s the grand finale of the series, and we have to recover it.

SK: Scenár pre poslednú epizódu je zašifrovaný úplne iným ransomvérom. Je to veľké finále seriálu a musíme ho obnoviť.

**Súbory**

- recovery_3.zip

## Riešenie

Archív obsahoval

- main.py

- files\flag.txt.enc

- files\slonik.png.enc

**Kód main.py**

```python
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
```

Opäť predpokladám, že slonik.png je to isté ako slon.png z predošlých úloh... 

Tu rovno začnem, že autori sú zmrdi (v dobrom :D) a zbytočne nás zviedli z cesty, kde v zipe nám metadáta napovedali, že sa nešifrovalo naraz ale na dvakrát, a že najprv bol sloník a potom flag.. Bullshit.. Tu bolo jasné, že pokiaľ nepoznáme známy plaintext alebo známy súbor sloník, tak je to neriešiteľné pokiaľ neboli zašifrované spolu.. Takže na tomto som zakladal a po tom ako som predpokladal, že slonik bol prvý a flag druhý a získal som stav PRNG pre counter_0, x_0, y_0 a nepodarilo sa mi s týmto dešifrovať flag, tak bolo jasné, že flag musel byť prvý... flag má 3315 bajtov, čo je 3315/4 (šifrované po 4 bajtoch)

> chunks = [data[i:i + 4] for i in range(0, len(data), 4)]

to máme 829 blokov (PRNG stavy 0-828), potrebujeme zistiť stav PRNG v 829 interácii. Teda counter_829, x_829, y_829



Skript, na získanie tohto stavu je

```python
import os
import math
from z3 import * 

FLAG_ENC_PATH = "files/flag.txt.enc"   # Cesta k zašifrovanému flag.txt
SLON_ORIG_PATH = "files/slon.png"      # Cesta k originálnemu slon.png
SLON_ENC_PATH = "files/slonik.png.enc" # Cesta k zašifrovanému slonik.png
# ---------------------------------------------

try:
    # Získanie veľkosti flag.txt.enc pre výpočet N_flag
    flag_size = os.path.getsize(FLAG_ENC_PATH)
    N_flag = math.ceil(flag_size / 4.0)
    print(f"[+] Veľkosť '{FLAG_ENC_PATH}': {flag_size} bajtov, N_flag = {N_flag}")

    # Výpočet counter stavu pred šifrovaním slonik.png
    c_s = (N_flag * 362437) & 0xffffffff
    print(f"[+] Vypočítaný counter (c_s) pred slonik.png: {c_s}")

    # Prečítanie prvých 8 bajtov originálu a šifrovaného súboru
    with open(SLON_ORIG_PATH, "rb") as f_orig, open(SLON_ENC_PATH, "rb") as f_enc:
        plain_bytes = f_orig.read(8)
        cipher_bytes = f_enc.read(8)

    if len(plain_bytes) < 8 or len(cipher_bytes) < 8:
        raise ValueError("Súbory sú príliš krátke (potrebujeme aspoň 8 bajtov).")

    # XORovanie na získanie prvých 8 bajtov keystreamu
    keystream_bytes = bytes(p ^ c for p, c in zip(plain_bytes, cipher_bytes))

    # Konverzia na dve 32-bit (4-byte) celé čísla (little-endian)
    k_slon_1 = int.from_bytes(keystream_bytes[0:4], 'little')
    k_slon_2 = int.from_bytes(keystream_bytes[4:8], 'little')
    print(f"[+] Prvé dve keystream hodnoty (k_slon_1, k_slon_2): ({k_slon_1}, {k_slon_2})")

    # --- Krok 3: Výpočet y_s1 a y_s2 ---
    c_s1 = (c_s + 362437) & 0xffffffff
    c_s2 = (c_s1 + 362437) & 0xffffffff

    y_s1 = (k_slon_1 - c_s1) & 0xffffffff
    y_s2 = (k_slon_2 - c_s2) & 0xffffffff
    print(f"[+] Vypočítané interné stavy (y_s1, y_s2): ({y_s1}, {y_s2})")

    # --- Krok 4: Použitie Z3 na nájdenie (x_s, y_s) ---
    print("[+] Spúšťam Z3 Solver na nájdenie (x_s, y_s)...")

    # Definovanie 4 bajtový, teda 32-bitových bitových vektorov pre neznáme stavy x_s, y_s
    xs = BitVec('xs', 32)
    ys = BitVec('ys', 32)

    # Simulácia prvého kroku PRNG (zo stavu xs, ys na stav xs1, ys1)
    # t = (self.x^(self.x<<10)) & 0xffffffff
    ts = (xs ^ (xs << 10))
    # self.x = self.y
    xs1_calc = ys # Toto bude stav x v *ďalšom* kroku
    # self.y = ((self.y ^ (self.y>>10)) ^ (t ^ (t>>13))) & 0xffffffff
    ys1_calc = ((ys ^ LShR(ys, 10)) ^ (ts ^ LShR(ts, 13))) # Toto je vypočítané y_s1

    # Simulácia druhého kroku PRNG (zo stavu xs1, ys1 na stav xs2, ys2)
    # Vstupný stav pre tento krok je (xs1_calc, ys1_calc)
    # t = (self.x^(self.x<<10)) & 0xffffffff
    ts1 = (xs1_calc ^ (xs1_calc << 10))
    # self.x = self.y
    # xs2_calc = ys1_calc # Nepotrebujeme pre constraint
    # self.y = ((self.y ^ (self.y>>10)) ^ (t ^ (t>>13))) & 0xffffffff
    ys2_calc = ((ys1_calc ^ LShR(ys1_calc, 10)) ^ (ts1 ^ LShR(ts1, 13))) # Toto je vypočítané y_s2

    # Vytvorenie solvera a pridanie podmienok
    solver = Solver()
    solver.add(ys1_calc == y_s1) # Vypočítané y_s1 sa musí rovnať hodnote odvodenej z keystreamu
    solver.add(ys2_calc == y_s2) # Vypočítané y_s2 sa musí rovnať hodnote odvodenej z keystreamu

    # Kontrola riešiteľnosti a získanie modelu
    if solver.check() == sat:
        model = solver.model()
        found_xs = model[xs].as_long()
        found_ys = model[ys].as_long()
        found_cs = c_s 

        print("\n" + "="*30)
        print(" ÚSPECH: Stav PRNG pred šifrovaním slonik.png bol nájdený!")
        print(f" x       = {found_xs}")
        print(f" y       = {found_ys}")
        print(f" counter = {found_cs}")
        print("="*30)

        # Overenie
        print("\n[+] Overujem nájdený stav...")
        from main import PRNG 
        test_prng = PRNG(found_xs, found_ys, found_cs)
        gen_k1 = test_prng.rand()
        gen_k2 = test_prng.rand()
        print(f"  Generovaný k1: {gen_k1}")
        print(f"  Očakávaný k1:  {k_slon_1}")
        print(f"  Generovaný k2: {gen_k2}")
        print(f"  Očakávaný k2:  {k_slon_2}")
        if gen_k1 == k_slon_1 and gen_k2 == k_slon_2:
              print("[+] Overenie úspešné!")
        else:
              print("[!] CHYBA: Overenie zlyhalo!")

    else:
        print("\n" + "="*30)
        print(" CHYBA: Z3 Solver nenašiel riešenie.")
        print("="*30)

except Exception as e:
    print(f"[!] CHYBA: Vyskytla sa neočakávaná chyba: {e}")

```

Výstup:

```
[+] Veľkosť 'files/flag.txt.enc': 3315 bajtov, N_flag = 829
[+] Vypočítaný counter (c_s) pred slonik.png: 300460273
[+] Prvé dve keystream hodnoty (k_slon_1, k_slon_2): (1145485340, 3797463018)
[+] Vypočítané interné stavy (y_s1, y_s2): (844662630, 3496277871)
[+] Spúšťam Z3 Solver na nájdenie (x_s, y_s)...

==============================
 ÚSPECH: Stav PRNG pred šifrovaním slonik.png bol nájdený!
 x       = 2071160246
 y       = 2224663447
 counter = 300460273
==============================

[+] Overujem nájdený stav...
[+] Encrypted slon.png
  Generovaný k1: 1145485340
  Očakávaný k1:  1145485340
  Generovaný k2: 3797463018
  Očakávaný k2:  3797463018
[+] Overenie úspešné!
```

Máme stav 

> counter_829 = 300460273
> 
> x_829 = 2071160246
> 
> y_829 = 2224663447



Teraz vypočítať stav pre counter = 0, z metódy rand triedy PRNG je jasné, že je to reverzovateľné. Skript na vrátenie do stavu 0 je:



```
# vlozime triedu PRNG z povodne main.py
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

def inv_xor_rshift(y, k, bits=32):
    mask = (1 << bits) - 1
    x = y
    # Opakujeme aplikáciu x = y ^ (x >> k)
    # Počet iterácií ceil(bits / k) zaručuje, že sa bity "rozlejú" správne
    if k == 0: return x # Okrajový prípad
    num_iters = (bits + k - 1) // k # Výpočet ceil(bits / k)
    for _ in range(num_iters):
        x = y ^ (x >> k)
    return x & mask

def inv_xor_lshift(y, k, bits=32):
    mask = (1 << bits) - 1
    x = y
    # Opakujeme aplikáciu x = y ^ (x << k)
    if k == 0: return x # Okrajový prípad
    num_iters = (bits + k - 1) // k # Výpočet ceil(bits / k)
    for _ in range(num_iters):
        x = y ^ ((x << k) & mask) # Nezabudnúť maskovať posun vľavo
    return x & mask

# --- Funkcia pre spätný krok (použije v3 inverzie) ---
def reverse_rand_step(x_new, y_new, counter_new):
    mask = 0xffffffff

    counter_old = (counter_new - 362437) & mask
    y_old = x_new
    k = (y_old ^ (y_old >> 10)) & mask
    target_t_xor = (y_new ^ k) & mask
    # Použijeme v3 inverzné funkcie
    t = inv_xor_rshift(target_t_xor, 13)
    x_old = inv_xor_lshift(t, 10)

    return x_old, y_old, counter_old

# --- Hlavný výpočet ---
x_n = 2071160246
y_n = 2224663447
counter_n = 300460273
num_steps = 829
mask = 0xffffffff

expected_counter_0 = (counter_n - num_steps * 362437) & mask
print(f"Očakávaný counter_0: {expected_counter_0}") # Stále by mal byť 0

current_x = x_n
current_y = y_n
current_counter = counter_n

# Spustenie spätných krokov
for i in range(num_steps):
    current_x, current_y, current_counter = reverse_rand_step(current_x, current_y, current_counter)

x_0 = current_x
y_0 = current_y
counter_0 = current_counter

print(f"\nVypočítaný stav pre counter = 0:")
print(f"x_0 = {x_0}")
print(f"y_0 = {y_0}")
print(f"counter_0 = {counter_0}")


print("\n--- Overenie")
p_verify = PRNG(x_0, y_0, counter_0)
for _ in range(num_steps):
    p_verify.rand()

print(f"Stav po {num_steps} krokoch:")
print(f"x_{num_steps} = {p_verify.x} (Očakávané: {x_n})")
print(f"y_{num_steps} = {p_verify.y} (Očakávané: {y_n})")
print(f"counter_{num_steps} = {p_verify.counter} (Očakávané: {counter_n})")

match = (p_verify.x == x_n) and (p_verify.y == y_n) and (p_verify.counter == counter_n)
print(f"Stavy sa zhodujú: {match}")


```

Výsledok:

```
Očakávaný counter_0: 0

Vypočítaný stav pre counter = 0:
x_0 = 1497418956
y_0 = 31103793
counter_0 = 0

--- Overenie
Stav po 829 krokoch:
x_829 = 2071160246 (Očakávané: 2071160246)
y_829 = 2224663447 (Očakávané: 2224663447)
counter_829 = 300460273 (Očakávané: 300460273)
Stavy sa zhodujú: True
```

Získale sme stav 0 a z tohto stavu sme prešli 829x a získali sme ten istý výstup ako z pôvodnej triedy, takže máme pôvodné x a y.



Teraz skript na desifrovanie, potrebujeme vytvorit triedy Decyptor



```python
import os

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
    
class Decryptor:
    def __init__(self, prng):
        """Inicializuje Decryptor s daným PRNG."""
        self.prng = prng

    def decrypt(self, encrypted_file, decrypted_filename):

        dec_data = bytearray()
        try:
            with open(encrypted_file, "rb") as f_enc:
                enc_data = f_enc.read()
                # Rozdelí zašifrované dáta na 4-bajtové bloky (posledný môže byť kratší)
                chunks = [enc_data[i:i + 4] for i in range(0, len(enc_data), 4)]

                for i, chunk in enumerate(chunks):
                    # Generuje presne ten istý kľúč ako pri šifrovaní pre tento blok
                    key_int = self.prng.rand()
                    key_bytes = key_int.to_bytes(4, 'little') # Rovnaké poradie bajtov

                    # Operácia XOR s kľúčom (funguje aj pre kratší posledný blok vďaka zip)
                    decrypted_chunk = bytearray(b ^ k for b, k in zip(chunk, key_bytes))
                    dec_data += decrypted_chunk

            # Zapíše dešifrované dáta do výstupného súboru
            with open(decrypted_filename, "wb") as f_dec:
                f_dec.write(dec_data)
            print(f"[+] Dešifrovaný súbor {os.path.basename(encrypted_file)} -> {os.path.basename(decrypted_filename)}")

        except Exception as e:
            print(f"[!] Nastala chyba pri dešifrovaní {encrypted_file}: {e}")


initial_x = 1497418956
initial_y = 31103793
p = PRNG(initial_x, initial_y)

# Vytvorte inštanciu Decryptora s inicializovaným PRNG
d = Decryptor(p)

encrypted_filename = "flag.txt.enc"

# Zavoláme metódu decrypt
d.decrypt(encrypted_filename, "flag.txt")

print("[*] Dešifrovanie dokončené.")
```



výsledný flag.txt



```
Title: Rick and Morty’s Intergalactic McDonald’s Mishap

[Scene: The Garage]

Rick is covered in grease, holding a wrench in one hand and a mysterious green glowing orb in the other.

Rick: "Morty! We're going to McDonald’s. Not just any McDonald’s... the one on Planet Zarquon-7. It's got the only surviving stash of Szechuan sauce left in the multiverse!"

Morty: "Uhh... I dunno, Rick. Last time we went intergalactic fast food hopping, I almost got turned into a sentient ketchup packet."

Rick: "That’s because you asked for extra mustard, Morty. That's a war crime on Glapflap-9. Now come on!"

Cue portal gun sounds and green swirl

[Scene: Intergalactic McDonald’s - Planet Zarquon-7]

The restaurant looks like a mix between a space station, a ball pit, and a glowing jellyfish.

They walk in. A 12-eyed cashier greets them.

Cashier: "Welcome to McDonald’s, may I take your—OH MY GOD IS THAT RICK SANCHEZ?!"

Rick: "Yeah, yeah, save the autograph request, eyeball. Give me 10 McZarbnuggets, a GlorbCola, and all the Szechuan sauce you got."

Morty: "Can I just get like… a regular cheeseburger?"

Cashier: "You want that... with or without the prophecy?"

Morty: "The what?!"

[Chaos Ensues]

As they sit down with their glowing, suspiciously pulsating food, Rick opens the Szechuan sauce.

Rick: "Awww yeah. Look at that viscosity, Morty. That’s pure nostalgia-based marketing right there."

Suddenly, the sauce starts levitating. The packet explodes in a blinding light.

Morty: "RICK! WHAT’S HAPPENING?!"

Rick: "I think... I think I just unlocked the sauce’s true form. Oh no... Morty, we’ve summoned the Sauce Deity."

From the exploded sauce emerges a godlike being made entirely of golden dipping sauce.

Sauce Deity: "I AM MCDONALDAN, THE FLAVOR ETERNAL. YOU HAVE VIOLATED THE CONDIMENT CODE."

Rick: "Morty, I knew this sauce was too good to be true. Get the portal gun. We’re about to be deep-fried in cosmic barbecue."

Morty: "Why does this always happen when we go to fast food places?!"

[Escape Attempt]

They run through the play-place tube network, dodging sentient Happy Meals that chant “I’m loving it... eternally.”

Rick pulls out his portal gun but it’s covered in nugget grease.

Rick: "I CAN’T OPEN A PORTAL, MORTY! THE GUN'S TOO SLIPPERY!"

Morty: "Use a napkin!"

Rick: "There are no napkins in space, Morty. What kind of utopian hellscape is this?!"

[Finale: The Bargain]

Cornered by McDonaldan and his army of intergalactic fry guys, Rick makes an offer.

Rick: "How about this — you let us go, and I give you the recipe for... Chick-fil-A sauce?"

Sauce Deity: gasps "You... you possess such knowledge?!"

Rick: "Of course. I’m Rick Sanchez. I cloned a cow that secretes it."

Sauce Deity: "Deal."

[Back in the Garage]

Morty: "We almost died... because of sauce, Rick."

Rick: "Morty, never underestimate the power of condiments. Wars have started over less. Now help me build a sauce-proof shield for next time."

Morty: "...there’s going to be a next time?"

Rick: "Morty, there's always a next time."

Cue burp.

Rick: "Also... I kinda miss those fry guys. They were crunchy."

Roll credits with a remix of “I’m Lovin’ It” sung by a robotic Justin Roiland AI.


btw here is the flag SK-CERT{h4rd3r_x0r5h1f7_r3v3r53}


```

## Vlajka

```
SK-CERT{h4rd3r_x0r5h1f7_r3v3r53}
```
