# Zadanie

EN: We've received a tip about a suspicious website promoting a privacy-focused browser extension. The website seems legitimate, but you should check it thoroughly. Sometimes the most interesting things are hidden in plain sight.

SK: Dostali sme tip na podozrivú webstránku propagujúcu rozšírenie pre prehliadače zamerané na súkromie. Webstránka sa zdá byť legitímna, ale mali by ste ju dôkladne skontrolovať. Niekedy sú najzaujímavejšie veci skryté priamo pred očami.

[https://alexmercer-dev.github.io/datashield-web/](https://alexmercer-dev.github.io/datashield-web/)

## Riešenie

V zadaní máme url, ktorá je vlastne interaktívna stránka github repozitára, kde doména tretej úrovne `alexmercer-dev` je autor a `datashield-web` je repozitár. Otvorím teda stránku repozitára na githube prostou zámenou položiek v url na `github.com/alexmercer-dev/datashield-web` a na konci úvodného readme v časti Licence leží odsek

```
This project is licensed under the MIT License - see the LICENSE file for details.

U0stQ0VSVHtoMWRkM25fMW5fcGw0MW5fczFnaHR9
```

kde base 64 už asi nemusím predstatovať

## Vlajka

```
SK-CERT{h1dd3n_1n_pl41n_s1ght}
```
