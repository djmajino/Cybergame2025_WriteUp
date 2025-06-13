# Zadanie

EN: We have gathered more information about the website. It seems like some time ago it contained malicious code.

SK: Zozbierali sme viac informácií o webstránke. Zdá sa, že pred časom obsahovala škodlivý kód.

## Riešenie

Takže sme v github repozitári, pozrieme aké commity sa udiali, ktoré obsahovali škodlivý kód. 

[Commits · AlexMercer-dev/datashield-web · GitHub](https://github.com/AlexMercer-dev/datashield-web/commits/main/)

až tak veľa ich zas nie je a keď idem od posledného hneď šiesty v poradí s označením `d76658afa4964698f6ffaebe4968110117c1b5bb` skátene `d76658a` obsahuje škodlivý kód. Plná adresa je [Enahnce analytics platform · AlexMercer-dev/datashield-web@d76658a · GitHub](https://github.com/AlexMercer-dev/datashield-web/commit/d76658afa4964698f6ffaebe4968110117c1b5bb) a ide o merge pull requestu od používateľa `evanmassey1976`.

Teraz stačí načítať Diff súboru `static/js/analytics-enhanced.js` a na riadku 144 leží poznámka kódu `//SK-CERT{m4l1c10us_c0mm1t_d3t3ct3d}`

## Vlajka

```
SK-CERT{m4l1c10us_c0mm1t_d3t3ct3d}
```
