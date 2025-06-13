# Zadanie

EN: So, turns out, Gene is also a skilled CyberChef! Some of his best inventions were so sensitive he has hidden them under layers of military grade encryption.

SK: Tak sa ukázalo, že Gene je tiež zručný CyberChef! Niektoré z jeho najlepších vynálezov boli tak citlivé, že ich skryl pod vrstvami vojenského stupňa šifrovania.

## Riešenie

Pri predošlej úlohe sa mi nepodarilo získať súbor `fourth-flag.aes.b64.txt`, po hlbšej analýze obrazu disku som si všimol, že zip súbor bol fragmentovaný na dve časti, prvá časť sa nachádzala v sektoroch pred pdf a druhá časť za pdf. Po spojení som dostal pôvodný celý zip súbor a v ňom bol spomínaný `fourth-flag.aes.b64.txt` a `fifth.txt`, ktorý obsahoval piatu vlajku, ale tá nám v tejto úlohe nepomôže.

Tu som som skúšal na AES rôzne techniky, sliding key z NonAscii časti file, v zadaní sú spomínane vrstvy, takže som skúšal aj brať skupiny 16,26,32 bajtov po sebe indúcem alebo 16+16,24+16,32+16 (key+iv). Nič nezabralo.. Až náhodou po skúsení kľúča ako samých null bajtov, konkrétne 32x 0x00 ako key a 16x 0x00 ako IV pri móde CBC sa podarilo dešifrovať.

[CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)AES_Decrypt(%7B'option':'Hex','string':'0000000000000000000000000000000000000000000000000000000000000000'%7D,%7B'option':'Hex','string':'00000000000000000000000000000000'%7D,'CBC','Raw','Raw',%7B'option':'Hex','string':''%7D,%7B'option':'Hex','string':''%7D)&input=ZlhCc29PT3MyTkl4RE9lRG8xYjR5em1pUEVGSU5EZm82U3lOQ1VGMGhDV003U3BvbE9SMlE4VU1LSkkwL1FFSApDOXBXZ0N2M21OaEw3bExLUm04OEl6NWhLLy85UTc3Yng5QmtkbWkxWGJQVVRkdHliOGZKTEI5Z21Ib081QXp5CnhQNnpsYU1QTm8vdlR6VGkvUGIyU0R0OWdGTkxHSHJ4T3VkdjVSZUF1SlF0SS9xWGZMR1FySkR1dWFJYzZYdEIKWldsaXNCMjhmS2V5SDE3TFp5MUErWDNqZWRDckJUM2NiSE5OWlp5YkZjZzhuZUNWdFFLd28wQzBucHBJOTYrTgpVOWlNQjFUZlNOZzB3Mm1mMGxkaG1TeXhqV1hkSVpMT1VBSUp5UFhLNmkzRjRBdDdrWUlQOGRkeEpqQzNOYlRECkl5K3hTNURQSzJHVzZpSEpXNGdLY2FVQml4SzhmOUgxQ1liOEczUnNuaHVYTGxDUFRhNjFvQVFOT1BqaXdOajQKaDRIU3UvVDRzTXBVaXF0KzQyYTNKZkhoVm1JcmZYNVhWbnd4NEx0U0dMWCtFMUZTNTZsNzd2T1dUU1h0T2tDTApYWHlZZ1d1c1RZVzN2WDQrZGlDc2FMY05HWVZ4b2pWc3JHOWQrMVBXWExqdXdCN2U4ckJrNHh3REVzaCtSUnpGCmY2Z3pHQ1I1NUZHTGNrS1FNdDhNVGNLQUxTRjZRbThsdTdBNVFHcTI2R0JCcTZOSm5ERmNMZ1ZZVE9FNjJNbmcKTGxhUkE4azNNUzlNeUpXYXBuUTluM0hBZWJUTGVNaFpPa3RIUGdOZERZaGtyL3c2c3I3dE9nNUdRWW9IODJkbApKQUN3SU4zV05vMFRuZnhXdUsyd3NUM3R5Wjd2cHBqVmFsWFQ1Y2tjeElvRDR6c1pUajRNY29hemtWcTgzWStuCmFSeWE4ZVNteTVGU0xxcmo5OUcrRERyMkJBeEJZc2VFRzZEblRRZjZudnl2a2VSd2YwZ3plQ0JZaUJaS2lzNnYKOGlsTjZYSVA1L1FsbU5scGdhOG5TZ1JTVlU2RGswZk5tLytVZjh5RlcyRT0K)

Obsah:

> In kitchens made of knitted cheese,
> the spoons recite old Greek decrees.
> A purple horse with wings of bread,
> plays chess against a talking shed.
> 
> Gravity sneezes, stars run late,
> the soup complains about its fate.
> On Tuesdays clocks wear hats and sigh,
> bananas teaching clouds to fly.
> 
> My socks debate philosophy,
> while hummingbirds drink cups of tea.
> A mailbox dreams of being king,
> whenever cabbages loudly sing.
> 
> So here we float in jelly seas,
> a pickle reading prophecies.
> Reality slipped on buttered floor—
> just nonsense knocking at the door.
> 
> SK-CERT{d0esnt_m4ke_s3nse_7o_d0_f0rensics_anym0r3}

## Vlajka

```
SK-CERT{d0esnt_m4ke_s3nse_7o_d0_f0rensics_anym0r3}
```
