# Zadanie

EN: Based on your findings, continue your analysis with the docker layer of the docker container.

SK: Na základe predchádzajúcich zistené, pokračujte s analýzov súborov napadnutého kontajnera.

**Súbory:**

- part2_docker_layer.tar.gz

## Riešenie

Z predošlej úlohy ma z príkazu, ktorý bol vykonaný používateľom ratchet zaujili dva súbory, a to `/tmp/persistence`, ale viac ma zaujíma `/var/data/keylogger.bin`. 

Nachádza sa konkrétne pod priečinkom `diff` a ide síce o binárku, ale skúsim grepnúť stringy SK-CERT alebo U0st.

```bash
majino@majino:~/.../diff/var/data$ strings keylogger.bin | grep SK-CERT
=== LOG START SK-CERT{l34v3_17_70_7h3_pr05} ===
```

## Vlajka

```
SK-CERT{l34v3_17_70_7h3_pr05}
```
