# Zadanie

EN: You know that feeling—waking up after a wild night of gambling, pockets full of keys you’re sure are yours, but somehow every single one feels wrong, and you can’t, for the life of you, remember which one fits where, or even what it’s supposed to unlock?

Now imagine being a novice cryptographer after that same night. You’ve got the keys—sure—but absolutely no clue what they open, how they work, or why you even have them in the first place. Welcome to the hangover of cryptography.

You think this file should contain a flag encrypted using... AES? Also, the letters ECB come to mind although you don’t know what it is. The flag should be in the usual format SK-CERT{something}.

key (hex format): 00000000000000000000000000000000

SK: Poznáš ten pocit—prebudíš sa po divokej noci gamblingu, vrecká plné kľúčov o ktorých si si istý že sú tvoje, ale akosi každý jeden nie je ten pravý, a za ten svet si nevieš spomenúť, ktorý pasuje kam, alebo čo vlastne mal odomykať?

Teraz si predstav, že si začínajúci kryptológ po tej istej noci. Máš kľúče—jasne—ale ani šajnu čo odomykajú, ako fungujú, alebo prečo ich vôbec máš. Vitaj v kryptografickej rannej opici.

Zdá sa ti, že tento súbor by mal obsahovať vlajku šifrovanú pomocou... AES? V mysli sa vynárajú aj písmenká ECB, hoci vôbec netušíš čo to je. Vlajka by mala byť v obvyklom formáte SK-CERT{niečo}.

kľúč (hex format): 00000000000000000000000000000000

**Súbory**

- ecb.dat



## Riešenie

Všetko je vlastne napísané, stačí hodiť vstup do cyberchef, aj kľúč, prepnut input na raw a hotovo

[CyberChef](https://gchq.github.io/CyberChef/#recipe=AES_Decrypt(%7B'option':'Hex','string':'00000000000000000000000000000000'%7D,%7B'option':'Hex','string':''%7D,'ECB','Raw','Raw',%7B'option':'Hex','string':''%7D,%7B'option':'Hex','string':''%7D)&input=qgAyCY81C5BTL/OeLcG/ZPPENrFYM5/C4IF9DTzLLk8)



## Vlajka

    SK-CERT{f1r57_15_3cb}
