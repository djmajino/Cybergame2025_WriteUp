# Zadanie

EN: You've been contacted by a movie production company that has been hit by ransomware. They need your help recovering the script for the next episode of a long-awaited series. It's urgent—millions (and possibly billions) of impatient fans are waiting.

SK: Boli ste kontaktovaní filmovou produkčnou spoločnosťou, ktorá bola zasiahnutá ransomware. Potrebujú vašu pomoc pri obnove scenára pre nasledujúcu epizódu dlho očakávaného seriálu. Je to naliehavé—milióny (a možno miliardy) netrpezlivých fanúšikov čakajú.

**Súbory**

- recovery_1.zip

## Riešenie

Archív obsahoval 

- ransomware.py

- files\inescapable_storyception_of_doom.txt.enc

- files\slon.png.enc

**Kód ransomware.py**

```python
import os
from itertools import cycle


TARGET_DIR = "./files/"

def encrypt(filename, key):
    orig_bytes = None
    encrypted_bytes = bytearray()
    with open(TARGET_DIR + filename, "rb") as f:
        orig_bytes = bytearray(f.read() )
    encrypted_bytes = bytes(a ^ b for a, b in zip(orig_bytes, cycle(key)))

    with open(TARGET_DIR + filename, "wb") as f:
        f.write(encrypted_bytes)

    os.rename(TARGET_DIR + filename, TARGET_DIR + filename + ".enc")

    print(f"[+] Encrypted {TARGET_DIR + filename}")


if __name__=="__main__":
    key = os.urandom(16)
    for subdir, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            print(f"file name: {file}")
            encrypt(file, key)
```

Zo skriptu vieme, že kľúč je 16 bajtový a každý 16 bajtový blok súbory je xorovaný týmto kľúčom. Ak poznáme 16 bajtov pôvodného súboru, dokážeme xorom derivovať pôvodný kľúč. Našťastie PNG súbory majú rovnakú 16 bajtovú hlavičku, takže urobíme xor medzi prvými 16 bajtami zakódovaného PNG a 16 bajtami známej png hlavičky 

> ```
> enc 0A D2 9C D9 08 53 D5 65 21 BE 0C BF B0 36 1D 07
> 
> XOR
> 
> png 89 50 4E 47 0D 0A 1A 0A 00 00 00 0D 49 48 44 52
> 
> ===============
> 
> key 83 82 d2 9e 05 59 cf 6f 21 be 0c b2 f9 7e 59 55
> ```

Kľúč je teda 

> 83 82 d2 9e 05 59 cf 6f 21 be 0c b2 f9 7e 59 55

Týmto kľúčom dešifrujeme text pomocou xoru

Vieme to skriptom

```python
import os
from itertools import cycle

FILES_DIR = "recovery_1/files"

#Načítaj zašifrovaný PNG a získaj XOR kľúč
PNG_HEADER = b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR'
enc_png_path = os.path.join(FILES_DIR, "slon.png.enc")

with open(enc_png_path, "rb") as f:
    encrypted_header = f.read(len(PNG_HEADER))

# XOR dekódovanie známeho PNG headera
xor_key = bytes([a ^ b for a, b in zip(encrypted_header, PNG_HEADER)])
print(f"[+] Získaný XOR kľúč: {xor_key.hex()}")

# Dešifrovanie všetkých súborov v adresári
for filename in os.listdir(FILES_DIR):
    if not filename.endswith(".enc"):
        continue

    enc_file_path = os.path.join(FILES_DIR, filename)
    dec_file_path = os.path.join(FILES_DIR, filename[:-4])  # odstráni '.enc'

    with open(enc_file_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = bytes(a ^ b for a, b in zip(encrypted_data, cycle(xor_key)))

    with open(dec_file_path, "wb") as f:
        f.write(decrypted_data)

    print(f"[+] Dešifrovaný súbor uložený ako: {dec_file_path}")
```

alebo samotný enkódovaný text pomocou cyberchef

[CyberChef](https://gchq.github.io/CyberChef/#recipe=XOR(%7B'option':'Hex','string':'83%2082%20d2%209e%2005%2059%20cf%206f%2021%20be%200c%20b2%20f9%207e%2059%2055'%7D,'Standard',false)&input=oKKA92Yy7w5P2iz/lgwtLKPjvPolLacKAfdi14odOCXi4L77JQq7AFPHb9eJCjA67aK9%2BCUdoABMtEXG2Q0tNPH2t/olNaYERJ5t3IBeNiHr56C%2BUSyqHEXfdYjZLDA26KKw/3c%2BqgsB12LGll4UOvH2q3yFwLxPU9Fj39VeKTTt9qHyYCq8T0DQaJKRETUx6uy1vmR5qANOyWXcnl4qJeLht75nLL0dSMpjnPN0u9Ufz73scSDuT2zRfsaAUnki5qK18XEtrk9G0S2SrRY8deH3oOxsLaBPUcxjwpEbOiyj66G%2BcDepAE3aZdyeUHkB6%2Beg%2B%2BfZVhwNnnna1V41POjn/r5keftdBJ5v2pgQOjCj7bS%2Bazi9HUDKZcScXjo67%2B6z7nY87wZHnnvX2Ro2O2ECS%2BolOKwbAdhtwY1fu9UeiNh8hcWYDkjK7jJtCTE0973yyW04u09F0WnB2QoxNPeit%2BhgN%2B8CRN9intksMDbovfN8hcTFZWPLeJKbGz868efy02oruxYB3WPHlRp5JfHtpvt2LeNPVdZpy9kJPCfmorPydzyuC1ieZdzZCjEwo/Gi/2Y8vAdIziCSkQsrIe/rvPklLacdTstr2tkfeSLs8L/2ajWqT1LWbcKcGnkm9vGi92YwoBpS0nWSlRcyMKPGs/AlEa4dTNFiUHnnKnXh57PsYXfFZXXWacvZGzQw8eW3%2BiUwoU9AnmjblBs3JurtvL5oOKsKAdtixpAMPDn6or34JSmjAFWeaNePFzow8Kzy23M8vRZV1mXcnl4uNPCioet2KaYMSNF5wZUHeTbs7KT7azCqAVWQLPPZKwoXo%2Bag93M87wlN0W3GnBp5N/qivv9nPKMKRZ7uMmUqMTzwooX3aTXvLUSeRd%2BJESsh4uymvkk4uwpTkO4yZF4UOvH2q753PK4MSdtokp8RK3Xq9vyUDwq6C0XbYt6AUnkw9eeg53ExpgFGnnzTjA08Ma2ik75nNqACSNBrko8RMDbmorf9bTaqCxu0BlB54g4w7%2B7%2BvnI8owMNnnvXlRK71SWiu/glMLtPSM1iUHnnLXXR67H1JTihCwHzY8CNB3V14OOn%2BW0t7wBP3WmSmBk4PO2iu/AlNLZPT99%2BwJgKMCPmorz7cXgt77y0BvuNXi408GBSOCUKmyBz5yz%2BtiwdeaP2uvslL6YDTd9l3NkJMTqj5Lf7YSrvAE%2BefN6WCjU87eehsiU0pgNKzSzGnBAqPOzs8vhqK%2B8fTslpwNVeODvnorX7cSrvHU7Hbd6NFzwmo%2Bek%2B3cg7xtI02mSihE0MOzst75iOLwfUp5ox4sXNzKj4/LtYDi8AE%2BeatuXHzUwrYjYfIXFiw5M0CzbjVJ5GOzwpucpu0/yAexl0ZJePif277DyYD3jT8M%2BkMWcXj855vXy92stoE9Ann7XmgsrJur0t75rOL0dQMplxJxeLSfi8vy%2BTTwt77jNLNCcGzd18Oem6mw3qE9V1mXB2QspdeXtoL52PK4cTtB/nBv%2BxF%2BJ0abxdyDvI07MaJKYDikw4vC3%2BiU9vQ5M33jbmh81Ofqu8upyML0DSNBrkpEXKnXu7bzxaTaoGkSeYceKCjg26%2Bf8vufZUzZOyyzTixt5O%2Bz18vdrKqYLRJ5tkooKNif6YFI4JS6mG0nXYpKYXioh7PCrfIX/7xhIymTbl144dfD2vex8eC3vvLQG5ZAKMXXioqHwZCnjT3PXb9nZHzcxo8%2B97HEg7xhEzGmSgB83Pubm8vdrLaBPQNBjxpEbK3Xv46v7d3mgCQHMadOVFy0suaKm9mAg7xhEzGmSlxEudeDqs%2BxkOrsKU80s25deOHXX1PLtbTa4T0DcY8eNXi0i7KKl7Gwtqh1Snm/AnB8tPO3l8v8lOq4dVdFj3NkfOzr29vLMbDqkT0DQaJK0ESsh%2Bq7y6XcwuwZP2SzT2Q06J%2Brypr5kO6AaVZ5e25oVeTTt5vLTaiu7FgHcaduXGXkh8eOi7mA97wZPnm2Sigo2J/pgUjgPU%2B09SN1nntkKMTzworvtJT6qG1XXYtXZHTY75feh92s%2B7k9onnjakBAydcqiuOt2Le8NU9Fn19kTIHXh8LP3a3jvJsM%2Bld/ZDTww6uy1vmYrqgtIyn%2BSkBB5OPqit%2BdgKu6NoSMGuKsXOj6j8b7/dSmqCwHzY8CNB3ki6va6vnExqk9Dy37AkAo2e6NgUgJWN64fAdF5xtkRP3Xq9vO%2BUjwt77jMaZKXES118eez8il5ggBTynWe2Qk8twMboPslNKobQJN%2B15gSd3XX6rPq59lWHAHMadOVGyt19%2Bqz8CUrqg5NkCzlnF4%2BOvf2s75nK6oOSp542pxeKzDg96DtbC%2BqT03RY8LZESt19OcwHpw1o09D2yzGix8pJebm8vdrea4BAddi1JAQMCHmorH2ZDChT07YLMGNESss7%2Bu8%2B3Z5uAdEzGmSnAg8J/qipvdoPO8YRJ5pwZofKTCvorvq59lWHAHUecGNXjg77Pa6%2B3d5vwNOyizGjhcqIaJgUgMPU5sHRMcs3pwfKSGj9rrsaiyoBwHfLNyYDCs09%2Buk%2ByUpoB1V32Ce2RI4O%2BfrvPklMKFPQJ5i3ZAMdCHr57/7YXmrClXbb8aQCDx18Pa97Hx3xWXDPpDgkB0yeaP1uuclOKJPaJ5715gMMDvkorO%2BYzyrAFPfLNOXGnk74vCg/3EwoQgB23rXiwctPerstb5MeasAAddikphePifi9LfyaSDvGU7Xb9fGnNnIiYiA92Yy7wNIyizT2R0wMuLwt%2BpxPO8YSMpkkphePzni77e%2BcTGuGwHNfNeVEjwxo%2B2n6iW7T/N19kn/vFC71R6iMB6ZG6oMQMt/19kJPLcDG6D7JTegGAHXYpKYXj4w7fC3vmk4tgpTkiz/lgwtLK2igepqK7ZPbdF%2B1hv%2BwCaj5bfqcTChCAHaacGJGys09%2Bf8vk08Le%2B4zSzGkQw2Iurstb5gL6odWJ54wJYOPHXr5zAenCrvCE7KLNONXiwmrWBSAw9TjBpEnmHHihc6NO%2Biv/FrLa4IRIQsxpEbIHXm8bH/dTzvDgHWaduKCnkl7%2B2msiU47x1O023cjRc6dfD3sO5pNrtPVtZpwJxeFDrx9qu%2BZDWiAFLKLNmQDSow8KKzvmk4oh8Nnm3cnV44de73ofdmOKNPT8th0JwMeTvi8KD/cTyrT0PHLP%2BWDD407aKU7GA8og5PnnzemAcwO%2BSiuvdoKqoDR5583pgHMDvkopXxYXmmAVLXaNfZCjEwo/Gm8Xcg7wBHnl7bmhV5NO3m8tNqK7sWD7QG9JAQODnv%2B/6%2BcTGqFgHMadOaFjwxo/a6%2ByU6oB1EhCzT2RIwIffut75hLLwbWJ5%2B3ZYTeSLq9rq%2BZHm7FlHbe8CQCjwnr6Kz8GF5oAEB13ic11B5NKPxsexsKbtPVdd43pwaebcDHoD3ZjLvDk/aLP%2BWDC0so%2BO8%2BiUtpwoB92LXih04JeLgvvslCrsAU8dv14kKMDrtor34JR2gAEyQ7jJkdFO3Ax6F/2wt409z12/Z11B3dffqs%2Brn2VYcAcpk19kQODjmor34JS2nBlKef8aWDCB7o8Og%2ByUuqkEPkCzTixt5Iuais/J3PK4LWJ5txtkKMTCj57z6OrtP8iu07jJlMDZ5o8%2B97HEg4U911mXB2RcqO2ECS%2BolLacKAdti1tdeDT3q8fL3dnmlGlLKLMaRG3km9%2BOg6iU2qU9V1mmSnBA9twMbob5nOKwEUspjwIBQu9UeiNjNcD2rCk/SdZ7ZCjEwo/Gx7Gwpu09H0mXCiRs9der2oftpP%2B8AUdtikpgQPXX36rfnJS6qHUSef8eaFTwxo%2Bu86mp5uwdAyizBjRErLKP2vfEreYEAVp542pwHeSLm8Le%2Bcji7DEnXYtXZCjEw7vG38nM8vE9T223W2QoxMKPxpvF3IO8AR5542pwTKjDv9LftJTuqBk/ZLMGMHTIw56K78HE27w4BzXjdiwd5NOHtp%2BolLacKTM1p3o8bKnX046b9bTChCAHKZNeUDTw59eehfIX/xWXDPpDhrTEJdGECT752Or0KQNNp1tkzNif3%2B/6%2BZjW6G0LWZdyeXjE88KK0/2Y84U/DPpD7jZzZzPCioepqK6YKUp5t3pVeLT3moqX/fHmrAFbQLVB541Nfwuy2vnExqgENnm2SjxEwNuZgUgp8NrodAchj25obdXXn57PsJSuqDkXbflB56io0%2BvHy8XAt7wNOy2iI83S71R/Vs/dxu0/JAclk041eLT3morr7aTXvDkyeRZKLGzgx6uy1oefZUmUr7Xjdiwd5Gezwtr5iOLwfUpAsUHniFzphAnS%2BcTGqT1PbbdacDHk94vHy/GA6oAJEnn/XlRh0NPTjoPskeY4NTsx4kpcfKyfi9rvoYHjvLmPxXubZMBgH0cOG11Mc7o2hIwa4qxc6PqPxv/d3MrxBAVyMLq0RNnXv46b7KXmlDkLVbcGKUHkco/G%2B93UpqgsB32KSmBAtPK7ss%2Bx3OLsGV9ss1YsbNzTn5/L3ay2gT1jRecDZEzwh4vK68XcwrA5NnnzTlwoqe2ECT5QPG4AgbJAGuLwIPCf69rr3az7vHUTNacaKUFNfzu2g6ny7T/ZSnm7TmhV5PO2isPthd8Vlwz6Q/5YMLSyiopX7cXm6HwCeW9fZGTYh9%2BPy7XE2v09yymPAgF4VOvHm8vxgP6AdRJ5k19kKKzTz8fLrdnmmAQHfLMCcHSwn8Ouk%2B%2BfZW42hIwa4G/7FG8zSl7AlF5onAetEnNk3u9Uaz/LaSheKQcM%2BkbjznNnJYQJ00W44tkMB1GnXg1B5E%2Brst7AlDq4BT98s1ZwKeSXi7LH/bjy8UMM%2BkbjznNnJ2uez9it5nw5P3W3ZnA15Juz3vPolKq4JRJDuMmR0UxTwoqb2YCDvA0TfetfVXjh15eu163c87xhAym/anA15M/Htv75keasOU9Us0ZYMNzDxrPLXcX68T0Cef9GLFykh9PC76mAr4WUr9mPenRc3MqPj8u5gN%2BFlK%2B1h25UXNzKtiNjKanmtCgHdY9yNFzcg5uYwHqN5pgEBymTX2Q0tOvH78ulsLacGT5542pxeKjDy97fyJS6mG0nXYpKNFjx18/C373A8o09O2CzGkRt5OvHrtfdreb0KQ9Fjxtd0U1yKi4HVKBqKPXXFO8DICGhh792gqmts/wJWin6BphhpJ9y1uq1abPhbU4lxu/N0)

Dostaneme:

```
# Rick and Morty and the Inescapable Storyception of Doom
It started like any other Tuesday: Rick barged into Morty’s room, pantsless and holding a glowing space burrito.

“Morty! Morty, we gotta go! The burrito prophecy is unfolding. There’s, uh, like, a 42% chance of narrative collapse if we don’t act fast!”

“Wait—what? What does that even mean, Rick?!”

But before Morty could protest, they were already in the spaceship, hurtling through a wormhole shaped suspiciously like Dan Harmon’s beard.

They emerged in a dimension made entirely of plot devices. Everything was suspiciously convenient. A USB drive floated by labeled “This Will Be Important Later.” Morty reached for it.

Suddenly, everything paused. A booming voice echoed:

“Well, well, well… if it isn’t Rick and Morty, caught once again in my narrative net!”

It was… STORY LORD, the villain who feeds on plotlines, milks tension for power, and gets royalties every time someone gasps during a season finale.

“Damn it, Morty,” Rick grumbled, “we flew into a recursive narrative trap. He’s been setting this up for seasons.”

Story Lord appeared dramatically, twirling his monologue mustache. “You are now inside a story… within a story… within a story!”

With a snap, Rick and Morty were yanked into another layer of reality: they were now characters in a TV show about two writers creating a cartoon about Rick and Morty, writing a script about Rick and Morty being trapped in a story…

"Rick, this is getting confusing! I think I just broke my brain! I’m seeing credits in my eyes!”

Rick slapped Morty with the burrito. “Snap out of it! We’re not real, Morty, we’re meta-real. That’s realer than real. We gotta break the recursive loop or we’ll be trapped in an infinite chain of storylines where every time we escape, it’s just another plot twist!”

They leapt through a narrative portal, landing in a noir-themed detective story.

“Rick, why am I wearing a fedora and narrating everything I do in a gravelly voice?”

Rick lit a cigarette with a flame that spelled out “THEME.” “Because we’re now in a genre layer, Morty. Story Lord’s getting desperate. He’s throwing every trope he’s got at us.”

Cue musical montage: they escape a heist plot, a romantic subplot where Morty almost kisses a lamp, and a musical number narrated by Morgan Freeman playing himself playing God inside the story of Rick and Morty.

Finally, they reached the core: a little dusty room with a typewriter, and on it... a script titled “Rick and Morty and the Inescapable Storyception of Doom.”

“Wait, Rick... that’s the name of this story. Are we... are we already at the end?”

“No, Morty. This isn’t the end. This is just the start of the end’s backstory.”

Suddenly, the script flipped itself open and they were sucked into that story too. Now they were watching themselves read the story of themselves being sucked into a story about themselves watching themselves…

“STOP!” screamed Morty, clutching his face. “It’s stories all the way down!”

And then, a voice—your voice, dear reader—says out loud:

“Wait… what the hell am I reading?”

Story Lord gasps. “No… the reader has become self-aware! Abort narrative! ABORT NARRATIVE!”

Rick smirks. “Too late, jackass. I slipped an anti-narrative grenade into your metaphorical pants.”

BOOM.

Everything resets.

Morty’s back in bed.

“Morty! Get up! We gotta stop Story Lord before he traps us in a recursive—”

“NOPE. NUH UH. I’M DONE.”

“…Okay, jeez. Fine. Wanna get pancakes?”

“Yeah. Pancakes sound safe.”

As they leave, a figure watches from a dark corner. It's a scriptwriter.

Holding a pen.

Smiling.

To be continued… in the story within the sequel within the prequel of the origin reboot.

            SK-CERT{7r1v14l_r4n50mw4r3_f0r_7h3_574r7}    
```

## Vlajka

```
SK-CERT{7r1v14l_r4n50mw4r3_f0r_7h3_574r7}
```
