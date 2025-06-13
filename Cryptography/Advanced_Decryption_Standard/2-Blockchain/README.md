# Zadanie

EN: You can’t, for the life of you, remember why each flag ended up with a different chaining method. Must’ve been one heck of a night...

This file contains the flag encrypted using AES with mode CBC.

key (hex format): 00000000000000000000000000000000 iv (hex format): 01020304050607080102030405060708

SK: Za ten svet si nedokážeš spomenúť, prečo si na každú vlajku použil inú metódu zreťazenia. To musela byť pekelná noc...

Tento súbor obsahuje vlajku zašifrovanú AES s módom CBC.

kľúč (hex format): 00000000000000000000000000000000 iv (hex format): 01020304050607080102030405060708

**Súbory**

- cbc.dat



## Riešenie

Rovnako ako v prvej úlohe, všetko ja dané, iba nakŕmiť Sajbršéra.

[CyberChef](https://gchq.github.io/CyberChef/#recipe=AES_Decrypt(%7B'option':'Hex','string':'00000000000000000000000000000000'%7D,%7B'option':'Hex','string':'01020304050607080102030405060708'%7D,'CBC','Raw','Raw',%7B'option':'Hex','string':''%7D,%7B'option':'Hex','string':''%7D)&input=YqNPLiW1wUyBAxdMEuIyOOAAY%2BppXPvTPiQRZHKeq6E)



## Vlajka

    SK-CERT{cbc_m0d3_15_n3x7}
