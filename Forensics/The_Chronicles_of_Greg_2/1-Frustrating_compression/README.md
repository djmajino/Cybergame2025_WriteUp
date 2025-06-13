# Zadanie

EN: Greg didn’t think much of the file when it showed up—just a zipped folder with a generic name. But the moment he opened it, he realized it was something else entirely. One archive led to another, then another, each packed with more layers, more files, more dead ends. His system crawled under the load, but he kept digging, knowing this wasn’t random. Buried somewhere in the mess was a single file—different, deliberate, hidden for a reason. It was a challenge meant for someone with his skills. And Greg wasn’t about to back down.

SK: Keď sa súbor objavil, Greg si o ňom veľa nemyslel – len zazipovaný priečinok s bežným názvom. Ale v momente, keď ho otvoril, si uvedomil, že je to niečo úplne iné. Jeden archív viedol k ďalšiemu, potom k ďalšiemu, každý plný ďalších vrstiev, ďalších súborov, ďalších slepých uličiek. Jeho systém sa pod ťarchou plazil, ale on pokračoval v kopaní, vediac, že to nie je náhoda. Niekde v tom chaose bol pochovaný jeden súbor – iný, zámerne skrytý z nejakého dôvodu. Bola to výzva pre niekoho s jeho schopnosťami. A Greg sa nehodlal vzdať.

**Súbory**

- 00114021.tar

## Riešenie

Táto úloha bola jedna z najzbytočnejších úloh aké tu boli. Nazvyme to čisto mechanickou úlohou. V príncípe je každému jasné, čo treba urobiť, len to treba urobiť. Ale o čo vlastne ide? Máme k dispozícii tar archív, ktorý obsahuje v sebe ďalšie archívy a každý z nich obsahuje ďalšie a ďalšie a tak ďalej a v archívoch sa nachádzajú aj súbory s príponou flag... Všetky okrem jedného a to ich je asi niekolko stoviek tisíc obsahujú garbage.

```bash
#!/bin/bash
set -e

ROOTDIR="$(pwd)"
OUTDIR="$ROOTDIR/out"

mkdir -p "$OUTDIR"

HASHFILE=$(mktemp)
trap 'rm -rf "$HASHFILE"' EXIT

process_dir() {
    local DIR="$1"

    for file in "$DIR"/*; do
        [ -e "$file" ] || continue

        case "$file" in
            *.zip|*.ZIP|*.tar|*.tar.gz|*.tgz|*.tar.bz2|*.tbz2|*.rar|*.RAR|*.7z|*.7Z)
                ARCHIVE_HASH=$(sha256sum "$file" | awk '{print $1}')
                if grep -q "$ARCHIVE_HASH" "$HASHFILE"; then
                    continue
                else
                    echo "$ARCHIVE_HASH" >> "$HASHFILE"
                fi

                NEWDIR="${file}_unz"
                mkdir -p "$NEWDIR"

                case "$file" in
                    *.zip|*.ZIP)
                        unzip -qq "$file" -d "$NEWDIR" >/dev/null 2>&1 || true
                        ;;
                    *.tar)
                        tar -xf "$file" -C "$NEWDIR" >/dev/null 2>&1 || true
                        ;;
                    *.tar.gz|*.tgz)
                        tar -xzf "$file" -C "$NEWDIR" >/dev/null 2>&1 || true
                        ;;
                    *.tar.bz2|*.tbz2)
                        tar -xjf "$file" -C "$NEWDIR" >/dev/null 2>&1 || true
                        ;;
                    *.rar|*.RAR)
                        unrar x -inul "$file" "$NEWDIR" >/dev/null 2>&1 || true
                        ;;
                    *.7z|*.7Z)
                        7z x -y -o"$NEWDIR" "$file" >/dev/null 2>&1 || true
                        ;;
                esac

                process_dir "$NEWDIR"
                ;;
            *.flag)
                grep -o 'SK-CERT{[^}]*}' "$file" 2>/dev/null | while read -r line; do
                    echo "$file: $line"
                done
                ;;
            *)
                if [ -d "$file" ]; then
                    process_dir "$file"
                fi
                ;;
        esac
    done
}

tar -xf "00114021.tar" -C "$OUTDIR"
process_dir "$OUTDIR"
```

Spustiť tento skript a po niekolkých desiatkách minút (možno aj pár hodinách, záleží od stroja) by malo byť všetko rozbalené. Skript by mal preskakovať rozbaľovanie rovnakých archívov ak narazí na rovnaký hash a ešte má vypnuté výpisy okrem nálezu vlajky pre optimalizáciu. Just in case.

Mne na Lenovo Thinkpad P15v Gen 2 bežal skript 2 hodiny a 15 min, kým hitol vlajku

> /mnt/e/CTFs/Cybergame2025/greg2/1/out/00114020.rar_unz/00114019.tar_unz/00114017.zip_unz/00113990.7z_unz/00113751.7z_unz/00113701.zip_unz/00111534.zip_unz/00108902.7z_unz/00108141.tar_unz/00105433.zip_unz/00096327.zip_unz/00089244.7z_unz/00012377.rar_unz/00007607.7z_unz/2NKY5QZQw94j.flag: SK-CERT{n33dl3_1n_h4yst4ck}

## Vlajka

    SK-CERT{n33dl3_1n_h4yst4ck}
