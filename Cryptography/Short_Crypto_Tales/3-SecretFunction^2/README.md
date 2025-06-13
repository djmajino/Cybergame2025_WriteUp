# Zadanie

EN: Legend has it that Gregory the Great—retired barista turned mad quaternion tinkerer—built a four-dimensional safe guarded by hyper-caffeinated squirrels and locked his secret croissant recipe inside a swirling mashup of a, b, c, and d raised to the 65537th power; now it’s up to you to brave his bamboozling “SecretFunction” arithmetic (u, v, and w included at no extra charge) and decrypt his espresso-fueled masterpiece.

SK: Povesť hovorí, že Gregory Veľký — bývalý barista, ktorý sa stal šialeným bádateľom kvaternionov — postavil štvordimenzionálny trezor strážený hyperkofeínovanými veverkami a uzamkol v ňom svoj tajný recept na croissant ako víriacu zmes premenných a, b, c a d. mocninu; teraz je na vás, aby ste sa odvážili čeliť jeho záhadnej aritmetike „SecretFunction“ a dešifrovať jeho espressom poháňané majstrovské dielo.

**Súbory:**

- main.py
- message.txt

## Riešenie

Ako už zadanie napovedá a rovnako aj obsah parametra `enc` v message.txt, ide o kvaternión, keďže je zapísaný v jeho fomráte $( a + b\mathbf{i} + c\mathbf{j} + d\mathbf{k})$. Viac na [Kvaternión – SK Wiki](https://sk.wikipedia.org/wiki/Kvaterni%C3%B3n)  alebo [Quaternion - EN Wiki](https://en.wikipedia.org/wiki/Quaternion).

Skript main.py robí t, že vytvorí z valjky, resp. z jej bajtov dlhé celé decimálne číslo, definuje exponent 65537 (0x10001), následne dve 4096 bitové prvočísla $p$ a $q$ sa modulus $n$ vytvorený ako súčin oboch prvočísel. Následne sa vytvorí sa premenná $R$, čo je "prstenec modulov" a všetky premenné následne vychádzajúce z $R$ budú len zvyšky po delení čísla x v R(x) čísom y v Zmod(y).

Príklad: 

> R = Zmod(7)    # teraz pracujeme so zvyškami po delení 7

Potom môžeme vytvárať "modulo 7 čísla" takto:

> a = R(10)      # 10 modulo 7 = 3
> b = R(13)      # 13 modulo 7 = 6

Keď s nimi počítame, výsledok je vždy modulo 7:

> print(a + b)   # (3 + 6) modulo 7 = 9 modulo 7 = 2
> print(a * b)   # (3 * 6) modulo 7 = 18 modulo 7 = 4
> print(a^3)     # (3^3) modulo 7 = 27 modulo 7 = 6

Toto sa budeteda diať zo všetkými premennými vychádzajúcimi z R, a toto je bežná praktika RSA.

Čo ale s tými kvaterniónmi?

Kvaternión, ako som už spomenul je štvorkomponentné číslo definované vzorcom $( a + b\mathbf{i} + c\mathbf{j} + d\mathbf{k})$. V kóde máme triedu `SecretFunction`, ktorá reprezentuje práve **kvaternión**, kde každá zložka (a, b, c, d) je číslo v zvyškovom okruhu `Zmod(n)`.  Každý výpočet so `SecretFunction` je vlastne výpočet s kvaterniónom **modulo n**.

V klasickom RSA sa šifrujú čísla (správy) ako bežné celé čísla modulo n. 

V našom zadaní je šifrovaná správa, vlajka, teda `enc` tvorená ako kvaternión. To znamená:

- že nie je zakódovaná ako obyčajné číslo, ale ako špeciálna kombinácia kvaterniónu.

- Potom je na ňu aplikovaná kvaterniónová mocnina (cez override `__pow__`, teda „umocni kvaternión na exponent e modulo n“).

Každý kvaternión v tomto kóde je štvorica čísel **modulo n**. Vieme s nimi sčítať, násobiť, umocňovať (všetko podľa špeciálnych pravidiel pre kvaternióny). Každá operácia v triede `SecretFunction` zabezpečí, že každá zložka zostane v `Zmod(n)` (teda vždy „po delení n“).

Čo robí kód zadania podľa toho ako je definované pow a pod je vysvetlené v nasledovnom príklade

```python
R = Zmod(7)  # R je "prstenec zvyškov po delení 7" (modulo 7 aritmetika)

q1 = SecretFunction(R(10), R(15), R(9), R(8))
# q1 = (10 % 7 = 3) + (15 % 7 = 1)·i + (9 % 7 = 2)·j + (8 % 7 = 1)·k
# q1 = (3 + 1·i + 2·j + 1·k)

q2 = SecretFunction(R(14), R(20), R(13), R(21))
# q2 = (14 % 7 = 0) + (20 % 7 = 6)·i + (13 % 7 = 6)·j + (21 % 7 = 0)·k
# q2 = (0 + 6·i + 6·j + 0·k)

q3 = q1 + q2
# q3 = (3+0, 1+6, 2+6, 1+0) modulo 7
#     = (3, 7, 8, 1) modulo 7
#     = (3, 0, 1, 1)

q4 = q1 * q2
# vypočítajme podľa pravidiel kvaterniónového násobenia, všetko modulo 7:

# a1, b1, c1, d1 = 3, 1, 2, 1
# a2, b2, c2, d2 = 0, 6, 6, 0

# new_a = a1*a2 - b1*b2 - c1*c2 - d1*d2
#        = 3*0 - 1*6 - 2*6 - 1*0
#        = 0 - 6 - 12 - 0 = -18 % 7 = (7* -3) + 3 = 3

# -18 // 7 = -3, zvyšok 3

# new_b = a1*b2 + b1*a2 + c1*d2 - d1*c2
#        = 3*6 + 1*0 + 2*0 - 1*6
#        = 18 + 0 + 0 - 6 = 12 % 7 = 5

# new_c = a1*c2 - b1*d2 + c1*a2 + d1*b2
#        = 3*6 - 1*0 + 2*0 + 1*6
#        = 18 - 0 + 0 + 6 = 24 % 7 = 3

# new_d = a1*d2 + b1*c2 - c1*b2 + d1*a2
#        = 3*0 + 1*6 - 2*6 + 1*0
#        = 0 + 6 - 12 + 0 = -6 % 7 = 1

# Výsledok:
# q4 = (3 + 5·i + 3·j + 1·k)

# zhrnutie premenných:
# q1 = (3 + 1·i + 2·j + 1·k)
# q2 = (0 + 6·i + 6·j + 0·k)
# q3 = (3 + 0·i + 1·j + 1·k)
# q4 = (3 + 5·i + 3·j + 1·k)

```

Teraz už vieme, ako sa správa kvaternión a ako fungujú operácie modulo n. Pozrime sa, čo sa deje pri samotnom šifrovaní vlajky v našej úlohe.

Vlajku máme teda ako jedno veľké číslo, napríklad text `"FLAG"` → bajty `[70, 76, 65, 71 ]` → číslo `70*256^3 + 76*256^2 + 65*256^1 + 71*256^0 = 1179402567`.

Povedzme si na príklade, že $p = 1179402571$, $q = 1179402677$,  $n = p * q$ teda bude $n = 1390990549498082567$, R bude teda prstenec čísel modulo 1390990549498082567. Z kódu 

```python
def MoreSecretFunction(mval, pval, qval):
    a = 1 * mval
    b = 3 * mval + 1 * pval + 337 * qval
    c = 3 * mval + 13 * pval + 37 * qval
    d = 7 * mval + 133 * pval + 7 * qval
    return SecretFunction(a, b, c, d)

enc = MoreSecretFunction(flag, p, q) ** e
```

sa vytvorí z týchto čísel a Secret function sa vytvorí kvaternión, kde mval je náš flag ako číslo (1390990549498082567), pval a qval sú naše prvočísla p a q, teda 1179402571 a 1179402677. Z týchto sa vytvorí prvý kvaternión s a,b,c,d 

- a = 1 * 1179402567= **1179402567**

- b = 3 * 1179402567+ 1 * 1179402571 + 337 * 1179402677 = 12830409 + 17 + 7751 = **402176312421**

- c = 3 * 1179402567+ 13 * 1179402571 + 37 * 1179402677 = 12830409 + 221 + 851 = **62508340173**

- d = 7 * 1179402567+ 133 * 1179402571 + 7 * 1179402677 = 29937621 + 2261 + 161 = **173372178651**

(1179402677, 402176312421, 62508340173, 173372178651) a funkcia vráti výsledok inicializácie triedy SecretFunction, čo bude na základe tohto kódu

```python
class SecretFunction:
    def __init__(self, a, b, c, d):
        self.a = R(a)
        self.b = R(b)
        self.c = R(c)
        self.d = R(d)
```

vlastne vyýsledok (vstup modulo n) a teda

```python
self.a = 1179402567   # R(a) = 1179402567/1390990549498082567 = 0, zvyšok 1179402567 
self.b = 402176312421 # R(b) = 402176312421/1390990549498082567 = 0, zvyčok 402176312421 
self.c = 62508340173  # R(c) = 62508340173/1390990549498082567 = 0, zvyšok 62508340173 
self.d = 173372178651 # R(d) = 173372178651/1390990549498082567 = 0, zvyšok 173372178651  
```

čiže 

```
enc = MoreSecretFunction(flag, p, q) ** e
enc = (1179402677, 402176312421, 62508340173, 173372178651) ** 65537
```

kde operátor `**` bude používať 

```python
def __pow__(self, exp):
    result = SecretFunction(1, 0, 0, 0)
    base = self # (1179402677 + 402176312421i + 62508340173j + 173372178651k)
    # 17 iterácií 2^16+1 = 65537 (2 na 16 a ešte 2/2)
    while exp > 0: #65537,32768,16384,8192,4096,2048,1024,512,256,128,64,32,16,8,4,2,1
        if exp % 2 == 1: # prvá a posledná iterácia iba
            result = result * base # (1,0,0,0)*(1179402677,402176312421,62508340173,173372178651)
        base = base * base # každá iterácia 
        exp //= 2 # floor division
    return result # (454567072040331097 + 123304733409285809*i + 323793788081250691*j + 339119907337011189*k)
```

Tu sa použije self ako sme spomenuli a následne sa inicializuje do resultu nový object SecretFunction s parametrami a,b,c,d = (1,0,0,0).

Výstup testovacieho 

```python
n = 1390990549498082567
e = 65537
enc (454567072040331097 + 123304733409285809*i + 323793788081250691*j + 339119907337011189*k)
```

Takto získaný kvaternión je šifrovaná verzia pôvodnej vlajky `FLAG` – dešifrovať ho bez znalosti súkromného kľúča (teda p a q) je veľmi ťažké, presne ako v klasickom RSA, len namiesto jedného čísla musíme „lúštiť“ štvoricu previazanú kvaterniónovou aritmetikou.

A prečo je to prelomiteľné? Pretože tento kvaternión je zostrojený lineárne z (flag, p, q) a všetky operácie prebiehajú “po zložkách modulo n”. Bežné RSA je bezpečné preto, lebo nepoznáme rýchly spôsob, ako z čísla $c = m^e \mod {n}$ dostať späť $m$ bez znalosti tajného rozkladu $n$. Ale tu je vlajka vložená do štyroch zložiek (kvaterniónu), z ktorých je každá lineárnou kombináciou vlajky a parametrov $p$, $q$.Tu je teda kvaternión zostrojený triviálne z vlajky, p a q. A vlajka je navyše nepriamo v prvej zložke kvaterniónu.

```python
a = 1 * flag
b = 3 * flag + 1 * p + 337 * q
c = 3 * flag + 13 * p + 37 * q
d = 7 * flag + 133 * p + 7 * q
```

Ako sme ukázali vyššie, všetky štyri zložky kvaterniónu po dešifrovaní sú **lineárnymi kombináciami** pôvodného flagu a parametrov $p$, $q$.  

Ak by sme poznali dešifrovaný kvaternión (čiže „kvaterniónovú odmocninu“), vieme z týchto hodnôt zostaviť systém rovníc a jednoducho ho riešiť – dostali by sme späť flag aj použité prvočísla.

No v skutočnosti (tak ako v bežnom RSA) máme k dispozícii iba šifrovaný kvaternión, teda jeho hodnoty po mocnení na verejný exponent $e$ modulo $n$. Zdalo by sa, že bez znalosti súkromného kľúča alebo rozkladu $n$ na $p$ a $q$ je systém bezpečný.  

**Avšak vďaka lineárnej závislosti vo vnútri kvaterniónu, vieme aj zo šifrovaných hodnôt zložiť ďalšie vzťahy a spätne dopočítať k pôvodným prvočíslam – a tým aj k vlajke!**

Kľúčovým krokom je uvedomiť si, že všetky tieto hodnoty sú previazané a preto sa dajú (pri dostatočne malom $n$ alebo „priateľskom“ zadaní) spätne vypočítať algebraickou manipuláciou.

 **Riešenie cez lineárnu sústavu a faktorizáciu***

Postup útoku je nasledovný:

1. **Získame jednotlivé členy kvaterniónu** zo šifrovanej správy (z message.txt).

2. **Spočítame vhodné pomery a parametre** pomocou inverzií modulo $n$ a prepočítame systém podľa známych vzorcov v zadaní.

3. **Získané čísla použijeme na faktorizáciu $n$** (gcd nám dá priamo pôvodné p alebo q).

4. **Zo získaných p, q dopočítame originálnu vlajku.**

Celý útok vieme zautomatizovať v krátkom skripte, ktorý priamo pracuje so šifrovaným kvaterniónom – ukážková implementácia nižšie:

```python
import re, math, sys, time 

t0 = time.perf_counter()

n  = 1390990549498082567
e  = 65537
enc_repr = r'''
(454567072040331097 + 123304733409285809*i + 323793788081250691*j + 339119907337011189*k)
'''

def modinv(a, m):                 # pomocná inverzia
    return pow(a, -1, m)

# 1) koeficienty kvaternionu 
coeffs = list(map(int, re.findall(r'([+-]?\d+)\s*\*?[ijkk]?', enc_repr)))
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
# 5) získanie pôvodnej správy 
m_inv_mod_q = (P0 % q) * modinv(p % q, q) % q
m           = modinv(m_inv_mod_q, q)
flag_bytes  = m.to_bytes((m.bit_length()+7)//8, 'big')

elapsed = time.perf_counter() - t0
print(f"Duration: {elapsed:.3f} s  \nFlag:     {flag_bytes.decode()}")
```

a vrátil

```
p =  1179402571
q =  1179402677
Duration: 0.001 s  
Flag:     FLAG
```

Tento postup demonštruje, že šifrovanie založené na takejto naivnej kombinácii kvaterniónov s lineárnymi vzťahmi nezvyšuje bezpečnosť nad rámec obyčajného RSA. Naopak, kvôli možnosti využiť viac informácií z viacerých zložiek je systém často **jednoduchšie prelomiteľný algebraicky**.



Finálny skript pre zadanie tohto challengu je 

```python
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
```

a jeho v ýstup bude

```
p =  1008396132902608605606488038251539778723369238572517114443643521908501724871028123914544082806601178329330311066314464780923943462745775287746421475606978419973139841837742629421299736236105231532761004171441367176298479292019802911732912709751269910731049887045804604909916317255121015368016358007341464581253599898320514965941027907987360094012157718759687710419797143702582953723388638033901423750741812823266550457932849501338543767892519827261480905870846315972553285101053829519362279545193197789422077558447407687795964545536309236884548359789804341658243911246439787668184137399097488784264076959278204466766177850791969750745237513365117075532057650624568053667765726613401055277527754251667819006672485259989539720803341954078868978504658353704995196403888830453084720437206213271803774747019740088990603136976557436316664532003506485399837918120334558266915261342376267070315103746549673017390325545834904437117823462878978721458378280150993428398254255924462886771376415034786749105441668085683351627392592293848379962610472527425193956746766996953425614435894391759192387611237241381188866623482070440244901378305682715892677873750575751850634351555762462050504387348162442822832071107470660504802749275406547960830859279
q =  999910680228688294358585717194472090313749974370618578228911149522744488055092352406278820127977624734992260005304138495275507572818003464470868120313851761759379612059787824241029248367538721493785489928399199086097012087229971559946194778917369743515393473686245028397994163687104818933529734366051379449656603208262786121832625125059265062524090915072517002579720533568648429055228749320017904509425650024604205942171118563127642765575666862245218158546646531366934255893065614892135611785832937791545045157982071250634670357767103171029593955119393612089646552019627880624916453516361589717129894903348148773844616110679772427318634804920837283621782900797717663330774376591462660803522594845600605016030060617563428283192584895058805766292956253473686281091184785928510519872410811266724291363964848795357068425557556132531556549747627240018722487024041186783732486518047640505829449750000572706115815002910713069564567330143401452422715494679298264037491491527011822114457159065493214562934300637305645313290201244126492397486796604604110451336275250633905108294664301914633412602118098732900167292553538901262305960745539631985665589452212375046523914506927615133267072810047196963017443697519794480563429914197641833456995987
Duration: 0.025 s  
Flag:     SK-CERT{RSA_w17h_u54g3_0f_qu473rn10n5}
```

V podstate úloha podobná až rovnaká ako z write-upu [RSA 4.0 | 7Rocky](https://7rocky.github.io/en/ctf/other/seccon-ctf/rsa-4.0/)



## Vlajka

```
SK-CERT{RSA_w17h_u54g3_0f_qu473rn10n5}
```
