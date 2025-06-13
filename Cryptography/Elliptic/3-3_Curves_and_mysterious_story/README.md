# Zadanie

EN: We have discovered an intergalactic server that asks for some data and, in exchange, returns more data—but encrypted. Check the source code and try to decrypt the mysterious message.

SK: Objavili sme medzihviezdny server, ktorý žiada určité údaje a na oplátku vráti ďalšie údaje — ale zašifrované. Prezri si zdrojový kód a pokús sa dešifrovať tajomnú správu.

`exp.cybergame.sk:7006`

**Súbory:**

- server.py

```python
import socketserver
import random
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def modinv(a, p):
    return pow(a, p - 2, p)

class EllipticCurve:
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b

    def is_on_curve(self, x, y):
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def point(self, x, y):
        if not self.is_on_curve(x, y):
            raise ValueError("The point is not on the curve.")
        return ECPoint(x, y, self)

    def infinity(self):
        return ECPoint(None, None, self)

class ECPoint:
    def __init__(self, x, y, curve):
        self.x = x
        self.y = y
        self.curve = curve

    def is_infinity(self):
        return self.x is None and self.y is None

    def __neg__(self):
        if self.is_infinity():
            return self
        return ECPoint(self.x, (-self.y) % self.curve.p, self.curve)

    def __add__(self, other):
        if self.curve != other.curve:
            raise ValueError("Can't add points on different curves.")
        p = self.curve.p

        if self.is_infinity():
            return other
        if other.is_infinity():
            return self

        if self.x == other.x:
            if (self.y - other.y) % p == 0:
                if self.y == 0:
                    return self.curve.infinity()
                m = (3 * self.x * self.x + self.curve.a) * modinv(2 * self.y, p)
            else:
                return self.curve.infinity()
        else:
            m = (other.y - self.y) * modinv(other.x - self.x, p)

        m %= p
        x3 = (m * m - self.x - other.x) % p
        y3 = (m * (self.x - x3) - self.y) % p
        return ECPoint(x3, y3, self.curve)

    def __rmul__(self, n):
        result = self.curve.infinity()
        addend = self
        while n:
            if n & 1:
                result = result + addend
            addend = addend + addend
            n //= 2
        return result

    def __str__(self):
        if self.is_infinity():
            return "Infinity"
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.curve == other.curve

E1 = EllipticCurve(
    p=221967046828044394711140236713523917903,
    a=65658963385979676651840182697743045469,
    b=84983839731806025530466837176590714802
)

E2 = EllipticCurve(
    p=304976163582561072712882643919358657903,
    a=178942576641362013096198577367493407586,
    b=135070218427063732846149197221737213566
)

E3 = EllipticCurve(
    p=260513061321772526368859868673058683903,
    a=125788353697851741353605717637937028517,
    b=206616519683095875870469145870134340888
)

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            self.request.sendall(b"Welcome to ECC Oracle!\n")
            self.request.sendall(b"Send g.x:\n")
            gx = int(self.request.recv(4096).strip())

            self.request.sendall(b"Send g.y:\n")
            gy = int(self.request.recv(4096).strip())

            G1 = E1.point(gx, gy)
            G2 = E2.point(gx, gy)
            G3 = E3.point(gx, gy)

            # generate private key
            d = random.randint(
                221967046828044394694688089238337659792,
                440883567264567553887820221359293838912320528316331486261350931519268084925699580001476273968159118924129968558327
            )

            Q1 = d * G1
            Q2 = d * G2
            Q3 = d * G3

            self.request.sendall(b"\nQ1 = " + str(Q1).encode() + b"\n")
            self.request.sendall(b"Q2 = " + str(Q2).encode() + b"\n")
            self.request.sendall(b"Q3 = " + str(Q3).encode() + b"\n")

            with open("story.txt", "rb") as f:
                data = f.read()

            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()
            iv = 16 * b'\x00'
            key = hashlib.sha256(str(d).encode()).digest()

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

            self.request.sendall(b"\nEncrypted story:\n")
            self.request.sendall(encrypted_data + b"\n")
        except Exception as e:
            self.request.sendall(b"Error: " + str(e).encode() + b"\n")

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 11337
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as server:
        print(f"[+] Server listening on {HOST}:{PORT}")
        server.serve_forever()
```

## Riešenie

V prvom rade server od nás očakáva nájdenie spoločného bodu na všetkých troch krivkách. 

Máme tri rôzne eliptické krivky definované rovnicami:

- $E_1$: $y^2 \equiv x^3 + a_1x + b_1 \mod p_1$
- $E_2$: $y^2 \equiv x^3 + a_2x + b_2 \mod p_2$
- $E_3$: $y^2 \equiv x^3 + a_3x + b_3 \mod p_3$

Chceme nájsť jeden bod ($gx, gy$), ktorý bude platný pre všetky tri krivky súčasne.

Najčastejšia chyba je predpoklad, že rovnaké \( $gy$ \) platí pre všetky krivky modulo rôzne prvočísla. V praxi je však takéto riešenie takmer nemožné priamo nájsť.

Správny postup bude:

1. Nájdeme jedno spoločné \( $gx$ \), ktoré vyhovuje všetkým trom krivkám naraz. To znamená:
   
   - $(gx^3 + a_ix + b_i)$ musí byť kvadratický zvyšok modulo každé $(p_i)$.

2. **Pre každú krivku zvlášť** vyriešime rovnicu a nájdeme individuálne $( gy_i )$ modulo $( p_i )$:
   
   $[
   gy_1^2 \equiv gx^3 + a_1 gx + b_1 \mod p_1\\
   gy_2^2 \equiv gx^3 + a_2 gx + b_2 \mod p_2\\
   gy_3^2 \equiv gx^3 + a_3 gx + b_3 \mod p_3
   ]$
   
   Dostaneme teda rôzne hodnoty $( gy_i \mod p_i )$.

3. Použijeme **Čínsku vetu o zvyškoch (CRT)** na spojenie týchto troch rôznych kongruencií do jedného veľkého čísla $( gy )$:
   
   $[
   gy \equiv gy_1 \mod p_1 \\
   gy \equiv gy_2 \mod p_2 \\
   gy \equiv gy_3 \mod p_3
   ]$
   
   Výsledné číslo $( gy )$ automaticky spĺňa všetky tri rovnice samostatne.

Server prijíma jedno číslo $( gy )$, ale pri overení bodu ho v metóde `is_on_curve` redukuje modulo každé prvočíslo $( p_1, p_2, p_3 )$ samostatne. Ak náš bod $(gx, gy)$ spĺňa rovnice modulo každé prvočíslo zvlášť, server ho považuje za platný.

CRT teda umožní vytvoriť jedno celočíselné \( gy \), ktoré naraz vyhovuje všetkým krivkám.

```python
p1 = 221967046828044394711140236713523917903
a1 = 65658963385979676651840182697743045469
b1 = 84983839731806025530466837176590714802

p2 = 304976163582561072712882643919358657903
a2 = 178942576641362013096198577367493407586
b2 = 135070218427063732846149197221737213566

p3 = 260513061321772526368859868673058683903
a3 = 125788353697851741353605717637937028517
b3 = 206616519683095875870469145870134340888

print("[*] Hľadám gx také, aby y^2 = gx^3 + a*gx + b malo riešenie na všetkých 3 krivkách...")

found_gx = None
found_gy = None
search_limit = 1000 

R1 = GF(p1)
R2 = GF(p2)
R3 = GF(p3)

# Iterujme cez 0, 1, -1, 2, -2, ...
for i in range(search_limit + 1):
    gx_candidates = [i] if i == 0 else [i, -i]

    for gx in gx_candidates:
        print(f"[*] Skúšam gx = {gx}...")

        try:
            rhs1 = R1(gx^3 + a1*gx + b1)
            rhs2 = R2(gx^3 + a2*gx + b2)
            rhs3 = R3(gx^3 + a3*gx + b3)

            if rhs1.is_square() and rhs2.is_square() and rhs3.is_square():
                print(f"[+] Nájdené vhodné gx = {gx}!")

                # Vypočítaj modulárne odmocniny
                y1_mod = rhs1.sqrt()
                y2_mod = rhs2.sqrt()
                y3_mod = rhs3.sqrt()

                # Konvertuj na celé čísla
                y1 = Integer(y1_mod)
                y2 = Integer(y2_mod)
                y3 = Integer(y3_mod)
                print(f"    sqrt(rhs1) mod p1 = {y1}")
                print(f"    sqrt(rhs2) mod p2 = {y2}")
                print(f"    sqrt(rhs3) mod p3 = {y3}")

                # Vyrieš systém pomocou CRT
                print(f"[*] Riešim systém pomocou CRT...")
                gy = crt([y1, y2, y3], [p1, p2, p3])

                found_gx = gx
                found_gy = gy
                break

        except Exception as e:
             print(f"    Chyba pri spracovaní gx = {gx}: {e}")
             continue

    if found_gx is not None:
        break 

if found_gx is not None:
    print(f"\n[+] Nájdené súradnice spoločného bodu:")
    print(f"    gx = {found_gx}")
    print(f"    gy = {found_gy}")

    print(f"\n[*] Overujem, či bod ({found_gx}, {found_gy}) leží na krivkách:")
    # Overenie pre E1
    on_E1 = mod(found_gy^2 - (found_gx^3 + a1*found_gx + b1), p1) == 0
    print(f"    Leží bod na E1? {on_E1}")
    # Overenie pre E2
    on_E2 = mod(found_gy^2 - (found_gx^3 + a2*found_gx + b2), p2) == 0
    print(f"    Leží bod na E2? {on_E2}")
    # Overenie pre E3
    on_E3 = mod(found_gy^2 - (found_gx^3 + a3*found_gx + b3), p3) == 0
    print(f"    Leží bod na E3? {on_E3}")

    if on_E1 and on_E2 and on_E3:
        print("[+] Overenie úspešné! Bod leží na všetkých troch krivkách.")
    else:
        print("[!] Chyba pri overení! Bod neleží na všetkých krivkách.")

else:
    print(f"\n[-] Nepodarilo sa nájsť vhodné gx v rozsahu +/- {search_limit}. Skúste zvýšiť limit.")
```

Výstup

```
[*] Hľadám gx také, aby y^2 = gx^3 + a*gx + b malo riešenie na všetkých 3 krivkách...
[*] Skúšam gx = 0...
[*] Skúšam gx = 1...
[*] Skúšam gx = -1...
[*] Skúšam gx = 2...
[*] Skúšam gx = -2...
[*] Skúšam gx = 3...
[*] Skúšam gx = -3...
[*] Skúšam gx = 4...
[*] Skúšam gx = -4...
[*] Skúšam gx = 5...
[*] Skúšam gx = -5...
[*] Skúšam gx = 6...
[*] Skúšam gx = -6...
[*] Skúšam gx = 7...
[*] Skúšam gx = -7...
[+] Nájdené vhodné gx = -7!
    sqrt(rhs1) mod p1 = 33025163115158898951954645693372101644
    sqrt(rhs2) mod p2 = 74596626100075397661628643936840548267
    sqrt(rhs3) mod p3 = 57172619184139184230226382358761294942
[*] Riešim systém pomocou CRT...

[+] Nájdené súradnice spoločného bodu:
    gx = -7
    gy = 14237250164363126969941140956358110912307455709874902630137533835473431931449667831487843998409359162292278539447234

[*] Overujem, či bod (-7, 14237250164363126969941140956358110912307455709874902630137533835473431931449667831487843998409359162292278539447234) leží na krivkách:
    Leží bod na E1? True
    Leží bod na E2? True
    Leží bod na E3? True
[+] Overenie úspešné! Bod leží na všetkých troch krivkách.
```

Máme bod, čo sa stane, keď ho zadám do konzoly?

```
Welcome to ECC Oracle!
Send g.x:
-7
Send g.y:
14237250164363126969941140956358110912307455709874902630137533835473431931449667831487843998409359162292278539447234

Q1 = (155700317780840675350070137808059974317, 160313857065874230305603415079143967649)
Q2 = (178575922192834984711956628717974384702, 156691469558702089065797861307582457666)
Q3 = (45491693492227718170290645719686509634, 222526968046165393713223283436711289961)

Encrypted story:
êÇ♥ÕÆµf2«öa‼♫┤↓\[äÔ¼TÉ]N@|ø#¶l<▄¶¤DEþ§mgKÎ¶ÉQ▒]xN╬Õ`-a▓½╗Í♫»┬ÈPì.}È$HYlÍ°»▀ÑÚ¡}ÜAÅ¦Üßõû←U┼Z(õÏ▀j¼ûI3vÖH¬Ë½tÜq²h{C▼py½v¹[→c╠T¡®▒┐eC@µ▼»:vøW♀çFïc Î¶ ³J
íÙ­Î6Ô:ÚÛ4`╝¶.Á¹}▬└┴Øñ╦?q\GÖ"   ")n■¹Ã[ÓD­«(Ãh3ƒ↕vé¿Ð¦Î0Dml▒=&ï#¼<pz}qä²┤>Äò`&¤à╩▲7█w9█¥),Ö¤▓J▄▀ñ┴¡↑ücê?u←¨Ð£~áì∟ãa¥▓/Õ⌂D80╬┴┬KÍA"
5;A▄>¯♠õ¦◄←ÁÙ&)Øµ§Õ▓Y¾→>ì├Ìµ©<└)?}¯¸♀7TÇ╩Àòg∟" ¤G╣pÞí:É5=←'_ ­êºÓ∟¶9¿½BÇI'Í¶a¨¬)·¹Ðá÷`ó¥1ªtMÉb
}║◄ªj⌂ùu┐úÀ╣Í┤A↕1x▓╣◄╦?ç├(¶?X_øï♂ºnýìxÎl‗H&ê↑1ððe¥iı→~+{ñ§ÄÀoaýX┤@èí¤&ƒ┬çÜ+\‼ÚïÉ{/ÀúéÞ·:■╬¶@    }■Ì©G
Î%ã▼×6¶ï$S═jøV▄ÿ@{»YàÇ┤´IP▒ªö&♥z@∟¸w▬Óó0f_ì‼¡→Ì-ÄR:n`RÈa*A*n¹}├½(V¹┌Á­hý5ú?Ù}ÔH╚█BmíãKÞ▼↑JQ Y-▄─uîÄÔÔ`Âs&7┴⌂à¹o▲1´╣o┬ÝüW§¬!☺Iá|°‼Pí!;?■ıá^{▒¢M=eúDO╩´×↨Ý6x½*» pý
âÔñÎî®ß ☻£`):2l↔└*n‼Z<~♠iÂâ↕─g¶År@¢jÐ§♠×¡Y~ÏPÿÞ¼S4i‗Pß×*╣*H┼╠ùÃ▓¾#i¤c^:©└+☼:Þ+»9âãBÛ═æ¼õ?¦-'äoÔÚÞ¡»À×─¹☻½ð3ª┼ï6eDX[Þm»ç6ávûvAÒ¼¡Ø◄♠.ü_←ÓSƒ]«÷
Ùw♦f4ÖÓjÛj∟8û~Óo±Ö
╦/ÏBjô(9ù☻║:©ý¹n♠³"q²VX Ø■¬  <PÂ¢Ë■½←←V>0IµØ∟¨£Yo9G☺®§êÓ♫[Ê,â♠‼♣X±ß⌂H¿v¸┐→↨©üe/îÌ»fÇEQ┴↓N‼Ù♣é╠¹▄♣Hñ·&/(┘:
↨ı╦w◄o♣☼Øï>Jì¥»N÷>2Ô┬\ã¶2¶¢╗╬Í╣Ç╦╚qÐ_cde↑ª⌂·m‼äñ,ÙÐƒö╩s█ûAiÏpp↔¥Ûª³▼0Ôì¶█['÷═½RÈ2îIëÈÑ¬ª¦­R;ö|öf▲♂V─it"À☺ucr╠►ê##.Î═Êj☻f!¸éÀ@-\åƒÅâ→Å╠+C
☺╠K¡╣;(êÿÇRÏçûU═+wv^³Æ~â§█╝lD├î↓Ó,ÒÔîð▲­u¯Ë]ÂÞh[ÚÁÍúø´èötZú╦┴u  Y       a╬j>Äy/←▓ÿÇ│f=øÃa¯K▄]‗ð█_âÙË¥Ù5↓╬Tg▀n╗♂ı:♠b**ÌìÛI☻ÂÙ∟Ìãá▀¹"acö6N$ò↨Î¬Ñaó        ½▲`ÇÈ┼V&jXS6ú‗Ç¶╔z☺[}í6¶0P]f│ñ╩9À¨%¸ÐAËÇ╗jG▓c╣┬‗Æ»♫├'Ó↨C↓w°ëæÊAßıÛö┴_§┤┼ÔÒ'ãôÐO¸)[ │Cï╗%↑²+▲2B#àÀ┼´'Ý        R╝Þ‼_Þ¾█É­ù³ZC↕÷*╦på‗­N·ar┌·├(Ï╬÷aÞ£þ6╩äh8◄♥ZZð÷÷ı─TH]VPÿù$Ld   ºÌ7É⌂«♥þ♥¬2KË▄Á6▒╦eñëõkß▒í╩W«IÝá² X­ÛM▼ı▒©h╝¥kFØ2 Cõ¨î╣I┼1=~ıjz¨┼Í ╩á_ÿf"I♂ÀMç¡À±Hq~#═²Ê$J]♣"áæ←\ÒÀ©┘Ï▲☻@¾u§`<^\þ←#Ì4Ü4ºJ=▀°J Z↓╩®¶
05JmR±ð0°÷2õ┤¡wú☻ç¶2─¶♥↔§┴♥^­L.░-╬OKz>ó▄0Âe9çd☼Y.ùå♥Ó¶OE?↓Dıj»┐╣hz;á¾³╩æH¾mé┬ú'­W×ÜÚ.
¥¶ûYì♠╦Fú♂ðèón9"Ç↕-╠,±∟hcÖòÓMOÈQS◄‗╦Ó▬e┼▄Ù½▀Z¢ã▒²)6♥©c‼Ët©-♣±ª┐'¤e±☺┤░☻}^lïÝ4ò∟Æ♠6♫╚▒h▒Ôá¶¯?FÏ§Õ┘S!k╝z╠hIQÁbì"»þ]¼ºt>FT_ûNX¯iâm¢♂U↕"╬ì<Z[W↔·☻,ï☺¡↕ù¬☻l#¹┬▀ƒAzl╝dsÅ▲T{‗d♠º¦¡ø8
☻═♣¢└³´¥.ï+q♠-☻v$▒÷{nÝ▼â┌pïyÓË└→É7ÇÇ↓¾Û>Ü←‗Ú¶▓ƒpßØLRdÆÄ♫$Ð→Ì'uÃı¶‗Q│ ­*ò╗X▀┤9▓═æ¹òF±♥☺ Ýı▄│_H▄Ä\lds¶▬╝E║└¾µÏA┼óeC¸↓£à&*¥È▲â)úµ5 ∟à«½¡×CêvM▬┼ïó
*Ê¶6¡©áU2Ù┐~╦¦µeƒ┘↔╠A ♀k▄╣øzg.CèEƒWD¤1á↕8┤Ôh▲fÌ§ò·g%♂qy4‼◄È}+A³é| Í2M
```

OK, takže bod sme našli a server nám poslal zašifrovaný obsah súboru `story.txt` pomocou privátneho kľúča, ktorý síce nepoznám, ale spolu s tou zašifrovanou správou poslal aj hodnoty $Q1,Q2,Q3$, ktoré sú výsledkom násobenia mnou zadaného bodu $(gx,gy)$ privátnym kľúčom $d$, ktorý sa vegeroval hneď po overení, čo mnou zadaný bod leží na všetkých krivkách.

Našou úlohou je získat privátny kľúč, vieme, že $Q1,Q2,Q3$ sú výsledok násobenia privátneho kľúča bod, ktorý sme my zadali. To čo nám server poskytol je ECC Oracle, ktoré vieme použiť na získanie privátneho kľúča. Ide o tzv. Elliptic Curve Discrete Logarithm Problem (ECDLP).

Pre overenie lokálne mám skript, ktorý mi odchytí  body Q a zašifrovanú správu, ktorú si uloží spolu s logom obsahujúcim body Q.

```python
import socket

HOST = "exp.cybergame.sk"
PORT = 7006
SOCKET_TIMEOUT = 10

def recv_until(sock, suffix):
    sock.settimeout(SOCKET_TIMEOUT)
    message = ""
    try:
        while not message.endswith(suffix):
            chunk = sock.recv(4096).decode("utf-8", errors="ignore")
            if not chunk:
                raise ConnectionAbortedError(
                    f"Server zatvoril spojenie počas čakania na '{suffix}'"
                )
            message += chunk
    except socket.timeout:
        raise TimeoutError(
            f"Timeout pri čakaní na '{suffix}'. Prijaté doteraz: '{message[:100]}...'"
        )
    except OSError as e:
        raise ConnectionAbortedError(f"Chyba socketu pri čakaní na '{suffix}': {e}")
    finally:
        sock.settimeout(None)
    return message

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print("[*] Spojenie so serverom nadviazané.")
    _ = recv_until(sock, "Send g.x:\n")
    sock.sendall(b"-7")
    _ = recv_until(sock, "Send g.y:\n")

    sock.sendall(b"14237250164363126969941140956358110912307455709874902630137533835473431931449667831487843998409359162292278539447234")
    full_output = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            full_output += chunk
        except socket.timeout:
            break

    with open('out.txt', 'wb') as file:
        file.write(full_output)

    # Extrakcia iba binárnych dát po hlavičke "Encrypted story:\n"
    if b"Encrypted story:\n" in full_output:
        _, binary_part = full_output.split(b"Encrypted story:\n", 1)

        with open("encrypted_data.bin", "wb") as f:
            f.write(binary_part.rstrip(b"\n"))
        print("[+] Binárne dáta uložené do 'encrypted_data.bin'")
    else:
        print("[!] Nenájdený blok 'Encrypted story:'")
```

Dostal som

```
Q1 = (26908861571403341412473949299561352742, 197024398250164802957847102700086734108)
Q2 = (38319172151600687065475480781488739737, 143035947817333620216699764350781136798)
Q3 = (186134293088159885373873349330981932520, 141762516966866597030833226375179491090)
```

a encrypted_data.bin...

Sage skript

```python
# --- Definície parametrov kriviek ---
p1 = 221967046828044394711140236713523917903
a1 = 65658963385979676651840182697743045469
b1 = 84983839731806025530466837176590714802
E1 = EllipticCurve(GF(p1), [a1, b1])

p2 = 304976163582561072712882643919358657903
a2 = 178942576641362013096198577367493407586
b2 = 135070218427063732846149197221737213566
E2 = EllipticCurve(GF(p2), [a2, b2])

p3 = 260513061321772526368859868673058683903
a3 = 125788353697851741353605717637937028517
b3 = 206616519683095875870469145870134340888
E3 = EllipticCurve(GF(p3), [a3, b3])

# --- Vstupné hodnoty (z vášho nc výstupu) ---
gx = -7
# Skopírujte presnú hodnotu gy, ktorú ste poslali serveru
gy = 14237250164363126969941140956358110912307455709874902630137533835473431931449667831487843998409359162292278539447234

# Skopírujte presné súradnice Q1, Q2, Q3
Q1x = 26908861571403341412473949299561352742
Q1y = 197024398250164802957847102700086734108

Q2x = 38319172151600687065475480781488739737
Q2y = 143035947817333620216699764350781136798

Q3x = 186134293088159885373873349330981932520
Q3y = 141762516966866597030833226375179491090

# --- Vytvorenie bodov v SageMath ---
try:
    G1 = E1(gx, gy % p1) # Použijeme gy modulo p pre každú krivku
    G2 = E2(gx, gy % p2)
    G3 = E3(gx, gy % p3)

    Q1 = E1(Q1x, Q1y)
    Q2 = E2(Q2x, Q2y)
    Q3 = E3(Q3x, Q3y)
    print("[+] Body G1, G2, G3, Q1, Q2, Q3 úspešne vytvorené.")
except Exception as e:
    print(f"[!] Chyba pri vytváraní bodov: {e}")
    exit()

# --- Výpočet rádov bodov G ---
try:
    print("[*] Počítam rády bodov G1, G2, G3...")
    n1 = G1.order()
    n2 = G2.order()
    n3 = G3.order()
    print(f"    Rád G1 (n1) = {n1}")
    print(f"    Rád G2 (n2) = {n2}")
    print(f"    Rád G3 (n3) = {n3}")
    # Voliteľné: Zobrazenie faktorizácie rádov
    # print(f"    Faktory n1: {n1.factor()}")
    # print(f"    Faktory n2: {n2.factor()}")
    # print(f"    Faktory n3: {n3.factor()}")
except Exception as e:
    print(f"[!] Chyba pri výpočte rádov: {e}")
    exit()

# --- Riešenie ECDLP pre každú krivku ---
# (Toto môže trvať dlhšie, ak rády nie sú dostatočne hladké)
try:
    print("[*] Počítam diskrétne logaritmy (d mod n_i)...")
    # Timeout môžeme pridať ako discrete_log(Q1, include_algorithm=False, operation='+') # starší syntax
    # V novších verziách Sage sa timeout priamo nepodporuje v discrete_log
    d1 = G1.discrete_log(Q1)
    print(f"    d mod n1 = {d1}")
    d2 = G2.discrete_log(Q2)
    print(f"    d mod n2 = {d2}")
    d3 = G3.discrete_log(Q3)
    print(f"    d mod n3 = {d3}")
except Exception as e:
    print(f"[!] Chyba pri výpočte diskrétneho logaritmu: {e}")
    print(f"[!] Pravdepodobne rád niektorého bodu nie je dostatočne hladký pre použité algoritmy.")
    exit()

# --- Kombinácia výsledkov pomocou CRT ---
try:
    print("[*] Kombinujem výsledky pomocou CRT...")
    # Získame d modulo lcm(n1, n2, n3)
    d_solution = crt([d1, d2, d3], [n1, n2, n3])
    print(f"\n[+] Možné riešenie pre d (modulo lcm(n1, n2, n3)):")
    print(f"    d = {d_solution}")

    # --- Overenie rozsahu d (voliteľné, ale odporúčané) ---
    d_min = 221967046828044394694688089238337659792
    d_max = 440883567264567553887820221359293838912320528316331486261350931519268084925699580001476273968159118924129968558327

    if d_min <= d_solution <= d_max:
        print("[+] Nájdene d je v očakávanom rozsahu!")
    else:
        print("[!] Upozornenie: Nájdene d NIE JE v pôvodnom rozsahu generovania.")
        # V tomto prípade by mohlo byť správne d = d_solution + k*lcm(n1,n2,n3)
        # Ale najpravdepodobnejšie je, že d_solution je správne d.
        print(f"    Pôvodný rozsah: [{d_min}, {d_max}]")

except Exception as e:
    print(f"[!] Chyba pri CRT alebo overení rozsahu: {e}")
```

Výstup

```
[+] Body G1, G2, G3, Q1, Q2, Q3 úspešne vytvorené.
[*] Počítam rády bodov G1, G2, G3...
    Rád G1 (n1) = 221967046828044394694688089238337659791
    Rád G2 (n2) = 304976163582561072724319063824010449966
    Rád G3 (n3) = 130256530660886263176425017554070029590
[*] Počítam diskrétne logaritmy (d mod n_i)...
    d mod n1 = 137801383649546415038323419401056624131
    d mod n2 = 36059447791986031365680397379433688289
    d mod n3 = 92081727378585183717770102771881681899
[*] Kombinujem výsledky pomocou CRT...

[+] Možné riešenie pre d (modulo lcm(n1, n2, n3)):
    d = 378136300158671525735798351876422983478838101778694338718304033442768193120234120690113969074520321091131147583509
[+] Nájdene d je v očakávanom rozsahu!
```

Idem použiť vyrátaný kľúč na dešifrovanie správy.

```python
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

d = 378136300158671525735798351876422983478838101778694338718304033442768193120234120690113969074520321091131147583509

# --- Výpočet AES kľúča ---
try:
    key = hashlib.sha256(str(d).encode()).digest()
    print(f"[*] AES kľúč (hash d): {key.hex()}")
except Exception as e:
    print(f"[!] Chyba pri výpočte kľúča: {e}")
    exit()

# --- Načítanie zašifrovaných dát zo súboru ---
try:
    with open('encrypted_data.bin', 'rb') as f:
        encrypted_data = f.read()
    print(f"[*] Načítaných {len(encrypted_data)} bytov zašifrovaných dát.")
except Exception as e:
    print(f"[!] Chyba pri načítaní súboru: {e}")
    exit()

# --- Dešifrovanie ---
try:
    iv = 16 * b'\x00'  # IV je pevne daný v serverovom kóde

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    print(f"[*] Dešifrované dáta (s paddingom): {padded_data}")

    # --- Odstránenie paddingu ---
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    # --- Výsledný príbeh ---
    print("\n[+] Dešifrovaný príbeh:")
    try:
        print(data.decode('utf-8'))
    except UnicodeDecodeError:
        print(f"(Nedá sa dekódovať ako UTF-8, zobrazujem raw byty):")
        print(data)

except Exception as e:
    print(f"[!] Chyba pri dešifrovaní alebo odstránení paddingu: {e}")
```

Výstup:

```
[*] AES kľúč (hash d): 50c8691d8c2b873ed08d90caf9d47944f47d94313efd6453f6e4a9638c704bbe
[*] Načítaných 2912 bytov zašifrovaných dát.

[+] Dešifrovaný príbeh:
“Squirrels, Secrets, and Szechuan Schemes”

It all started on a Tuesday—because weird stuff always starts on Tuesdays. Morty had just gotten out of gym class and was still wearing his Rick and 
Morty™ brand sweatband when Rick burst through a wormhole, soaking wet and carrying a squirrel in a tiny mech suit.

“Morty! Get in the garage, now! We’ve got a code Omega-Nut situation!” Rick barked, flinging the squirrel into a reinforced hamster ball with laser turrets.

Morty blinked. “W-wait, Rick, why are you soaking wet and carrying a rodent in battle armor?!”

Rick took a swig from a flask labeled “Neural Blocker + Mango,” then belched. “It’s not just a rodent, Morty. Squirrels run one of the oldest shadow 
governments in the multiverse. They're the Illuminati, the Bilderbergs, the deep-fried state—all rolled into one, fur-covered nut-hoarding network.” 

Morty squinted. “Wait… didn’t we already get in trouble with squirrels once?”

“Yeah, and we skipped timelines to avoid them. Guess what? They figured it out. Turns out hyper-intelligent squirrels have quantum acorn tracking. Now they’re back, and this one,” Rick tapped the mech-ball, “is the Secretary of Disinformation. He tried to sneak into my lab disguised as a DoorDash 
driver. Big mistake.”

As Rick disassembled the mech suit to reverse-engineer its cloaking tech, the squirrel squeaked something unintelligible.

Morty leaned in. “What’s he saying?”

Rick smirked. “He says the Nutwork—that’s their internal name for it, not joking—is planning a Neur-Acornal reset. Basically, they control global finance, social media, and squirrels at every bird feeder. And they’ve infiltrated every timeline but ours… until now.”

Suddenly, dozens of squirrels in tactical gear dropped from the ceiling tiles. “Squeak squeak mutiny!” the leader yelled—then coughed and corrected, 
“Sorry, force of habit. Engage Rick Neutralization Protocol!”

A battle broke out. Lasers, acorns, peanut-butter-based explosives—chaos erupted. Rick whipped out his Rodent Annihilation Cannon (Beta) and zapped half the swarm.

“Morty, activate the contingency plan!”

“Which one? You’ve got like—twelve of those labeled ‘Squirrelpocalypse!’”

“The one with the hazelnut-scented detonator!”

Morty fumbled through Rick’s drawer and hit the big red button. A dimensional rip opened, sucking the squirrel army into a parallel universe filled only with cats and hawks.

Panting, Morty looked at Rick. “Is it over?”

Rick looked solemn. “For now. But trust me, Morty… they’re out there. Watching. Waiting. Probably running TikTok.”

He lit a cigar made of rolled-up conspiracy theories and muttered, “Never trust a species with a 3-year memory and a 4D finance plan.”

End scene. Sponsored by Szechuan Sauce.
SK-CERT{5qu1rr3l5_53cr375_4nd_d33p_57473}
```

[elliptic3_allinone.sage](elliptic3_allinone.sage)

## Vlajka

```
SK-CERT{5qu1rr3l5_53cr375_4nd_d33p_57473}
```
