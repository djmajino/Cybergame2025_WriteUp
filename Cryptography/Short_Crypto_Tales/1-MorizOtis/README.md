# Zadanie

EN: Moriz Otis, cryptographer and CERTcoin tycoon, sent coins to a phishing awareness hotline, a jar of entropy, and even himself. But when he tried one final mega-transfer and locked his flag with it, something went horribly wrong. Now the flag’s encrypted, Moriz is panicking, and it’s your job to fix the mess.

SK: Moriz Otis, kryptograf a magnát CERTcoinu, poslal mince na linku na zvýšenie povedomia o phishingu, do dózy entropie a dokonca sám sebe. Keď však vykonal posledný mega-prevod a uzamkol s ním svoju vlajku, niečo sa strašne pokazilo. Teraz je vlajka zašifrovaná, Moriz panikári a vašou úlohou je tento zmätok napraviť.

**Súbory:**

- main.py
- data.json

## Riešenie

V main.py máme `BYTE_MAX = 255` a `KEY_LEN = 32`

```python
def __init__(self):
        self.priv_key = []
        for _ in range(KEY_LEN):
            priv_seed = urandom(KEY_LEN)
            self.priv_key.append(priv_seed)
        self.gen_pubkey()

    def gen_pubkey(self):
        self.pub_key = []
        for i in range(KEY_LEN):
            pub_item = self.hash(self.priv_key[i])
            for _ in range(BYTE_MAX):
                pub_item = self.hash(pub_item)
            self.pub_key.append(pub_item)

    def hash(self, data):
        return hashlib.sha256(data).digest()
```

Zo zadania viem, že skript pri inicializácii triedy Motiz_OTS vytvorí KEY_LEN teda 32 náhodných private keys o veľkosti KEY_LEN teda 32 bajtov, z ktorých pre každý vytvorí po jednom public key tak, že každý privátny kľúč zahashuje raz a následne daný hash (konkétne jeho digest, teda hex ako bajt) ešte BYTE_MAX teda 255 krát a toto je výsledný verejný kľúč. Použitím hash funkcie si môžem byť istý, že úloha nebude o získani privátneho kľúča. A etda nebudem potrebovať privat key na získanie podpisu tej poslednej message2.

> Vďaka vlastnostiam SHA-256 (predimage resistance) z daného verejného kľúča nemožno „vypátrať“ pôvodný privátny seed, takže VPN (Verifiable One-Time Signature) schéma zostáva bezpečná a cieľom tejto úlohy nie je lámať privátne kľúče, ale ukázať, ako z nich odvodíme verejné kľúče pomocou hash-reťazca.

Po spustení kódu sa teda inicializuje táto metóda, ktorá ale navyše obsahuje aj metódy 

```python
def sign(self, data):
    data_hash = self.hash(data)
    data_hash_bytes = bytearray(data_hash)
    sig = []
    for i in range(KEY_LEN):
        sig_item = self.priv_key[i]
        int_val = data_hash_bytes[i]
        hash_iters = BYTE_MAX - int_val
        for _ in range(hash_iters):
            sig_item = self.hash(sig_item)
        sig.append(sig_item)
    return sig

def verify(self, signature, data):
    data_hash = self.hash(data)
    data_hash_bytes = bytearray(data_hash)
    verify = []
    for i in range(KEY_LEN):
        verify_item = signature[i]
        hash_iters = data_hash_bytes[i] + 1
        for _ in range(hash_iters):
            verify_item = self.hash(verify_item)
        verify.append(verify_item)
    return self.pub_key == verify
```

ktoré vytvárajú a overuju podpisy pre dané správy.

```python
for i in range(20):
        message = f"{w.pub_key[0].hex()} transfered {int.from_bytes(urandom(1), 'big')} CERTcoins to {urandom(32).hex()}".encode()
        signature = w.sign(message)
        assert w.verify(signature, message)
        output["signatures"].append({
            "message": message.decode(),
            "signature": [s.hex() for s in signature],
        })
```

Tu vidím, že kód vytvorí 20  správ, kde každú jednu podpíše každým privátnym kľúčom, takže každá z 20 správ obsahuje po 32 podpisov. Problém však spočíva v tom, že podpis nie je ani tak podpis správy ako skôr počet iterácii zahashovania privátneho kľúča podľa konkétneho bajtu hashu tej ktorej správy. A to v znení - pozícia bajtu hashu správy zľava (big endian) určí počet iterácii hashovania privátneho kľúča a to tak že 255-hodnota toho bajtu, ak je bajt f3, tak 255 - 243 (0xf3 = 243) iterácii hashovania privátnneho kľúča...

Príklad:
`c16e202e80a75a46d938c9cbe1fb16f42f768fd496c306ec837fec05030e8e5b transfered 171 CERTcoins to 9c4833bf7905d20da279db81fd88f240803cea674e5e173103f8a1d5515d5bb7` má hash `f3ee7588459a2fa61370481ba1c093f1315ab2f846a2375205ed738501fc43bc`

Ak bol priv. kľúč na indexe 0 `3a8022c95863dfa150cf465bfb2ecd2cf149c76349cd06dd4be9753f4b012645` tak by mal byť prvý podpis (nultý index) podpis tejto správy 12. riadok výstupu tohto skriptu

```python
hex_string = "3a8022c95863dfa150cf465bfb2ecd2cf149c76349cd06dd4be9753f4b012645"
data = bytes.fromhex(hex_string)

def hash(data):
    return hashlib.sha256(data).digest()

# vykonaj hash 256-krát
for i in range(256):
    data = hash(data)
    print(data.hex())
```

výstup

```
39a05bb15590ad4d9756b0827fec166a22409a6afb8e5fb38f6a8a30d8751f3a
4d46c70c01e2d8b3f0ce03b0f33ac8bb99884f538954b4ca393f88631fc8c0e5
78e132d5beadf7f38cd239353967ba1805f3d117b7f49d53520f1e268b8fa799
fc0de8d98b5a3a9ca90b06e84fec2840fd268c2475b2ae06e25e655e32809348
8de0f26c231c4bd6dc0c9e086dbe1fcfaec3cf5f12e940ee39e414e8b5be6e6a
014393cefa5b600ea6c7e8495d184f54534bb8f3b882e81c4cb8c7b5b16bc45c
5d5f30f6aafc81bfb483e3c60c9f0d0f539bad03702cebdf54f37ebc30ba8096
60655aa4cad02e2cf6090ca9ef6342727e9de1febfd743b0b88f96322dbcb599
c960df285e3464d2178605a6682221203e39644fc6a968050729a4dfb951477a
4f319b127a31f73681a7dee3e75e65e5a7f184ab7f9133657a46f6549b30d1f4
96ac5fd7c07c0dc86a4c39eff6f0d0a86d1f0b4f9a5c445faca8797ad2a303dc
--->a51691310505af2ce6f74fdd316974cf487a9d0add68a5f1082f040fb49cca32
ae3bf3fbd4183b8d2cc635ae1c1636f2aaef9bf83467d466ddfc0ac2e9408631
59328ffb4837a69f2b07a680928c9e8eb0bef0119894a1925483e8e209bc13b4
484a87294f9e011b332281cd33b36ef53c01fc1cb1446f951d9f41d5f3a15bca
2d7b7e3005d6f154f9e83471fdf7b85656ca45e32d837dfde35426750386f911
```

A teda aj skutočne je

```json
"message": "c16e202e80a75a46d938c9cbe1fb16f42f768fd496c306ec837fec05030e8e5b transfered 171 CERTcoins to 9c4833bf7905d20da279db81fd88f240803cea674e5e173103f8a1d5515d5bb7",
    "signature": [
    --->"a51691310505af2ce6f74fdd316974cf487a9d0add68a5f1082f040fb49cca32",
        "42c5875bb2017a15fe1a31b03f15db2953985e9e7202e07c3b079666dcbf9c3e",
        "3eaf79a8f065e046b655fe21333bdb7e42066d5723c0cea3bde11d1860e774a6",
        "6020f1fdca62bce83b9acc683298d336d29c63ea1441fcb852156c1b471e6a8e",
        "cf9803d04999d7cef79b27626d195c8df3678ed4d26eaa8e58ad64eb278deac0",
        "493a5075ae1ce04e4f69db11610ba172ea686acc02682572ace6b0783a183e8b",
        "abbdf01d9b83252fe4bdaa5a4d5208caa85a5b392506a5c5f93895952e5afd14",
        "b71566b0f0179f7784a3b2736e2f4f839d368085eda5260f6da51593fd464ffe",
        "6624fafbcaaf8681ea8b7fbff53e9486ade9732fa48b757044d1faafb420e47c",
        "b147dcdd5760a19a34b92cb97b9bd500d8dfbc93cd933368d0614e2e8167e6b2",
        "4acbcb78fe5ab3afde711aae6aafd4386b0925d99f92f36e3cc6b3b0f46198e3",
        "b10c711a5b184d00fd50b46e66e2f765f7796fa203dc692c810dd9fcab40a458",
        "4536e5fd3226de75c33934c15ee91346577a5222808b4b2e2c46bbe3ad51aaf9",
        "443f2ecf7ee7bf656eff170e0ce6e002f3a498c901f2410a77258f9dbe361d74",
        "ff81bef692ded6f2e2cfe462ea611c2211ae6bed311b91db490fea2ffca6af22",
        "de58e8f2f2a37f0f4968ffe87793c5697829ac0b41bdbbfe2bb6aadfbdf0dbc0",
        "0cf5d4e59e35f2ba403dd01c1d36ec46565ca3d1d70c242532825090ada8a5cd",
        "3c51b27cd786ce621d7886006a40057fe2c0ebdef4d374229a45eb484733e14a",
        "7890ab60ecd93eeb6eb20d12e4b8b0ef362255cafefce2b0cd53a85cacd04a20",
        "6c4eca77ef7c6df91009b1fec7750addddae3b54f6f952e2d6d1038a9325b933",
        "912682b858741b3520b59df0c691ec417516c2d9c951f451d6862728e9b2fd2a",
        "5bde884690f686da85d1405fcb9e5de4e0d9d2d45a35c26119eab355b609319d",
        "2d0175127d5644e1338b524ad8a80a0b209b9d3ba88a8a82e23bc3441db9b625",
        "7c20e7e53469551abd5936ad60f601b90ba779f4bcca4373c7cc3f9e134f4cb0",
        "981875fb1c2bcfe2bbbd1fb94a2efa7c02d0b6f6e6a4ba4a7a4a4e3cdbd46e3b",
        "142366c5afe82b57d1cb11bba42dd43553f044a3adf359fef5739a8007a6761a",
        "041579df2b368f2a76712f0e6ea14904540deaf5d96ef8dd9f25e1441d61a6f0",
        "fd83c4b1babcb1c32885f2875e5e20a8bdbe457a76e5b90c112a712758809672",
        "3843332b1ffc01ee7cae86c029f664b6c3c538519da9001cb30d82734acf91b8",
        "8ffa9307f14de6e812d5a54925f596f6fd98c6616ad808f45edbdf5d15991bf5",
        "ee5c53bdf2fc3680f98bfefdee1a580cd96b8db28af7164e956cc2326915be1d",
        "a1fdd846510e947eee7b08aa85ca93d66f01784597d3d894eb143af3afc29c6a"
    ]
}
```

Čo to znamená? Hashovať vieme len jednosmerne, povedzme teda, že len dopredu.. Nedokážeme získať originál toho, z čoho vznikol hash. Ale ak hash správy `message2 = f"{w.pub_key[0].hex()} transfered 999999 CERTcoins to me".encode()` bude mať bajt na pozícii úplne vľavo menší ako `0xf3` napríklad bude `0xf2`, tak aj bez znalosti privátneho kľúča vieme získať verejný kľúč, pretože vieme, že tu treba 13 hashov (ff - f2 = 13) privátneho kľúča namiesto 12 (rozdiel bol 1, takže o jedno viac ako 12), takže urobíme iba jednu iteráciu hashu `a51691310505af2ce6f74fdd316974cf487a9d0add68a5f1082f040fb49cca32` a to bude podpis našej správy a to vieme z toho malého skriptu, že to bude `ae3bf3fbd4183b8d2cc635ae1c1636f2aaef9bf83467d466ddfc0ac2e9408631`.. a vieme teda, že bajt 0xae bude prvý bajt AES kľúča, ktorým dešifrujeme vlajku (hypoteticky, reálny bajt bude iný, pretože reálny rozdiel bude iný)... Čo to znamená? Vieme, že každá správa obsahuje ako odosielateľa hex reprezentáciu verejného kľuča na nultom indexe a ako prijímateľa náhodné hex číslo, ale správa, ktorú chceme použiť obsahuje len "to me", čiže vieme, že správa je `c16e202e80a75a46d938c9cbe1fb16f42f768fd496c306ec837fec05030e8e5b transfered 999999 CERTcoins to me` a z toho hash je `b01aaf675357340e61d208d032ac19e265e31779e43757a2d4639d275faf57f6`. 

Čo teraz potrebujeme na získanie všetkých podpisov? 

Potrebujeme nájsť najväčšie bajty na každej bajtovej pozícii(d_max) hashov všetkých správ a ak každý najväčší "bajt" hashov známych správ bude vačší ako bajt na konkrétnej pozícii hashu dodatočnej správy, vieme, že máme k dispozícii priestor na dohashovanie známych podpisov týchto správ na takej pozícii zhora ako je pozícia bajtu hashu zľava tej správy, kde vyšiel najväčší bajt.

Pri riešení som si vyrobil vlastný json, je v tomto priečinku uložený ako `data_mytest.json` Vytiahnem najvačšie bajty hashov a podpisy podla pozicie.

| Index | MaxByte | Hash                             | Signature                        |
| ----- | ------- | -------------------------------- | -------------------------------- |
| 0     | fc      | fcc19660a3eb6772db2eebb57120bb99<br>afbf823b702104bcd8bd09e6369614c8 | 78e132d5beadf7f38cd239353967ba18<br>05f3d117b7f49d53520f1e268b8fa799 |
| 1     | f3      | 92f3d6032487e13dc83d9e84c9837cdf<br>250b9ab9e1e5c97f19cc76df9a69b692 | 489ec41b8dbd8e549e9adf95873b2d45<br>db95054ad93334e4446e9277df6bc398 |
| 2     | f8      | f7b1f82fbade3dec88485abc9cd321a2<br>95afc1c4f78795b2dafabe65787c9f13 | 8958fcd477674691b4e49cd9a7fa07a0<br>d0211b3a91b4df8df754f11e3e5a2354 |
| 3     | df      | 3de53adf2c4bfa3d4c3c1669cf0ae8c4<br>68482cd92ff4078f7187fe1e2cfabdc4 | f07c1f687a09681f36c5376e537fd625<br>94c9c554f9338852f9f051984dfbf23c |
| 4     | e8      | 164da8dde87842716101ef3ee09fc681<br>6ae3a2c49f6b03ee08d542bb2afca888 | 259f47957b24f24840a9d024ad582801<br>db4c6dfc87e47f30ebcd64247cfdf4b0 |
| 5     | f5      | 579cee3b7df554b446676355aa01d464<br>73e4708eafc5c6fa7a57695a6ee84f90 | 22214c4c06136420b199119fd55e4ccc<br>52d2562a6eb00cb4cc6468196bd01f76 |
| 6     | fa      | 3de53adf2c4bfa3d4c3c1669cf0ae8c4<br>68482cd92ff4078f7187fe1e2cfabdc4 | 346b54709b943b74f887f8bc850301c6<br>1f6b1637fcbbd88126ae1d7929fabc85 |
| 7     | ec      | f7b1f82fbade3dec88485abc9cd321a2<br>95afc1c4f78795b2dafabe65787c9f13 | d43d5341797f51640af395cc98566250<br>87384c282e6c9777921243e2c1bf5ada |
| 8     | f5      | 046b206e1b744096f5da26e77fb3e2fe<br>d61bc155f4bbf136760b70e37b93a6b8 | 7b8208b898b9b4bbb5aff4768038f609<br>86b716674025b6497c6bf36ed620c813 |
| 9     | f4      | 6f780f7b3ae43d41dcf4b2055b48bea7<br>b68aa151888efc7622b3a5b85a2472ce | a5e9801c2e9e07ad022f0a42df38d963<br>67b54a14d08a38c60e76b28531c97256 |
| 10    | ef      | 164da8dde87842716101ef3ee09fc681<br>6ae3a2c49f6b03ee08d542bb2afca888 | 51cf4dbdc99790129d9db56deb6e93c7<br>434f8a4bf9eff23d80c25931761778cf |
| 11    | e7      | 046b206e1b744096f5da26e77fb3e2fe<br>d61bc155f4bbf136760b70e37b93a6b8 | deaa6af5c0bfe855fa17117f9c43564a<br>22a35f8eeb49538b223139c19bfeca83 |
| 12    | f4      | ef6b0ead9cc66178058d2a07f4d6aff6<br>e9f91f51044789441247d8ebc8e8153d | 44238053ad753f4ed88ea26a571aba91<br>cbd5b5270cd8419a20b991120ca14206 |
| 13    | f6      | b98a6372887348a868c5773d5af6603d<br>4cdc50d14281542a0d65ec165dae771b | f8adf7dec6600aee92a5499e1b347643<br>8d24aa68f011cf2fb6f92cf7380ab4bd |
| 14    | e8      | 3de53adf2c4bfa3d4c3c1669cf0ae8c4<br>68482cd92ff4078f7187fe1e2cfabdc4 | 9469d0caffe59b7c3cfe9fe14ddf6615<br>715f56292537b9cc21e42884c4a70f85 |
| 15    | fe      | 046b206e1b744096f5da26e77fb3e2fe<br>d61bc155f4bbf136760b70e37b93a6b8 | e911f0ecc206ed348d3f30d0c099e946<br>ca41284b93da4290126826039eea1ebb |
| 16    | fd      | 173c6789884075153a321123c0cad8b9<br>fde4e92cfb9f81557cd5e03aa228800b | fe891f378635b1394d0c0d60656ff639<br>a62afcff4d8674294e914070c9b0d5a5 |
| 17    | f9      | ef6b0ead9cc66178058d2a07f4d6aff6<br>e9f91f51044789441247d8ebc8e8153d | b53fa2f5a52acf92ecb942126e68908b<br>bc0537803b5937363d168693609e6e82 |
| 18    | e9      | 173c6789884075153a321123c0cad8b9<br>fde4e92cfb9f81557cd5e03aa228800b | 26d37934843dcc11b5f74893233f4aec<br>c84c24bc7afac6a054afa792dc3395d9 |
| 19    | f8      | f3ee7588459a2fa61370481ba1c093f1<br>315ab2f846a2375205ed738501fc43bc | 6c4eca77ef7c6df91009b1fec7750add<br>ddae3b54f6f952e2d6d1038a9325b933 |
| 20    | fb      | 173c6789884075153a321123c0cad8b9<br>fde4e92cfb9f81557cd5e03aa228800b | 03d9afb1793d8cc89ad61d132a23c054<br>1b81d5ba7ef326c3a15082751aa5b27c |
| 21    | f4      | 3de53adf2c4bfa3d4c3c1669cf0ae8c4<br>68482cd92ff4078f7187fe1e2cfabdc4 | 4309776debed2fe103109fbb39b47751<br>1b8a2d54e209a6f69827dabe7c69c698 |
| 22    | fc      | 6f780f7b3ae43d41dcf4b2055b48bea7<br>b68aa151888efc7622b3a5b85a2472ce | fc1153f31f93a797ea3eefebcd8c344c<br>9fcc31d2c1850aeecd3acd05b5abea2a |
| 23    | fa      | 579cee3b7df554b446676355aa01d464<br>73e4708eafc5c6fa7a57695a6ee84f90 | 2ae6ae02b24f34193d78a221afdbeb23<br>e8a5e34fea724f08a66107fb42b8cf50 |
| 24    | ee      | a0b7b0d97d780a100e0a591a837988ad<br>1009b10aae348648ee7666dfcb1a9ca3 | 4133159e71f3a4f44f7d2beab1756c4a<br>1d58a8128ec58c27279629c115b5ea59 |
| 25    | fa      | f7b1f82fbade3dec88485abc9cd321a2<br>95afc1c4f78795b2dafabe65787c9f13 | bc8396fe6d5627d61922f09266d12fe4<br>6a355f97a6f97f2872d5b70a7304ffaf |
| 26    | fe      | 3de53adf2c4bfa3d4c3c1669cf0ae8c4<br>68482cd92ff4078f7187fe1e2cfabdc4 | 26fcc061d5f07f7494cabb0e74bb0606<br>2f135ba638d2e1a4a5d17d2f6688cc99 |
| 27    | eb      | ef6b0ead9cc66178058d2a07f4d6aff6<br>e9f91f51044789441247d8ebc8e8153d | 2f823bfcb5b1a7d88a646c547f65e5c9<br>cd1925786df726807627504c4cf3c478 |
| 28    | e1      | b8ae274c38455c83997e0b7d9829d1cc<br>77381532b00498b248916860e1bc508f | c268f180f98395ef6ef964054c42b2a6<br>c0c6e98543f79b52d81658b44bd35c16 |
| 29    | fc      | f3ee7588459a2fa61370481ba1c093f1<br>315ab2f846a2375205ed738501fc43bc | 8ffa9307f14de6e812d5a54925f596f6<br>fd98c6616ad808f45edbdf5d15991bf5 |
| 30    | bd      | 3de53adf2c4bfa3d4c3c1669cf0ae8c4<br>68482cd92ff4078f7187fe1e2cfabdc4 | 79d5ee796dddd8b00d38ef34f1f17b1f<br>5f759fcb41813844da3f45d04205297a |
| 31    | fb      | 5e90c17652c8ee14761ddd907d8dd399<br>b42d0c4c5b607eec2c398a70c0d573fb | 70db21c39027d496525c3447bc339f05<br>9886f8126e129e5be8601238ce95e2c5 |

Tu je rozdielova tabuľka medzi najväčšími bajtami hashov správ a bajtami novej správy

| index | d_max | d_new | rozdiel |   | index | d_max | d_new | rozdiel |
| ----- | ----- | ----- | ------- |---| ----- | ----- | ----- | ------- |
| 0     | fc    | b0    | 76      |   | 16    | fd    | 65    | 152     |
| 1     | f3    | 1a    | 217     |   | 17    | f9    | e3    | 22      |
| 2     | f8    | af    | 73      |   | 18    | e9    | 17    | 210     |
| 3     | df    | 67    | 120     |   | 19    | f8    | 79    | 127     |
| 4     | e8    | 53    | 149     |   | 20    | fb    | e4    | 23      |
| 5     | f5    | 57    | 158     |   | 21    | f4    | 37    | 189     |
| 6     | fa    | 34    | 198     |   | 22    | fc    | 57    | 165     |
| 7     | ec    | 0e    | 222     |   | 23    | fa    | a2    | 88      |
| 8     | f5    | 61    | 148     |   | 24    | ee    | d4    | 26      |
| 9     | f4    | d2    | 34      |   | 25    | fa    | 63    | 151     |
| 10    | ef    | 08    | 231     |   | 26    | fe    | 9d    | 97      |
| 11    | e7    | d0    | 23      |   | 27    | eb    | 27    | 196     |
| 12    | f4    | 32    | 194     |   | 28    | e1    | 5f    | 130     |
| 13    | f6    | ac    | 74      |   | 29    | fc    | af    | 77      |
| 14    | e8    | 19    | 207     |   | 30    | bd    | 57    | 102     |
| 15    | fe    | e2    | 28      |   | 31    | fb    | f6    | 5       |


Rozdiel udáva koľko hashov ešte urobíme z tej signature z d_max a to bude signature pre d_new...

Keď budeme mať tieto nové podpisy tejto novej správy, z každej vezmeme prvý bajt, z toho vyskladáme AES kľúč, použijeme známy inicializačný vektor a dešifrujeme enc string

Moje podpisy:

```json
[
  "eb5129157d09091c729e2bf7e7f0ea3a34ee6f4a787a3cff550b9a3c0ba51398",
  "54d6e088fd32936615c13834fc46d55e3dace026e7419a065c0d2f343b21ae0b",
  "ca63c0b2be173d7ddf007e5a4e644163e54aa98c754abee4db17a3504803e1de",
  "55d392f8126725159f5d72f1bbb0a4a76f24003c3359243c84cace8c1f12cd06",
  "d22c73879aef3de612532723877f88367bb4b9868be69e3c21087bbe657e3994",
  "6ff63e68c4b3faf4dc9dcd286715d4cface40415e21eaab30a297aa1184336b8",
  "8c6d0880a39439a57b66e7e4566f0403de5baa90aa1b1c9c1eb3f1793b07901d",
  "4608e69c0a489aa57f544c14ac7bbf9e94e99cec190039344bcdd6940aaee627",
  "88c3a3087449688f9e86a9623cb6c60208483b871d0fca1917017bd6db606396",
  "945c9557a2b4eb802e957a8d0e7c0d6c27bf27eb283a964f739ed7b57aed1c37",
  "873f34c5c3a6cc4750fa8465f8e9cf9975217041b5585026fec27f84759c87b8",
  "3f56d8af0fa48c8845b17d2b696bee5cf8ea3c03d4ba62ccaca89c42ac8905bb",
  "8a1e63f73b2739b2103eb110da51175852d80b9ed3e05c87eec6a436e67d644c",
  "797f53c94a92c50c6a0d5d7e61ca9789dbf90bc01a97a6de4683b92e83c677a4",
  "fbafbe4e960655af9270586b5132e2072305d1e308f914e451cc876f727a51ba",
  "3ce21204ee19a1f1f4af725f05b2aed1c9140aba628581085b9aef0f0a3d4634",
  "36632108d776cc5da85a69d9a64081349eff766561332ee25c18d8251c4e14f5",
  "bd13b03a899ce24f89ac7aa8d468d604d06c2bd430d0018652ab668face28329",
  "3adc8f7a51ae9b833d306ccb8c64518dde384c42394ad308f4946a0876e8882a",
  "e84624ba1d90d25cf63fccc20d504375e071a527856a5f84a17b70e57f4a1ede",
  "81a3ba2616f3600ff1323c0280f71ceae22103385568322023c3cea5aa826552",
  "60424b607246dda48562dd4fca88371b3e957b935f47ca1f68e5b32e09dcaf6d",
  "dba2953677ba4487fe38382144ecb6389fb6b43b383e37f39c3dfc81f9976ebc",
  "33eb67c38fb61bd86aae57bed9ec27816b3b7cfbbc440d017a28c6afd7e07c57",
  "6d669e8dc01e9b27b808b0e35ea35437816b72ce81c0f0b2cdb37dd20175707b",
  "2c3dfb8b169bb0697c6abd90e7eace4e846e7d018e8fc2ec2f78dd8635b112ab",
  "adbae6828f65643d84b7852c68942f57fc9541f1961d11d1cfcc48b67b2ebc4b",
  "afa60bbdcb0fb9fdba1ff4d986b47d65414f3bff503857bc8e1246d9b1b40ff2",
  "3faedf732f1023e9e6b2c74c0d87879e7a93a1e58d24abb87d1de8ef36a5a888",
  "5a784d5f5db65e87452e8fbbb416a978feed6413a9ec1bc22ccb7ea3cc6c66a9",
  "36f230d4171f631170a2763ab39f2d847ee30bf4a7e4d3ee73bbaaff6d48064a",
  "67356c8d6fbfc612f066a94b321727fe27fe90e03533f3ca009d4ff19fd1e585"
]
```

V mojom teste bol enc string ciphertext realnej vlajky a to  `0deb292ce447800844234d514245ffc52917a6e6044c79b3b1b4043b3111de0a`, 

IV bol `b8c278880cff47d959b7f788fab405b1` 

a z podpisov získaný aes kľúč `eb54ca55d26f8c468894873f8a79fb3c36bd3ae88160db336d2cadaf3f5a3667`

Skript ktorý toto celé zautomatizuje

```python
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
```

vráti

```
Kľúč: eb54ca55d26f8c468894873f8a79fb3c36bd3ae88160db336d2cadaf3f5a3667
Vlajka: SK-CERT{h45h_0n3_71m3_51gn47ur3}
```

Celý prblém bol v tom, že tými istými privátnymi kľúčmi boli vytvorené podpisy pre až 20 správ, čím vznikla šanca, že na každej pozícii "bajtu" v hashi týchto 20 správ bol nejaký bajt vačší ako "bajt" na pozícii hashu správy `message2 = f"{w.pub_key[0].hex()} transfered 999999 CERTcoins to me".encode()` a tým sme vedeli pokračovať v hashovaní až kým sme si vytvorili vlastné platné podpisy a z nich aes kľúč.

## Vlajka

```
SK-CERT{h45h_0n3_71m3_51gn47ur3}
```
