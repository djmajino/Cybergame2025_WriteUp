# Zadanie

EN:

1. Which two of these colors are most related to common criteria? (uppercase, comma separated)

RED / ORANGE / YELLOW / GREEN / BLUE / INDIGO / VIOLET

2. The ENISA incident handling book, which we already mentioned, has this nice truck. What is the color of the longest part of the truck?

BLUE / RED / GRAY / BLACK / WHITE

3. The NIST standard has a different first responder's truck on some diagram. Which is true: 1 it is a police van 2 the driver of the truck is a bald male 3 the driver of the truck is a young female 4 the truck is a 6-wheeler 5 the truck looks at the shield and a sword 6 the truck travels towards the tree

Flag format: answers, separated by dash:

- colors from the list, uppercase, comma separated, in the order from the list.
- color from the list, uppercase
- the number of the correct statement

For example, if your answers were

- RED,CYAN
- GREEN
- 9

Then the flag will be RED,CYAN-GREEN-9

Submission limit is 20 flags

SK:

1. Ktoré dve z týchto farieb sú najviac spojené s Common Criteria? (VEĽKÝMI PÍSMENAMI, oddelené čiarkou)

RED / ORANGE / YELLOW / GREEN / BLUE / INDIGO / VIOLET

2. Kniha o riešení incidentov od ENISA, ktorú sme už spomínali, obsahuje pekné auto. Akú farbu má najdlhšia časť tohto auta?

BLUE / RED / GRAY / BLACK / WHITE

3. Štandard NIST zobrazuje na jednom diagrame iné záchranné auto. Čo z nasledujúceho je pravda: 1 je to policajná dodávka 2 vodičom auta je plešatý muž 3 vodičom auta je mladá žena 4 auto má 6 kolies 5 auto je otočené k štítu a meču 6 auto cestuje smerom k stromu

Formát odpovede: odpovede oddelené pomlčkou:

- farby zo zoznamu, VEĽKÝMI PÍSMENAMI, oddelené čiarkou, v poradí zo zoznamu
- farba zo zoznamu, VEĽKÝMI PÍSMENAMI
- číslo správneho tvrdenia

Napríklad, ak sú vaše odpovede:

- RED,CYAN
- GREEN
- 9

Potom bude vlajka: RED,CYAN-GREEN-9

Limit odovzdaní vlajok je 20

## Riešenie

1. Farby **RED** a **ORANGE** sa viažu k `„Red Book“ (TNI)` [Trusted Computer System Evaluation Criteria - Wikipedia](https://en.wikipedia.org/wiki/Trusted_Computer_System_Evaluation_Criteria) a `„Orange Book“ (TCSEC)` z [Rainbow Series and Related Documents](https://irp.fas.org/nsa/rainbow.htm), ktoré boli neskôr nahradené alebo prekryté schémou Common Criteria (ISO/IEC 15408).

2. Druhá časť je referencia na prvú úlohu, konkrétne dokument https://www.enisa.europa.eu/sites/default/files/publications/Incident_Management_guide.pdf - je tam červené hasičské auto s bielym rebríkom, rebrík je samozrejme najdlhšia časť, takže **WHITE**

3. Tretia časť vlajky je **5**, sanitka je otočená k zelenému štítu a meču https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-61r2.pdf (Figure 3-1. Incident Response Life Cycle, strana 21)

## Vlajka

```
RED,ORANGE-WHITE-5
```
