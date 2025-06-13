from datetime import datetime
from sage.all import GF, EllipticCurve
import json, multiprocessing, os, random

# ── parametre ──────────────────────────────────────────────────────────────
p  = 6277101735386680763835789423207666416083908700390324961279
a  = -3
target_orders   = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                   53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
                   109, 113, 127, 131, 137, 139, 149, 151]

max_b_search    = 1000          # b = 0 … 999
attempts_per_r  = 25            # náhodných pokusov pre každé r
NUM_WORKERS     = 16            # ← sem daj počet threadov
output_filename = "bodymalychradov.json"

# ── worker funkcia – spúšťa sa v každom procese ────────────────────────────
def search_b_worker(b):
    """Vráti dict {r: (x,y)} s nájdenými bodmi pre dané b."""
    Fp = GF(p)
    try:
        E = EllipticCurve(Fp, [-3, b])
    except ArithmeticError:         # singularna krivka
        return {}

    n_E    = E.order()
    result = {}
    for r in target_orders:
        if n_E % r:                 # r nedelí |E|
            continue
        k = n_E // r
        for _ in range(attempts_per_r):
            Q = k * E.random_point()
            if not Q.is_zero() and (r * Q).is_zero():
                x, y = map(int, Q.xy())
                result[r] = (x, y)
                break
    return result

# ── hlavný proces ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_time   = datetime.now()
    manager      = multiprocessing.Manager()
    results      = {str(r): "Not found" for r in target_orders}
    orders_left  = set(target_orders)

    with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
        # imap_unordered → výsledky prichádzajú hneď ako sú hotové
        for res in pool.imap_unordered(search_b_worker, range(max_b_search)):
            # spracujeme dict z jedného b
            for r, (x, y) in res.items():
                if r in orders_left:                 # ak ešte nemáme
                    results[str(r)] = f"{x} {y}"
                    orders_left.remove(r)
                    print(f"✓ našiel som bod rádu {r:<3}  (x = {x}, y = {y})")
            if not orders_left:                      # všetko hotové
                pool.terminate()                     # zastav zvyšné úlohy
                break

    # zápis výsledkov
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=2)

    # čas behu
    elapsed = datetime.now() - start_time
    m, s = divmod(int(elapsed.total_seconds()), 60)
    print(f"\nFinito! Čas trvania: {m}:{s:02d}")
