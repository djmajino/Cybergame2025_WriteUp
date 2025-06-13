import random
import json
import csv
from math import prod
from sympy import isprime, nextprime, divisors
from secret import flag

bits = 32
primes = []
while len(primes) < 12:
    candidate = random.getrandbits(bits) | (1 << (bits-1)) | 1
    if isprime(candidate):
        primes.append(int(candidate))

N = prod(primes)

offset = random.randint(2, 5000)
base = N*offset + 1
p = nextprime(base)

exp = (p - 1) // N
g = None
while g is None:
    a_candidate = random.randrange(2, p - 1)
    potential = pow(a_candidate, exp, p)
    if pow(potential, N, p) == 1:
        is_generator = True
        for q in primes:
            if pow(potential, N // q, p) == 1:
                is_generator = False
                break
        if is_generator:
            g = potential


flag = b"SK-CERT{REDACTED}"
x = int.from_bytes(flag, 'big')
assert x < N, "flag too large"


divs = divisors(N)
F = {}
for n in divs:
    total = 0
    for d in divs:
        if n % d == 0:
            total += pow(g, x * d, p)
    F[n] = total % p

with open('params.json', 'w') as file_1:
    json.dump({'p': str(p), 'g': str(g), 'N': str(N)}, file_1, indent=2)

with open('values.csv', 'w', newline='') as file_2:
    writer = csv.writer(file_2)
    writer.writerow(['n', 'F(n)'])
    for n in divs:
        writer.writerow([n, F[n]])
