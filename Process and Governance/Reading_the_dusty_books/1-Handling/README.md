# Zadanie

EN:

1. There was a large incident in a water treatment facility. It required response from various CSIRT teams, providing live system analysis, forensics, malware analysis, ICS expertise and other roles. You overheard a guy from team A talking about choosing a containment strategy. A guy from team B talking about containment and eradication stage. A guy from team C talking about evidence gathering and handling. Identify which two teams are likely using the same incident handling methodology.

2. In one of the two leading standards on cybersecurity incident handling, there is a chapter Access Control under Type of incidents. Looking at the second word of the text from that chapter, how many letters are there?

3. In ENISA incident guide table of contents, which chapter has the same colour as the iconic object on the picture on the same page? Answer in uppercase, no spaces.

4. In the same document, there is a diagram which looks like a downward pointing arrow. What is the stage on the tip of the arrow? Answer in uppercase, no spaces.

5. SANS methodology for incident handling specifically mentions some operating systems. Out of those, which is the least frequently mentioned one? Answer in uppercase, no spaces.

Flag format: answers, separated by dash:

- two letters from the first question, i.e. one of AA, AB, AC, BC (two letters, uppercase, nothing else)
- number answering the second question
- name of the chapter, all letters uppercase, no spaces (if any).
- stage, all letters uppercase, no spaces (if any)
- name of the operating system

For example, if your answers were

1. CD (of course there is no letter D, are we clear?)
2. 9
3. NAMEOFTHECHAPTER
4. SOMESTAGE
5. BEOS

Then the flag will be

CD-9-NAMEOFTHECHAPTER-SOMESTAGE-BEOS

Submission limit is 20

SK:

1. V zariadení na úpravu vody došlo k veľkému incidentu. Vyžadovalo si to zásah rôznych tímov CSIRT, ktoré poskytovali analýzu živých systémov, forenznú analýzu, analýzu škodlivého softvéru, odborné znalosti v oblasti ICS a ďalšie úlohy. Počuli ste, ako člen tímu A hovoril o výbere containment strategy. Člen tímu B hovoril o fázach containment a eradication. Člen tímu C hovoril o evidence gathering a handling. Identifikujte, ktoré dva tímy pravdepodobne používajú rovnakú metodológiu riešenia incidentov.

2. V jednom z dvoch popredných štandardov pre riešenie kybernetických incidentov sa nachádza kapitola "Access Control" pod Type of incidents. Koľko písmen má druhé slovo textu z tejto kapitoly?

3. V obsahu príručky ENISA pre riešenie incidentov, ktorá kapitola má rovnakú farbu ako ikonický objekt na obrázku na tej istej strane? Odpoveď napíšte VEĽKÝMI PÍSMENAMI, bez medzier.

4. V tom istom dokumente sa nachádza diagram, ktorý vyzerá ako šípka smerujúca nadol. Aká fáza sa nachádza na hrote šípky? Odpoveď napíšte VEĽKÝMI PÍSMENAMI, bez medzier.

5. Metodológia “SANS methodology for incident handling” konkrétne spomína niektoré operačné systémy. Ktorý z nich je spomenutý najmenej často? Odpoveď napíšte VEĽKÝMI PÍSMENAMI, bez medzier.

Formát odpovede: odpovede oddelené pomlčkou:

- dve písmená z prvej otázky, t. j. jedna z možností AA, AB, AC, BC (dve VEĽKÉ písmená, nič iné)
- číslo odpovedajúce na druhú otázku
- názov kapitoly, všetky písmená VEĽKÉ, bez medzier (ak existuje)
- fáza, všetky písmená VEĽKÉ, bez medzier (ak existuje)
- názov operačného systému

Napríklad ak sú správne odpovede:

1. CD (samozrejme tu nie je žiadne písmeno D, je to jasné?)
2. 9
3. NAMEOFTHECHAPTER
4. SOMESTAGE
5. BEOS

Vlajka bude:

CD-9-NAMEOFTHECHAPTER-SOMESTAGE-BEOS

Limit odovzdaní vlajok je 20

## Riešenie

1. najblišie k odpovedi sú A a C, pretože používajú metológiu podľa https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-61r2.pdf, konkrétne `3.3.1 Choosing a Containment Strategy` a `3.3.2 Evidence Gathering and Handling`, takže **AC**

2. odpoveď na toto by mala byť oficiálne v tomto dokumente https://www.iso.org/obp/ui/en/#iso:std:iso-iec:27035:-1:ed-2:v1:en konrétne v `B.1.5 Access control` pod `B.1 Type of incidents` ale ten je za platobnou bránou, takže ostáva hľadať ďalej a nakoniec sa podarilo nájsť https://bsn.go.id/uploads/attachment/rsni3_iso_iec_27035-1_2023_jp.pdf
   
   > B.1.5 Access control
   > 
   > 
   > Unauthorized access leads to system compromise, theft of resources, and information breach.
   > Future occurrences should be prevented by identifying underlying exposures and causes and, where applicable, review of access control permissions (authorization, authentication, roles, privileges, network access, etc.)
   
   Druhé slovo je access, takže odpoveď je **6**

3. na titulnom obrázku v https://www.enisa.europa.eu/sites/default/files/publications/Incident_Management_guide.pdf je červené hasičské auto, rovnakej farby ako kapitola 7 - **WORKFLOWS**

4. šípkových diagramov je tam viac, ale taký, ktorý má v šípke nejaké fázy je na strane 37 a hrote šípky je Improvement proposals - **IMPROVEMENTPROPOSALS**

5. v tomto dokumente https://dl.icdst.org/pdfs/files3/d60a0c473353813ed1f32c4faefedbd6.pdf je spomenutých viacero operačných sýstémov, zo spomenutých je tam 17x Windows, 2x linux, 6x unix, najmenej teda **LINUX**

## Vlajka

```
AC-6-WORKFLOWS-IMPROVEMENTPROPOSALS-LINUX
```
