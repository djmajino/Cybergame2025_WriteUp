# Zadanie

EN: They are suspecting us! It seems like they are migrating to a new, closed platform. We need to find where they're going before they disappear completely.

SK: Podozrievajú nás! Zdá sa, že prechádzajú na novú, uzavretú platformu. Musíme zistiť, kam prechádzajú, skôr než úplne zmiznú.

## Riešenie

Správa zo štvrtej úlohy, `Note to self: Password for Mark's channel is 'ReallySecretNobodyKnowsAboutThisPassword'. Need to keep this safe. SK-CERT{d1sc0rd_b0t_s3cr3ts}` obsahuje aj hedlo do nejakého Merkovho kanála. Keď pozrieme  používateľov, všimneme si, že medzi botmi je okrem `Aleah Franco` aj `Mark Wesley`. Keď ho kontaktujem a napíšem hello, tak mi odpíše `Nope, that's not it. Nice try though.` Tak napíšem `Give me flag` a on mi odpíše `Access denied. I need the correct password`. Aha! Takže na toto bolo to heslo v poznáme Aleaha Francoa. Zadám teda `ReallySecretNobodyKnowsAboutThisPassword` a odpíše `Access granted. Good to have you aboard.` Vtedy sa mi zjaví nový kanál

`# hacking`

kde je pár správ a fotka. Keď kliknem na fotku zjaví sa mi pár možností, medzi ktorými je aj `View details`, ktoré obsahuje položky Filename, Size a ***Description (Alt text)** s obsahom `freirehf-fancr.rh`. Samo o sebe to nie je niš, ale ked to dekódujeme cézarom a teda ROT13, dostaneme `serverus-snape.eu`

Táto stránka sa ukázalo ako krásny honeypot plný endpointov, ktoré len zamotajú hlavu útočnikovi (nám), ale vlajku tam nenájdeme.

Ked však čítam pozorne správy botom je tam viacero zaujímavých hinto, jeden obsahuje cestu ako sa k vlajke dostať, konkrétne od bota `Spioniro_golubio` so znením `Interesting finding: This malware uses DNS TXT records for command and control communication.`

Keď zobrazím `TXT` DNS záznamy servera `serverus-snape.eu` pomocou napríklad

https://mxtoolbox.com/SuperTool.aspx?action=txt%3aserverus-snape.eu&run=toolpage

dostaneme

| Type | Domain Name       | TTL    | Record                                          |
| ---- | ----------------- | ------ | ----------------------------------------------- |
| TXT  | serverus-snape.eu | 30 min | "U0stQ0VSVHtkbnNfcjNjMHJkXzFuc3AzY3Qwcn0="      |
| TXT  | serverus-snape.eu | 30 min | "v=spf1 a mx include:_spf.hostcreators.sk -all" |

Opäť, ako v prvej úlohe, iba dekódujeme base64 a dostaneme vlajku.

## Vlajka

```
SK-CERT{dns_r3c0rd_1nsp3ct0r}
```
