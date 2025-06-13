# Zadanie

EN: You can’t believe your eyes. Gene was more secretive than you can imagine. Can you recover the hidden stash of wisdom?

SK: Nemôžeš uveriť vlastným očiam. Gene bol tajomnejší, než si dokážeš predstaviť. Dokážeš získať späť skrytý poklad múdrosti?

## Riešenie

FTK Imager mi bez problémov vytiahol vymazaný súbor !AUCE.PDF (výkričník značí, že sa jedná o zmazaný súbor. Je to kvôli tomu, že FAT32 zmení prvý bajt názvu na bajt `0xE5`, čo je v ascii `!`)..

Na prvotnú analýzu pdf som použil Notepad++ a tento webový nástroj

[Inspect PDF Online - PDFCrowd](https://pdfcrowd.com/inspect-pdf/)

z ktorého som vyextrahoval streamy a obrázky. Vlajka sa nakoniec nachádzala v obrázku s logom SK-CERT, konkrétne v metadátach... 

https://exif.tools/

Cez tento nástroj som prehnal obrázok, boli tam výskyty hlášok ako

> This REALLY is not it
> 
> This TRULY isn't it..
> 
> This ALSO is not it..

Bolo treba íst hlbšie a nakoniec to bolo <rdf>..... časti, resp za ňou ako xml koment.

```
<!--ÂÂ‚Âƒ\cprt@PwtptA2B2_^@VuwtuTeEEf9uthkAwc1_zzpRq9x4c/LV0TOw5x6a_U0stQ0VSVHs3aDFzX1dBU18xN19hZnRlcl9hbGx9$EucR/FqMoVaZvjx3OvGT_EV4u/Y7EDwDeA/w9QO3+^ALYXhvTD3R1JcGJUgKFi_mhzkezdqaIHzm261y9IQ_EV4u/Y7EDwDeA/w9QO3+µpâ)‘pÌ<©p¯NpŒ_ßpcpØp6“p’ oÎ¢‡o–²Ïo^Âýo9Ó7o6ã-->
```

Zaujímavý je reťazec skupiny base64 stringov

> VuwtuTeEEf9uthkAwc1_zzpRq9x4c/LV0TOw5x6a_U0stQ0VSVHs3aDFzX1dBU18xN19hZnRlcl9hbGx9$EucR/FqMoVaZvjx3OvGT_EV4u/Y7EDwDeA/w9QO3

Po dekódovaní

> ........._SK-CERT{7h1s_WAS_17_after_all}$.........

## Vlajka

```
SK-CERT{7h1s_WAS_17_after_all}
```
