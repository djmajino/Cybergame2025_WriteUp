# Zadanie

EN: Explore the source git repository for the bastion server docker deployment and look for the source of the dropped backdoor.

SK: Preskúmajte zdrojový git repozitár pre nasadenie ssh servera a vyhľadajte pôvod nežiaduceho ssh kľúča.

**Súbory:**

- part5_ssh-bastion-repo.tar.gz

## Riešenie

Rozbalíme archív, vojdeme v shelli do priečinka s repozitárom, to je ten čo obsahuje `.git` priečinok, ale do toho nevojdeme. Pozrieme, či niečo naobsahujú samotné commity

```bash
majino@majino:---/ssh-bastion-repo$ git log --oneline --all
5f603d8 (main) merge suggested changes from colleague
a222654 (HEAD -> suggested_changes) update ssh keys SK-CERT{r09U3_3MPL0Y33_0r_5uPpLycH41n}
fe00ee7 upgrade base image
018ab72 harden user passwords
3f9744d bastion deployment. initial commit
```

A bingo, vlajka!

## Vlajka

```
SK-CERT{r09U3_3MPL0Y33_0r_5uPpLycH41n}
```
