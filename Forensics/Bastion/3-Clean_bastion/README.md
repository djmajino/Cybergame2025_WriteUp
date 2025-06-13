# Zadanie

EN: The keylogger binary was passed to a malware analyst. Regarding the server, no further changes were detected, so the container was rebuilt and redeployed to a test environment. Ssh to the system. WARNING: be aware that the system is running as a single container for all CTF players, so behave.

SK: Keylogger binárka bola posunutá malvérovému analytikovi. Na serveri už neboli zdetekované žiadne zmeny a tak bol znovu vytvorený a nasadený do testovacieho prostredia. Prihláste sa do systému.

`ssh://exp.cybergame.sk:7009 (ratchet:23ekmnjr4bh5tgvfhbejncidj)`

## Riešenie

Stačí sa teda len prihlásiť na ssh server

```bash
majino@majino:~$ ssh -l ratchet exp.cybergame.sk -p 7009
Welcome, Ratchet!
ratchet@exp.cybergame.sk's password:
Come in and don't be shy

     SK-CERT{bru73_f0rc1n6_u53r5_w0rk5}


3f35af04c9ab:/home/ratchet$
```

## Vlajka

```
SK-CERT{bru73_f0rc1n6_u53r5_w0rk5}
```
