# Zadanie

EN: Inside the quarantined system, dig in and search for any remnants or traces of the attackers.

SK: Ponorte sa do systému a overte či nezostali nejaké stopy po útočníkoch.

`ssh://exp.cybergame.sk:7009`

## Riešenie

Z predošlej úlohy sme prihlásení na server a stačí sa len povŕtať. Prvé čo mi napadlo, je pozrieť, čo všetko nájdem tam kde som.

```bash
3f35af04c9ab:/home/ratchet$ ls -la
total 16
drwxr-sr-x    1 ratchet  ratchet       4096 Apr 22 13:24 .
drwxr-xr-x    1 root     root          4096 Apr 22 13:24 ..
drwxr-sr-x    2 root     ratchet       4096 Apr 22 13:24 .ssh
3f35af04c9ab:/home/ratchet$ cd .ssh
3f35af04c9ab:/home/ratchet/.ssh$ ls -la
total 12
drwxr-sr-x    2 root     ratchet       4096 Apr 22 13:24 .
drwxr-sr-x    1 ratchet  ratchet       4096 Apr 22 13:24 ..
-rw-r--r--    1 root     ratchet        351 Apr 22 13:24 authorized_keys
3f35af04c9ab:/home/ratchet/.ssh$ cat authorized_keys
ecdsa-sha2-nistp256 AAAAvZHODysGbxHo1wGtqbqi1Ffnr2li7j8ov/V26Nt4w/HR26mWOtT/APG1qBilJoVmCQChz/hCWuIWwzqqZNe1BQ== ratchet@infocube
ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBOSeOZtJmXS7zliVg5tEaEk9KvhIRn4S3FBjLuo1s0eUvHi6HkzuLTNXiphR8Lth/DWQNeC/A+meex8Y09RtZQA= hacker-U0stQ0VSVHtoMEx5X00wTGx5X1RIM3lfNHIzXzV0aUxsX2gzUjN9
```

A tu je zaujímavý string obsahujúci U0st, čo je začiatok vlajky.  dekódujeme

```bash
3f35af04c9ab:/home/ratchet/.ssh$ echo U0stQ0VSVHtoMEx5X00wTGx5X1RIM3lfNHIzXzV0aUxsX2gzUjN9 | base64 -d
SK-CERT{h0Ly_M0Lly_TH3y_4r3_5tiLl_h3R3}
```



## Vlajka

```
SK-CERT{h0Ly_M0Lly_TH3y_4r3_5tiLl_h3R3}
```
