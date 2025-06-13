# Zadanie

EN: We have intercepted a ciphertext along with a presumed key exchange in plaintext. Our sources informed us that the adversary is using a custom-made cipher they call "3AES".

SK: Zachytili sme šifrovaný text spolu s predpokladanou výmenou kľúčov v čistom texte. Naše zdroje nás informovali, že protivník používa vlastnoručne vyrobenú šifru, ktorú nazýva "3AES".

**Súbory**

- intercept.txt

```
key1: h+NvKyaJFRhpn7lRWo0JGGcSk7TOd2ltibSSI1CGDCk=
key2: CznIYU0rBgmzSb7WyqYfj+WKyDSXbbnsa8Wp/IRvUOc=
key3: ihpLsXPURUTwH4ULO9/87rHRCQibQO6+V4/QKJL7Bgg=

Y: rOkz0hogqrrjVXe8KhfwPmTXqy0NI5BaaVRwg8g4490Gi//XIIYY6t7pMpw/0DN4V26tcdwmmOOne75oEt4/oQ==
X: t+WZSn6H1mA9XUQJrQ2xxt33nVh6orKFygb7Q+8xMe9JSk7XgMdZ8Fwq9rSMw9SuCZWoIJ8qYOSOKwmyyvMmW7/kkPDoWNEezfme08HmEWi3DrPAefIpNVVewbfVzt5j
Y: dNMxxcWRHkxNxHu17gw5g5IE/Jf6tNmxw4OfBHEXfRv0cx4pKVKYjZofSRAgFspLnWcdR5GGasKxCgpOANPyS4liypMrPFKlXy/pm2BG7bM=
X: k8JzsMNxiG5KPGSdM/YjGjW7y8dzgG8vsQ3RB062Kz1/EzwUaWz5Sr2UFNuq0jcWqDdj3Y9I0UKz0rYdZuTxMHZ+oKVEqI8Xv9CuvOmOzkdBoBgsjaWT9ke6+BPcMH9Kpwq/jgoYVQ7SfJDKx5GCAxzSLyyS6tXGIZRrUny6jiU=
```

## Riešenie

```python
import base64
from Crypto.Cipher import AES

# Odstránenie PKCS7 paddingu (klasika pre AES blokovú šifru)
def unpad(data):
    return data[:-data[-1]]


# Dešifrovanie pomocou AES-256 EDE: Decrypt(k3) → Encrypt(k2) → Decrypt(k1)
def decrypt_ede(ct, k1, k2, k3):
    cipher = AES.new(k3, AES.MODE_ECB)
    data = cipher.decrypt(ct)
    cipher = AES.new(k2, AES.MODE_ECB)
    data = cipher.encrypt(data)
    cipher = AES.new(k1, AES.MODE_ECB)
    data = cipher.decrypt(data)
    return unpad(data)


k1 = base64.b64decode("h+NvKyaJFRhpn7lRWo0JGGcSk7TOd2ltibSSI1CGDCk=")
k2 = base64.b64decode("CznIYU0rBgmzSb7WyqYfj+WKyDSXbbnsa8Wp/IRvUOc=")
k3 = base64.b64decode("ihpLsXPURUTwH4ULO9/87rHRCQibQO6+V4/QKJL7Bgg=")

# ======================= DEŠIFROVANIE SPRÁV =======================

ciphertexts_b64 = [
    "rOkz0hogqrrjVXe8KhfwPmTXqy0NI5BaaVRwg8g4490Gi//XIIYY6t7pMpw/0DN4V26tcdwmmOOne75oEt4/oQ==",
    "t+WZSn6H1mA9XUQJrQ2xxt33nVh6orKFygb7Q+8xMe9JSk7XgMdZ8Fwq9rSMw9SuCZWoIJ8qYOSOKwmyyvMmW7/kkPDoWNEezfme08HmEWi3DrPAefIpNVVewbfVzt5j",
    "dNMxxcWRHkxNxHu17gw5g5IE/Jf6tNmxw4OfBHEXfRv0cx4pKVKYjZofSRAgFspLnWcdR5GGasKxCgpOANPyS4liypMrPFKlXy/pm2BG7bM=",
    "k8JzsMNxiG5KPGSdM/YjGjW7y8dzgG8vsQ3RB062Kz1/EzwUaWz5Sr2UFNuq0jcWqDdj3Y9I0UKz0rYdZuTxMHZ+oKVEqI8Xv9CuvOmOzkdBoBgsjaWT9ke6+BPcMH9Kpwq/jgoYVQ7SfJDKx5GCAxzSLyyS6tXGIZRrUny6jiU="
]

# Base64 -> bytes
ciphertexts = [base64.b64decode(c) for c in ciphertexts_b64]

# Dešifrovanie všetkých 3 častí správ
plaintext = b''.join(decrypt_ede(c, k1, k2, k3) for c in ciphertexts)

print("\n== Dešifrovaný plaintext ==")
print(plaintext.decode(errors="replace"))
```

alebo

[CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)AES_Decrypt(%7B'option':'Base64','string':'ihpLsXPURUTwH4ULO9/87rHRCQibQO6%2BV4/QKJL7Bgg%3D'%7D,%7B'option':'Hex','string':''%7D,'ECB/NoPadding','Raw','Raw',%7B'option':'Hex','string':''%7D,%7B'option':'Hex','string':''%7D)AES_Encrypt(%7B'option':'Base64','string':'CznIYU0rBgmzSb7WyqYfj%2BWKyDSXbbnsa8Wp/IRvUOc%3D'%7D,%7B'option':'Hex','string':''%7D,'ECB/NoPadding','Raw','Raw',%7B'option':'Hex','string':''%7D)AES_Decrypt(%7B'option':'Base64','string':'h%2BNvKyaJFRhpn7lRWo0JGGcSk7TOd2ltibSSI1CGDCk%3D'%7D,%7B'option':'Hex','string':''%7D,'ECB/NoPadding','Raw','Raw',%7B'option':'Hex','string':''%7D,%7B'option':'Hex','string':''%7D)&input=ck9rejBob2dxcnJqVlhlOEtoZndQbVRYcXkwTkk1QmFhVlJ3ZzhnNDQ5MEdpLy9YSUlZWTZ0N3BNcHcvMERONFYyNnRjZHdtbU9PbmU3NW9FdDQvb1E9PQp0K1daU242SDFtQTlYVVFKclEyeHh0MzNuVmg2b3JLRnlnYjdRKzh4TWU5SlNrN1hnTWRaOEZ3cTlyU013OVN1Q1pXb0lKOHFZT1NPS3dteXl2TW1XNy9ra1BEb1dORWV6Zm1lMDhIbUVXaTNEclBBZWZJcE5WVmV3YmZWenQ1agpkTk14eGNXUkhreE54SHUxN2d3NWc1SUUvSmY2dE5teHc0T2ZCSEVYZlJ2MGN4NHBLVktZalpvZlNSQWdGc3BMbldjZFI1R0dhc0t4Q2dwT0FOUHlTNGxpeXBNclBGS2xYeS9wbTJCRzdiTT0KazhKenNNTnhpRzVLUEdTZE0vWWpHalc3eThkemdHOHZzUTNSQjA2Mkt6MS9FendVYVd6NVNyMlVGTnVxMGpjV3FEZGozWTlJMFVLejByWWRadVR4TUhaK29LVkVxSThYdjlDdXZPbU96a2RCb0Jnc2phV1Q5a2U2K0JQY01IOUtwd3EvamdvWVZRN1NmSkRLeDVHQ0F4elNMeXlTNnRYR0laUnJVbnk2amlVPQ)

Výjde nám

> The meeting was compromised. They were waiting for us.It should be fine now. We switched to a custom cipher based on the AES standard.FINE but if this fails again I pick the crypto we use! What is the drop point?We had to flee. Our guy will wait for you near Slavin. Come right at noon. SK-CERT{1_w0nd3r_why_th3y_d0nt_us3_7h1s_1rl}

## Vlajka

```
SK-CERT{1_w0nd3r_why_th3y_d0nt_us3_7h1s_1rl}
```
