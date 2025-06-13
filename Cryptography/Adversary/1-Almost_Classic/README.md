# Zadanie

EN: We've captured communication of two adversaries. We need to decrypt it.
SK: Zachytili sme komunikáciu dvoch protivníkov. Potrebujeme ju dešifrovať.

**Súbory**

- communication.txt

    X: Ovgh xlliwrmzgv gsv wilk klrmg.
    Y: Ztivvw yfg dv szev gl yv xzivufo. Lfi xibkgltizksvih dzimvw fh zylfg gsrh nvgslw. Gsvb hzb rg dlmg slow uli olmt.
    X: Dv wlmg szev grnv gl hvg fk zmbgsrmt yvggvi. Xlnv gl gsv fhfzo kozxv rm gsv Kvmgztlm, Hgzeyzihpz 42. Gsv yzigvmwvi droo trev blf gsv kzxpztv. 
    Y: Urmv yfg ru dv tvg xlnkilnrhvw yvxzfhv lu gsv xrksvi blf szev gl wlfyov blfi hgzpvh. HP-XVIG{szev_blf_vevi_svziw_zylfg_z_yolxp_xrksvi???}

## Riešenie

Vidím, že sa zmenili len alfanumerické znaky a znaky ako { } a pod. ostali zrejme na svojom mieste, takže nepôjde o transpozičnú, ale stále o jednoduchú substitučnú šifru ako je ROT13, atbash a pod. 
Skopíral som text šifry do https://www.multisolver.de/ a pri ATBASH mám výsledok

    C: Lets coordinate the drop point.
    B: Agreed but we have to be careful. Our cryptographers warned us about this method. They say it wont hold for long.
    C: We dont have time to set up anything better. Come to the usual place in the Pentagon, Stavbarska 42. The bartender will give you the package. 
    B: Fine but if we get compromised because of the cipher you have to double your stakes. SK-CERT{have_you_ever_heard_about_a_block_cipher???}

## Vlajka

    SK-CERT{have_you_ever_heard_about_a_block_cipher???}
