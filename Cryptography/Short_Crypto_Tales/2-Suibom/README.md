# Zadanie

EN: While pruning timelines, Mobius met a bizarre variant obsessed with organizing numbers by divisibility. The variant handed him a dusty notebook titled The Table of Divine Divisors, muttering something about cosmic balance. Mobius, unimpressed, filed it under “N for Nonsense” — but kept a copy, just in case it had anything to do with jet skis or Lokis.

SK: Pri orezávaní časových línií Mobius stretol podivnú verziu, ktorá bola posadnutá usporadúvaním čísel podľa deliteľnosti. Tá mu podala prachom pokrytý zošit s názvom Tabuľka božských deliteľov a mumlala niečo o kozmickej rovnováhe. Mobius, bez záujmu, ho zaradil pod „N ako nezmysel“ — no jednu kópiu si ponechal, keby náhodou súvisel s vodnými skútrami alebo Lokimi.

**Súbory:**

- main.py
- params.json
- values.csv

## Riešenie

Zadanie samo o sebe hovorí o použití mobiusovej inverzie a kód to len potvrdzuje.

```python
for n in divs:
    total = 0
    for d in divs:
        if n % d == 0:
            total += pow(g, x * d, p)
    F[n] = total % p

```

$$
F(n) = \sum_{d \mid n} g^{xd} \pmod{p}
$$

Zo súborov poznáme 

$N$, čo je v našom prípade súčin náhodne vygenerovaných 12tich 32bitových prvočísel

```python
bits = 32
primes = []
while len(primes) < 12:
    candidate = random.getrandbits(bits) | (1 << (bits-1)) | 1
    if isprime(candidate):
        primes.append(int(candidate))

N = prod(primes)
```

$p$, čo je v našom prípade najbližšie prvočíslo nad celočiselnym násobkom $N$ a pripočítaním 1 ($N*offset + 1$)

```python
offset = random.randint(2, 5000)
base = N*offset + 1
p = nextprime(base)
```

$g$, čo je generátor cyklickej podskupiny rádu $N$ v multiplikatívnej skupine (mod $p$).

```python
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
```

Skript úlohy následne vyrobil z hexbajtov vlajky jedno veľké celé číslo, ale také aby nebolo väčšie ako $N$ a

```python
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
```

a následne našiel všetkých deliteľov $n$ pre $N$ a doplnil ku každému deliteľovi $n$ hodnotu

$$
F(n) = \sum_{d \mid n} g^{xd} \pmod{p}  
$$

kde $x$ je tajné celé číslo odvodené z vlajky. Všetky tieto dvojice (n,F(n)) zapísal do súboru  `values.csv`.

Týmto postupom zadanie **každému deliteľovi N priradilo hodnotu F(n)**, ktorá je vlastne „zabaleným“ súčtom mocnín generátora g pre rôzne násobky tajného exponenta x.  Keďže všetky tieto hodnoty sú verejné, **a formula je suma cez deliteľov**, je možné použiť **Möbiusovu inverziu**, ktorá umožní „odlepiť“ pôvodné hodnoty, tzn. získať $g^{xn}$ pre každý deliteľ $n$.

Doplním, že ide o Dirichletovu konvolúciu funkcie $d↦g^{xd}$ s konštantnou 1 a Möbiova inverzia naozaj dá priamo $g^{xn}$.

Avšak, vidíme, že medzi vypočítanými a zverejnenými hodnotami je aj hodnota pre $n = 1$ (teda $F(1)$). 

```csv
n,F(n)
1,2082453810845349954530857848803337496260456195444224420180316718294766405024576544871833258060845944088804345866959
```

V tomto špeciálnom prípade suma obsahuje len jeden člen, konkrétne: $F(1)=g^x\pmod{p}$, čo platí preto, že 1 má jediného deliteľa samého seba.

To znamená, že poznáme priamo hodnotu $g^x$ a vďaka znalosti generátora $g$ a modulu $p$ nemusíme využívať Möbiovu funkciu ani Möbiusovu inverziu na rekonštrukciu tejto hodnoty. Pre útok na úlohu nám teda úplne stačí vyriešiť diskrétny logaritmus pre $g$ a $F(1)$ v podskupine rádu $N$, pričom získané zvyšky pre jednotlivé faktory $N$ môžeme zlepiť Čínskou vetou o zvyškoch (CRT).

Aj keď zadanie v podstate volá po Möbiusovej inverzii, vďaka prítomnosti hodnoty $F(1) = g^x$ je možné riešiť úlohu oveľa jednoduchšie – postačí riešiť diskrétny logaritmus priamo na tejto dvojici. 

Okrem iného z csv vieme odčítať aj samotných 12 prvočísel, z ktorých bol $N$ odovedené, 

```csv
n,F(n)
1,2082453810845349954530857848803337496260456195444224420180316718294766405024576544871833258060845944088804345866959
--> 2154506941 <--,22632951765121400523883966852261626004970777782336602908708963927540918382964224521495145682268609929243183566557336
--> 2321340949 <--,10401727099478156813382826368585803972778954803737728238855287854811023415439067231467178600182129084666595032150375
--> 2477438617 <--,10397851866985311971031032311045041397965529059860118679361084206586684785656923199648479317834151570602324421029691
--> 2598192473 <--,2338872011165648058577659641359505109532326798598908948175671575704035255681973726541710992581138130305940515567975
--> 2656632067 <--,2376082603639769652563368416187618988248938939299896720183426389617980655558611744254682969887315082537368190850782
--> 2661306983 <--,7366158583016284927758678142643841623532947400577373889396136391335646161110806496496490012654606777475373373248452
--> 2704495351 <--,567645483790946881339562829931387262692188476592313650701706537505633670807071178946248001184751941708855101872886
--> 2704606529 <--,7104205944174923899355188705107126656714921726016152352705004978701037019125903274550553663934197894348892337472906
--> 3358863457 <--,3317078736458652830483025797727462002670768048713324511329300191862607985220034920930094872112831347590746523307879
--> 3439295149 <--,9368845995137740331194562427020246742502535389122959069819760227771438142620581123619744049340847186330939591375879
--> 3999681181 <--,11941413042192202891913765582196339394688882433905020337551413598189436370282892306922802080806974563495816931846581
--> 4090576319 <--,23183688365494625847645994911798292869517805911392680319424317064425202617208791504612986007858101888473842850952425
```

takže nepotrebujem ani riešiť faktorizáciu, teda rozklad $N$ potrebný čínsku vetu o zvyškoch (CRT) pretože CRT potrebuje poznať delitele, ale keďže ich máme, nie je čo zokladať.

## **Prečo nám stačí CRT (Čínska veta o zvyškoch)?**

**Čo robíme?**

- Zistíme $x \bmod q_1$, $x \bmod q_2$, ..., $x \bmod q_{12}$ pre všetky (prvočíselné) delitele $N$.

- Chceme celé $x$ modulo $N = q_1 \cdot q_2 \cdots q_{12}$.

### **Prečo práve CRT?**

CRT je **matematický nástroj**, ktorý hovorí:

> Ak poznáme zvyšok neznámeho čísla $x$ po delení každým z navzájom nesúdeliteľných čísel (teda prvočísel), existuje práve jedno $x$ (modulo súčinu všetkých týchto čísel), ktoré tieto zvyšky splní.

Teda:

- Ak poznáme $x \bmod q_1$, $x \bmod q_2$, ..., $x \bmod q_{12}$,

- vieme nájsť presne jedno $x$ v rozsahu $0 \leq x < N$, ktoré má všetky tieto zvyšky súčasne.

### **V našej úlohe:**

- Vieme vypočítať **$x$ modulo každého prvočíselného faktora $N$** (pomocou diskrétneho logaritmu v malej cyklickej skupine).

- Všetky tieto faktory $q_i$ sú vzájomne nesúdeliteľné (sú to prvočísla).

Avšak, na zistenie konkrétnej hodnoty $x \bmod q_i$ z rovnice $g^{x} \equiv F(1) \pmod{p}$ je potrebné vyriešiť **diskrétny logaritmus** v podskupine rádu $q_i$.  

Na tento účel využijeme algoritmus **Baby-Step Giant-Step (BSGS)**, ktorý efektívne nájde riešenie $x$ pre malé poradia skupín (napr. naše 32-bitové prvočísla).

BSGS je najefektívnejší všeobecný algoritmus na disk. logaritmus v takto malých moduloch a funguje aj v prípadoch, kde nie sú známe ďalšie slabiny skupiny či generátora. Pre každý faktor $q_i$ teda spočítame $x \bmod q_i$ pomocou BSGS a následne výsledné zvyšky spojíme Čínskou vetou o zvyškoch (CRT) do celkového $x$.



Hľadáme teda $x$ tak, že $g^x \equiv h \pmod{p}$.

Zvolíme $m = \lceil \sqrt{q} \rceil$.

$x$ sa dá zapísať ako $x = i m + j$, kde $0 \leq i, j < m$.

Potom:

$$
h \equiv g^{x} \equiv (g^m)^i \cdot g^j \pmod{p}
$$



Pre každý $j$ si vypočítame $S_j = g^j \pmod{p}$ ("baby steps").

Pre každý $i$ vypočítame $T_i = h \cdot (g^{-m})^i \pmod{p}$ ("giant steps").

Nájdeme $i, j$ také, že $T_i = S_j$. Potom riešenie je $x = i m + j$.

a $x$ je naše veľké celé číslo, ktoré ked prevedieme do hex hodnoty a tú prečítame ako ascii bajty, tak dostaneme vlajku. 

A tu je skript ktorý to celé urobí za nás



```python
import math

p = 24543926533640002647957367866857207914306117049983697556799269232027004353932658074554559267003250607939288726496967
g = 2078132001926017604748032590856030624252738363341625757437676864936624505324989739084558861915765841155338265586523
N = 314665724790256444204581639318682152747514321153637148164093195282397491717085359930186657269272443691529342647397

F1 = 2082453810845349954530857848803337496260456195444224420180316718294766405024576544871833258060845944088804345866959

primes = [
    2154506941,
    2321340949,
    2477438617,
    2598192473,
    2656632067,
    2661306983,
    2704495351,
    2704606529,
    3358863457,
    3439295149,
    3999681181,
    4090576319
]

# Baby-Step Giant-Step pre diskrétny log
def bsgs(g, h, p, order):
    m = int(math.isqrt(order)) + 1
    tbl = {pow(g, j, p): j for j in range(m)}
    factor = pow(g, (p-2)*m % (p-1), p)
    gamma = h
    for i in range(m):
        if gamma in tbl:
            return (i*m + tbl[gamma]) % order
        gamma = (gamma * factor) % p
    raise Exception("Diskrétny log sa nenašiel")

# Získanie x mod q pre všetky q 
residues = []
for q in primes:
    gq = pow(g, N // q, p)
    hq = pow(F1, N // q, p)
    xq = bsgs(gq, hq, p, q)
    residues.append(xq)

# Čínska veta o zvyškoch (CRT)
def crt(residues, moduli):
    x, M = 0, math.prod(moduli)
    for a, m in zip(residues, moduli):
        M_i = M // m
        inv = pow(M_i, -1, m)
        x = (x + a * M_i * inv) % M
    return x

x = crt(residues, primes)
print(f"x: \n{x}")
x_hex = hex(x)
print(f"x hex: \n{x_hex}")
print(f"x bytes: \n{' '.join(x_hex[i:i+2] for i in range(2, len(x_hex), 2))}")

# Vytvorenie vlajky
byte_len = (x.bit_length() + 7) // 8
flag = x.to_bytes(byte_len, "big").decode()
print(f"Vlajka: \n{flag}")


```

Výpis je

```
x: 
50078388732947606039010220039142339595603437895940133944323365620560182242304710998027717178846800980134745897341
x hex:
0x534b2d434552547b6d30623175355f316e7633723731306e5f31355f333435795f6630725f3376337279623064797d
x bytes:
53 4b 2d 43 45 52 54 7b 6d 30 62 31 75 35 5f 31 6e 76 33 72 37 31 30 6e 5f 31 35 5f 33 34 35 79 5f 66 30 72 5f 33 76 33 72 79 62 30 64 79 7d      
Vlajka:
SK-CERT{m0b1u5_1nv3r710n_15_345y_f0r_3v3ryb0dy}
```

Aj vlajka hovorí o použití mobiusa, ale žiaľ bolo prezradených viac informácií ako bolo potrebné na jeho použitie.



## Vlajka

```
SK-CERT{m0b1u5_1nv3r710n_15_345y_f0r_3v3ryb0dy}
```
