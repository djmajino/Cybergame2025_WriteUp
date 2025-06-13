# Zadanie

EN: Even though we contracted the best javelin thrower in the whole world, the alien spaceship seems to have a force field. Switching to plan B - we must hack their mainframe. We know their computer would shut down if we pass the right keyword. However, the keyword is verified by a regular expression (regex). Can you find the correct string?

> ^(?:S[K])-(?:C(?:E|E{0})R)(?:T){v(?:3)r[y]_[5]7r(?:4)n6(?:3)_r3(?:6)3x}$

SK: Hoci sme najali toho najlepšieho vrhača oštepov na celom svete, zdá sa, že mimozemská vesmírna loď má nejaké silové pole. Prechádzame na plán B - musíme hacknúť ich riadiaci počítač. Vieme, že ich počítač sa vypne, ak zadáme to správne slovo. Avšak toto slovo je verifikované regulárnym výrazom (regex). Nájdeš správny text?

> ^(?:S[K])-(?:C(?:E|E{0})R)(?:T){v(?:3)r[y]_[5]7r(?:4)n6(?:3)_r3(?:6)3x}$

## Riešenie

V podstate o nejaký regex, ja som si len nechal vyextrahovať `a-z,A,Z,0-9,-,_,{,},_`

```python
import re

def filter_text(input_text):
    return re.sub(r'[^a-zA-Z0-9_\{\}-]', '', input_text)

# Príklady:
text = "^(?:S[K])-(?:C(?:E|E{0})R)(?:T){v(?:3)r[y]_[5]7r(?:4)n6(?:3)_r3(?:6)3x}$"

print(f"Výstup: '{filter_text(text)}'")

```

Dostanem

`Výstup: 'SK-CEE{0}RT{v3ry_57r4n63_r363x}'`

Trochu upravím aby bola pevná SK-CERT



## Vlajka

    SK-CERT{v3ry_57r4n63_r363x}
