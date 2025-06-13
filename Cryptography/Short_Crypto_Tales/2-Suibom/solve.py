#!/usr/bin/env python3
"""
vypočíta SK-CERT flag z parametrov a hodnôt F(n)

Potrebné balíčky:
    pip install sympy

"""

import json, csv, math, sys, time
from pathlib import Path
from sympy import factorint  # rýchly rozklad 12×32-bit prvočísel
# ---------- pomocné algoritmy ----------

def bsgs(g: int, h: int, p: int, order: int) -> int:
    """
    Baby-Step Giant-Step pre diskrétny logaritmus v g^x = h (mod p)
    funguje spoľahlivo pre order ≤ 2³²  (≈ 65 k baby-krokov)

    :vracia: x v rozsahu 0 ≤ x < order
    """
    m = int(math.isqrt(order) + 1)
    # baby-steps
    table = {pow(g, j, p): j for j in range(m)}
    # g^{-m} ≡ g^{m·(p-2)}  (Fermatov trik)
    factor = pow(g, (p - 2) * m % (p - 1), p)

    gamma = h
    for i in range(m):
        if gamma in table:                 # našli sme zhodu
            return (i * m + table[gamma]) % order
        gamma = (gamma * factor) % p
    raise ValueError("logaritmus sa nenašiel - niečo nesedí")

def crt(residues, moduli):
    """Čínska veta o zvyškoch pre vzájomne prvočíselné moduly."""
    x, M = 0, math.prod(moduli)
    for a_i, m_i in zip(residues, moduli):
        M_i = M // m_i
        inv = pow(M_i, -1, m_i)            # modulárny inverz
        x = (x + a_i * M_i * inv) % M
    return x

# ---------- načítanie vstupov ----------
with open("params.json") as f:
    params = json.load(f)
p = int(params["p"])
g = int(params["g"])
N = int(params["N"])

with open("values.csv", newline="") as f:
    rdr = csv.DictReader(f)
    F1 = next(int(row["F(n)"]) for row in rdr if int(row["n"]) == 1)

# ---------- hlavný výpočet ----------

# rozklad N (12 × 32-bit prvočísel)
factorisation = factorint(N)          # {q: 1} všetky exponenty sú 1
primes = list(factorisation.keys())

residues, moduli = [], []
for q in primes:
    exp = N // q
    g_q = pow(g, exp, p)
    h_q = pow(F1, exp, p)
    x_q = bsgs(g_q, h_q, p, q)
    residues.append(x_q)
    moduli.append(q)

x = crt(residues, moduli)             # 0 ≤ x < N

# ---------- konverzia na flag ----------

byte_len = (x.bit_length() + 7) // 8
flag_bytes = x.to_bytes(byte_len, "big")

flag = flag_bytes.decode()

print(f"Vlajka: {flag}")


