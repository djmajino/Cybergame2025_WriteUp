# Zadanie

EN: The producer did not upgrade their infrastructure, and their servers were encrypted again. The attackers used slightly modified malware, but it should not be too hard to decrypt.

SK: Producent neaktualizoval svoju infraštruktúru a ich servery boli opäť zašifrované. Útočníci použili mierne upravený malware, ale nemalo by to byť príliš ťažké dešifrovať.

**Súbory**

- recovery_2.zip

## Riešenie

Archív obsahoval

- ransomware.py

- files\slopes_of_the_unknowable.txt.enc

- files\slon.png.enc

**Kód ransomware.py**

```python
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
```

V tomto prípade ide o zložitejší ransomware. Na základe poskytnutého skriptu môžeme povedať, že prvý blok dát každého súboru je šifrovaný nasledovne:

- Každý bajt prvého bloku sa XOR-uje s bajtom kľúča.

- Najnižší bit každého zašifrovaného bajtu (LSB) je náhodne zmenený (bit flipping).

Každý nasledujúci blok:

- XOR-uje sa s rotovaným kľúčom.

- Výsledné bajty sú rotované vľavo o 3 bity (`rotate_left(b, 3)`).

Keďže súčasťou procesu je zmena LSB (least significant byte) v prvom bloku náhodne, kľúč nedokážeme spoľahlivo odvodiť z prvého bloku. Preto budeme musieť odvodiť kľúč pomocou druhého bloku (ktorý je spoľahlivo šifrovaný bez náhodnosti) pomocou známej hlavičky súboru PNG (IHDR).

Postup riešenia:

**1. Získať 16-bajtový kľúč zo súboru `slon.png.enc`:**

- Preskočiť prvý blok (16 bajtov).

- Využiť druhý blok, kde očakávame štandardnú časť PNG (začiatok IHDR chunku). Tu použijeme druhý blok až koniec png súboru predošlej úlohy, dúfajúc, že sa jedná o ten istý súbor

**2. Implementovať kompletný dešifrovací skript podľa princípu ransomwaru.**

```python
import os

FILES_DIR_OLD = "recovery_1\\files"
FILES_DIR_NEW = "recovery_2\\files"

def rotate_left(byte, bits):
    return ((byte << bits) & 0xff) | (byte >> (8 - bits))

def rotate_right(byte, bits):
    return ((byte >> bits) & 0xff) | ((byte << (8 - bits)) & 0xff)

def derive_correct_key(enc_file, plain_file):
    with open(enc_file, "rb") as f_enc, open(plain_file, "rb") as f_plain:
        f_enc.seek(16)
        f_plain.seek(16)
        enc_block = f_enc.read(16)
        plain_block = f_plain.read(16)

    rotated_xor = bytes(rotate_right(b, 3) ^ p for b, p in zip(enc_block, plain_block))
    # kľúč je rotovaný o offset 1 vľavo, takže opačne (15 vľavo == 1 vpravo)
    correct_key = rotated_xor[-1:] + rotated_xor[:-1]
    return correct_key

def decrypt(filename, key):
    block_size = len(key)

    with open(filename, "rb") as f:
        data = f.read()

    decrypted = bytearray()
    num_blocks = (len(data) + block_size - 1) // block_size

    for i in range(num_blocks):
        enc_block = data[i * block_size : (i + 1) * block_size]
        if i == 0:
            # Prvý blok (XOR, náhodný LSB)
            dec_block = bytearray((b ^ key[j]) & 0xFE for j, b in enumerate(enc_block))
        else:
            offset = i % block_size
            rotated_key = key[offset:] + key[:offset]
            rotated = bytes(rotate_right(b, 3) for b in enc_block)
            dec_block = bytes(b ^ k for b, k in zip(rotated, rotated_key))
        decrypted.extend(dec_block)

    dec_filename = filename[:-4] if filename.endswith(".enc") else filename + ".dec"
    with open(dec_filename, "wb") as f:
        f.write(decrypted)

    print(f"[+] Decrypted file saved to: {dec_filename}")

# Získanie správneho XOR kľúča
key = derive_correct_key(
    os.path.join(FILES_DIR_NEW, "slon.png.enc"),
    os.path.join(FILES_DIR_OLD, "slon.png")
)

print(f"[+] Correctly derived key: {key.hex()}")

# Dekryptuj všetky .enc súbory v recovery_2
for filename in os.listdir(FILES_DIR_NEW):
    if filename.endswith(".enc"):
        decrypt(os.path.join(FILES_DIR_NEW, filename), key)
```

Dostaneme:

```
Rhrdddhnf thd Rlopes of the Unknowable

It all started with Rick waking up from a hangover inside a snow globe.
“Morty, get the sledgehammer. I accidentally dimension-hopped into a Christmas ornament again.”

Five smashed snowmen later, they stood in front of the portal gun.

“Morty, we’re going skiing. But not just anywhere,” Rick slurred, calibrating the gun with one hand while pouring schnapps into his coffee with the other. “We’re going outside the Central Finite Curve.”

Morty blinked. “Wait, what? Isn't that where all the non-Rick-dominated realities are?”

“Exactly! Which means we might actually get decent ski lift service.”

They portaled into a parallel universe ski resort called Slippery Realities, where the laws of physics were suggestions and snowflakes screamed as they fell.

“W-what the hell is this place?” Morty yelled as he adjusted his ski goggles, which were alive and whispering ominous prophecies into his ears.

Rick adjusted his skis, which were shaped like interdimensional fish. “This is Universe -∞.9b. Snow here is made of crystallized existential dread. It's primo for shredding.”

As they hit the slopes, Rick started yelling, “Watch out for the Slope Moguls! They’re sentient!”

Morty screamed as a mogul jumped at him, yelling “DO A TRICK OR DIE!”

Halfway down the mountain, they hit a temporal avalanche. Time itself started rewinding. Rick turned into a baby. Morty turned into a failed tax auditor.

“Rick! I can’t audit powder! I don’t even know what a W-2 is in this universe!”

Rick, now a toddler with a lab coat diaper, screamed, “BABY RICK NEEDS A TIME NAP!”

Thankfully, a sentient snowboard named Chad rescued them by doing a backflip so gnarly it temporarily restored local causality.

At the bottom of the mountain was a ski lodge run by Nietzsche clones, where the hot chocolate tasted like despair and came with a complimentary crisis of identity.

“We should go,” Morty muttered, sipping his drink while weeping softly.

“Not until we beat the Downhill Boss,” Rick said, pointing to the ski hill’s final challenge: a 10,000-foot vertical drop guarded by a giant snow demon made of failed philosophies.

Morty screamed.

Rick screamed louder—but only because his marshmallow was too hot.

They escaped by skiing off the edge of the universe itself, launching into the meta-dimensional void where gravity was negotiable and ski poles argued about Kantian ethics.

Back home, covered in frost and trauma, Morty collapsed on the couch.

“Rick… why?”

Rick tossed him a t-shirt that read ‘I Skied Outside the Central Finite Curve and All I Got Was a Recursive Mental Breakdown’.

“Because, Morty. Skiing inside the curve is for posers.”

THE END.

(Or is it? Time is still reversing in three universes. Sorry, Chad.)
############################################################################################


            SK-CERT{r1ck_4nd_m0r7y_4dv3n7ur35}    


############################################################################################
```

## Vlajka

```
SK-CERT{r1ck_4nd_m0r7y_4dv3n7ur35}
```
