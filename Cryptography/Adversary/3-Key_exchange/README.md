# Zadanie

EN: The adversary started using a new algorithm for key exchange. We were able to get its schema from our source. We attach the communication where we suspect the adversary might be agreeing upon a key and then using the 3AES encryption we've seen previously.

SK: Protivník začal používať nový algoritmus na výmenu kľúčov. Podarilo sa nám získať jeho schému od nášho zdroja. Prikladáme komunikáciu, kde podozrievame, že protivník môže dohodnúť kľúč a následne použiť 3AES šifrovanie, ktoré sme už predtým videli.

**Súbory**

- messages.txt

- exchange.png

```
X: tL90zeX19A2CLF9PH9oMQEuAPURmv7rp+oQ/DWiXEwTTQ6Ry/yDBHgqBGAa+OCaoI5JfdGYqhM2SHCWQyVdKJPj8HTY3gkxG38JEaET+CgX7h3cPQrufwYG8UOH6scrk1+guWvLOIAb/VJZ7pbjnEeORtN9C91EvxhNAO7r9pSFczo2TCGyFSaNOsvzN6C88Gw+4eXMTtVw=
Y: mBpf0ZTjWUczik9rrfwdM4wgVrN4I+++PGQSctBkAliziynxXJxYT0KnWxf5q8f1utv9ERPaWsJ+e/fENymhCWELXAnXGFaF8LHLzl9N1TWxu4b1CPPsU2pi2Rar9pm9FLfN4x/yYfP7daqKD7Rvq67wRu9+jsrgQKFj7687mZA4I9s11NpQQ7TSrEVr8Xx0d8FIZsV4x9M=
X: R8BSLUs24ieC8nV22ER/HYDYE7ltrz548dNMJeC+SwsOrcXFmuTdYHlSCnor9NU28nSoDhCJ7DXMDL5gzEiPWsikIgeM30CNfyH2ny/A6H0eZrOyLiEK8ZOS79hoFDsbiA3IidA2KpB9EgbRz1vRzXoOsAhUTa27/Px3nlCOboZRhXnTruzsPnKpWYjvXRQLKKW/d4Y4BbI=
Y: xl24Q/q0QOTK0hl1zOrSLgOEfbg+pzUf2FLNfS4OJD8k+R5hviqHb+DFSO2m1gXzkNoQa2guDRSRtKmHqigFKB/azqdEahvEnbH/wUImMc5UeC1FjOwsc7MBrhELI2M+rpo0z2RvzX+2VF0fCQWGm8by5D7yyJL8VHsE6acQjGSvkz0L+kRNtAQXh4ywjAet3rxnSlyu1kO9N4BPjCpCYNtfuPbnccMUCWiePiyj+GXh838frFEDdzL9gVOA4CZSNIOOgIJ0Re1c3dPQBdxhqpeXXyoj4PUK1W1Q6ZjOr362SoD8PwUU55nQTPUW50cp
X: CuU+OFj7FoHmmT1Ppsfn+kbLwwQF9A9hvdLgE8sEIi6D6RyCr6b2E+YxQi2x9qkECPJkiuSeYypnDifjavlhvTez6hM2JbZV4WrrzmePjWd/a63ZBgTs/JR9j0XdO0xoXCi5Y0rPDjj0oJsfLilu34PXtO8t1Y2MnlPQ/aRvhn+xe3mKauDuDtPjI+N3Tood
Y: AYdjr4yUpFrQC23EKtj0+w5m6Qq5QnxHcCC8WeU9GUPH6rAig0auAEKMVyfGnj/qxHKXuFSnWX+9Z04hY3RYLw==
```

## Riešenie

```python
import base64
from Crypto.Cipher import AES

# XOR troch bajtových reťazcov po bajtoch
def xor3(a, b, c):
    return bytes(x ^ y ^ z for x, y, z in zip(a, b, c))

# Odstránenie PKCS7 paddingu (klasika pre AES blokovú šifru)
def unpad(data):
    return data[:-data[-1]]

# Automatické doplnenie Base64 paddingu ('=' na konci), ak chýba
def fix_base64_padding(s):
    return s + '=' * (-len(s) % 4)

# Dešifrovanie pomocou AES-256 EDE: Decrypt(k3) → Encrypt(k2) → Decrypt(k1)
def decrypt_ede(ct, k1, k2, k3):
    cipher = AES.new(k3, AES.MODE_ECB)
    data = cipher.decrypt(ct)
    cipher = AES.new(k2, AES.MODE_ECB)
    data = cipher.encrypt(data)
    cipher = AES.new(k1, AES.MODE_ECB)
    data = cipher.decrypt(data)
    return unpad(data)

# ======================= INPUT =======================

# Zachytené 3 výmeny správ medzi protivníkmi (M1, M2, M3) – každá 152 bajtov
M1_b64 = "tL90zeX19A2CLF9PH9oMQEuAPURmv7rp+oQ/DWiXEwTTQ6Ry/yDBHgqBGAa+OCaoI5JfdGYqhM2SHCWQyVdKJPj8HTY3gkxG38JEaET+CgX7h3cPQrufwYG8UOH6scrk1+guWvLOIAb/VJZ7pbjnEeORtN9C91EvxhNAO7r9pSFczo2TCGyFSaNOsvzN6C88Gw+4eXMTtVw="
M2_b64 = "mBpf0ZTjWUczik9rrfwdM4wgVrN4I+++PGQSctBkAliziynxXJxYT0KnWxf5q8f1utv9ERPaWsJ+e/fENymhCWELXAnXGFaF8LHLzl9N1TWxu4b1CPPsU2pi2Rar9pm9FLfN4x/yYfP7daqKD7Rvq67wRu9+jsrgQKFj7687mZA4I9s11NpQQ7TSrEVr8Xx0d8FIZsV4x9M="
M3_b64 = "R8BSLUs24ieC8nV22ER/HYDYE7ltrz548dNMJeC+SwsOrcXFmuTdYHlSCnor9NU28nSoDhCJ7DXMDL5gzEiPWsikIgeM30CNfyH2ny/A6H0eZrOyLiEK8ZOS79hoFDsbiA3IidA2KpB9EgbRz1vRzXoOsAhUTa27/Px3nlCOboZRhXnTruzsPnKpWYjvXRQLKKW/d4Y4BbI="

# Base64 -> bytes
M1 = base64.b64decode(M1_b64)
M2 = base64.b64decode(M2_b64)
M3 = base64.b64decode(M3_b64)

# XOR-ovanie všetkých 152 bajtov: výsledok obsahuje 3 AES kľúče ako Base64 text
xor_key = xor3(M1, M2, M3)
xor_key_text = xor_key.decode()

print("== Derivovaný XOR výstup ==")
print(xor_key_text)

# ======================= PARSOVANIE KĽÚČOV =======================

lines = [line.strip() for line in xor_key_text.strip().splitlines()]
k1 = base64.b64decode(fix_base64_padding(lines[0].split(":")[1]))
k2 = base64.b64decode(fix_base64_padding(lines[1].split(":")[1]))
k3 = base64.b64decode(fix_base64_padding(lines[2].split(":")[1]))

# ======================= DEŠIFROVANIE SPRÁV =======================

ciphertexts_b64 = [
    "xl24Q/q0QOTK0hl1zOrSLgOEfbg+pzUf2FLNfS4OJD8k+R5hviqHb+DFSO2m1gXzkNoQa2guDRSRtKmHqigFKB/azqdEahvEnbH/wUImMc5UeC1FjOwsc7MBrhELI2M+rpo0z2RvzX+2VF0fCQWGm8by5D7yyJL8VHsE6acQjGSvkz0L+kRNtAQXh4ywjAet3rxnSlyu1kO9N4BPjCpCYNtfuPbnccMUCWiePiyj+GXh838frFEDdzL9gVOA4CZSNIOOgIJ0Re1c3dPQBdxhqpeXXyoj4PUK1W1Q6ZjOr362SoD8PwUU55nQTPUW50cp",
    "CuU+OFj7FoHmmT1Ppsfn+kbLwwQF9A9hvdLgE8sEIi6D6RyCr6b2E+YxQi2x9qkECPJkiuSeYypnDifjavlhvTez6hM2JbZV4WrrzmePjWd/a63ZBgTs/JR9j0XdO0xoXCi5Y0rPDjj0oJsfLilu34PXtO8t1Y2MnlPQ/aRvhn+xe3mKauDuDtPjI+N3Tood",
    "AYdjr4yUpFrQC23EKtj0+w5m6Qq5QnxHcCC8WeU9GUPH6rAig0auAEKMVyfGnj/qxHKXuFSnWX+9Z04hY3RYLw=="
]

# Base64 -> bytes
ciphertexts = [base64.b64decode(c) for c in ciphertexts_b64]

# Dešifrovanie všetkých 3 častí správ
plaintext = b''.join(decrypt_ede(c, k1, k2, k3) for c in ciphertexts)

print("\n== Dešifrovaný plaintext ==")
print(plaintext.decode(errors="replace"))
```

Výjde nám výstup

> == Derivovaný XOR výstup ==
> key1: Om3TeRjbnnGxxNs3k/73aZXMZWneHF9XD11tIklg4kk=
> key2: kl426dwQSc8lEZNPRy94s7MTZBHdiycxLf/9ShBKR+0=
> key3: eWYw7oB8h46tzNTJEHR75h/urZ94e5G1IDGCDkOh0Sw=
> 
> == Dešifrovaný plaintext ==
> They were there again.  Exchanging keys in the plaintext is not something a sensible person would do! We cannot make rookie mistakes like this again. The key exchange algo I made is 100% secure as it's based on Diffie Hellman.Okay Mr. Robot. Since they've busted all our people I'll be waiting for you on the corner of Priehradna and Modricova tomorrow at 15:30Agreed. SK-CERT{d1ff13_h3llm4n_15_n07_7h47_51mpl3_l0l}

## Vlajka

```
SK-CERT{d1ff13_h3llm4n_15_n07_7h47_51mpl3_l0l}
```
