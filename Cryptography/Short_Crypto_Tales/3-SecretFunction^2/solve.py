import re, math, sys, time 

t0 = time.perf_counter() # meranie času

with open("message.txt", "r") as f:
    content = f.read()

n = int(re.search(r'n\s*=\s*([0-9]+)', content).group(1))
e = int(re.search(r'e\s*=\s*([0-9]+)', content).group(1))
enc_repr = re.search(r'enc\s*=\s*(.+)', content).group(1)

def modinv(a, m):
    return pow(a, -1, m)

# 1) koeficienty kvaternionu
coeffs = list(map(int, re.findall(r'([+-]?\d+)', enc_repr)))
if len(coeffs) != 4:
    sys.exit("Chyba: kvaternion nemá 4 koeficienty.")
a_enc, b_enc, c_enc, d_enc = coeffs

# 2) pomery r1, r2
inv_c = modinv(c_enc % n, n)
inv_d = modinv(d_enc % n, n)
r1 = (b_enc % n) * inv_c % n
r2 = (b_enc % n) * inv_d % n

# 3) lineárna sústava 
A1 = (3 - 3*r1) % n;  B1 = (1 - 13*r1) % n; C1 = (337 - 37*r1) % n
A2 = (3 - 7*r2) % n;  B2 = (1 - 133*r2) % n; C2 = (337 -  7*r2) % n

D  = (B1*C2 - B2*C1) % n
P0 = ((A2*C1 - A1*C2) * modinv(D, n)) % n
Q0 = ((B2*A1 - B1*A2) * modinv(D, n)) % n

# 4) faktorizácia
p = math.gcd(P0, n)
print("p = ",p)
if p in (1, n):
    sys.exit("Zlyhalo: gcd(P0, n) nedal netriviálny deliteľ.")
q = n // p
print("q = ", q)

# 5) získanie vlajky
m_inv_mod_q = (P0 % q) * modinv(p % q, q) % q
m           = modinv(m_inv_mod_q, q)
flag_bytes  = m.to_bytes((m.bit_length()+7)//8, 'big')

elapsed = time.perf_counter() - t0
print(f"Duration: {elapsed:.3f} s  \nFlag:     {flag_bytes.decode()}")