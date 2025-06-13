# Zadanie

EN: You have a persistent feeling there must be more to it. We are still searching for Gene’s recipe. Keep recovering.

SK: Máš dotieravý pocit, že tam musí byť ešte niečo viac. Stále hľadáme Geneov recept. Pokračuj v obnove.

## Riešenie

diskimage.bin som prehnal na kali cez `binwalk`

Výsledok

```
binwalk diskimage.bin   

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
1630720       0x18E200        Zip archive data, at least v2.0 to extract, compressed size: 130929, uncompressed size: 130936, name: file
1761711       0x1AE1AF        Zip archive data, at least v2.0 to extract, compressed size: 776, uncompressed size: 1262, name: fifth.txt
1766068       0x1AF2B4        JPEG image data, EXIF standard
1766080       0x1AF2C0        TIFF image data, big-endian, offset of first image directory: 8
1879290       0x1CACFA        Zip archive data, at least v2.0 to extract, compressed size: 653, uncompressed size: 825, name: fourth-flag.aes.b64.txt
1880270       0x1CB0CE        End of Zip archive, footer length: 22

```

Podľa výskytu sa tam nachádza niekoľko zip súborov obsahujúcich súbory ako `file`, `fourth-flag.aes.b64.txt` a `fifth.txt`.

Použil som FTK Imager na extrakciu súboru zip a po otvorení cez 7zip vidím len súbory `file` a `fifth.txt` , `file` sa nám podarilo vytiahnuť, `fifth.txt` sa obnoviť nedá a fourth... tu ani nie je... vo `file` je však takýto obsah

> Begin by gently whispering to a fresh beetroot, ensuring it's thoroughly startled before peeling. Simmer beef slices under moonlight until they hum softly, indicating readiness. Combine with precisely three beetroot dreams, diced finely, and a pinch of yesterdayâ€™s laughter. Allow the mixture to philosophize in an oven preheated to curiosity. Occasionally stir with a skeptical spoon, preferably wooden, until the aroma resembles purple jazz. Serve only after garnishing with a sprinkle of questions unanswered, paired with a side dish of a sautÃ©ed third flag SK-CERT{R3c0V3r3D_R3cip3}. 
> 
> 
> a náhodný sled bajtov



## Vlajka

```
SK-CERT{R3c0V3r3D_R3cip3}
```


