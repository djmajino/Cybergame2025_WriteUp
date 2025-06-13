"""
Tento skript na základe pôvodných podpísaných správ zo súboru data.jsonodvodí 
platný podpis pre autorovu správu s veľkým prevodom, odvodí AES kľúč použitý 
v úlohe CTF a nakoniec dešifruje správu s vlajkou.

Potrebné balíčky:
    pip install pycryptodome
"""
import json
import hashlib
from pathlib import Path
from typing import List, Tuple

from Crypto.Cipher import AES

# Pomocné funkcie

def H(x: bytes) -> bytes:
    return hashlib.sha256(x).digest()


def hash_n(x: bytes, n: int) -> bytes:
    """Aplikuje hash H na vstup x presne n-krát (n ≥ 0)."""
    for _ in range(n):
        x = H(x)
    return x

# Hlavná logika vytvorenia podpisu

def collect_known_pairs(dataset: dict) -> List[Tuple[bytes, List[bytes]]]:
    """Vráti zoznam [(digest, [32 odhalených hodnôt])] pre každú podpísanú správu."""
    pairs = []
    for entry in dataset["signatures"]:
        msg: str = entry["message"]
        digest = hashlib.sha256(msg.encode()).digest()
        reveals = [bytes.fromhex(x) for x in entry["signature"]]
        pairs.append((digest, reveals))
    return pairs


def forge_signature(target_digest: bytes, pairs) -> List[bytes]:
    """Vytvorí platný podpis pre cieľový digest pomocou predchádzajúcich únikov."""
    forged: List[bytes] = []
    for i in range(32):
        needed = target_digest[i]
        for prev_digest, prev_reveals in pairs:
            available = prev_digest[i]
            if available >= needed:
                # Vieme vypočítať hash dopredu (available - needed)-krát.
                forged.append(hash_n(prev_reveals[i], available - needed))
                break
        else:
            raise RuntimeError(
                f"Nepodarilo sa pokryť bajt na pozícii {i} (potrebujeme {needed}).")
    return forged

# Vstupný bod skriptu

data_path = Path("data_mytest.json")

with data_path.open("r", encoding="utf-8") as fp:
    dataset = json.load(fp)

# Opätovné vytvorenie autorovej špeciálnej správy o veľkom prevode
pk0 = dataset["public_key"][0]
target_msg = f"{pk0} transfered 999999 CERTcoins to me"
target_digest = hashlib.sha256(target_msg.encode()).digest()
#print(hashlib.sha256(target_msg.encode()).hexdigest()) 

# Vytvorenie podpisu a odvodenie AES kľúča
pairs = collect_known_pairs(dataset)
forged = forge_signature(target_digest, pairs)
key = bytes(chunk[0] for chunk in forged)

# Výpis vytvoreného podpisu pre kontrolu
forged_hex = [chunk.hex() for chunk in forged]
#print("Vytvorený podpis (hex):")
#print(json.dumps(forged_hex, indent=2))
print(f"Kľúč: {key.hex()}")
# Dešifrovanie sajfrtextu :D
iv = bytes.fromhex(dataset["iv"])
#print(f"IV: {iv.hex()}")
enc = bytes.fromhex(dataset["enc"])
#print(f"Enc: {enc.hex()}")
flag = AES.new(key, AES.MODE_CBC, iv).decrypt(enc)

print(f"Vlajka: {flag.decode('utf-8')}")
