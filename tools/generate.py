import glob, json, os, sys, zipfile, io
from PIL import Image

MOD = "better-wood-chests"
ROOT = "src/main/resources"

# ============ HIER ANPASSEN ============
# id, English, Deutsch, Planken-Item (Farbe und Struktur kommen von den Brettern)
WOODS = [
    ("oak",       "Oak Chest",        "Eichentruhe",        "oak_planks"),
    ("spruce",    "Spruce Chest",     "Fichtentruhe",       "spruce_planks"),
    ("birch",     "Birch Chest",      "Birkentruhe",        "birch_planks"),
    ("jungle",    "Jungle Chest",     "Tropenholztruhe",    "jungle_planks"),
    ("acacia",    "Acacia Chest",     "Akazientruhe",       "acacia_planks"),
    ("dark_oak",  "Dark Oak Chest",   "Schwarzeichentruhe", "dark_oak_planks"),
    ("mangrove",  "Mangrove Chest",   "Mangrovenholztruhe", "mangrove_planks"),
    ("cherry",    "Cherry Chest",     "Kirschholztruhe",    "cherry_planks"),
    ("pale_oak",  "Pale Oak Chest",   "Blasseichentruhe",   "pale_oak_planks"),
    ("bamboo",    "Bamboo Chest",     "Bambustruhe",        "bamboo_planks"),
    ("crimson",   "Crimson Chest",    "Karmesintruhe",      "crimson_planks"),
    ("warped",    "Warped Chest",     "Wirrtruhe",          "warped_planks"),
]
# =======================================

def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def find_jar():
    for j in glob.glob("/workspaces/**/.gradle/loom-cache/**/minecraft-clientOnly-*26.1.2.jar", recursive=True):
        if "sources" not in j:
            return j
    sys.exit("Minecraft-Jar nicht gefunden")

import bisect

def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def planks_palette(planks):
    img = Image.open(io.BytesIO(zf.read(f"assets/minecraft/textures/block/{planks}.png"))).convert("RGBA")
    pix = [p[:3] for p in img.getdata() if p[3] > 0]
    pix.sort(key=lum)
    return pix

def recolor(img, palette):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    wood = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            if mx and (mx - mn) / mx < 0.18:
                continue  # Metall (Schloss) unveraendert
            wood.append((x, y, a, lum((r, g, b))))
    vals = sorted(t[3] for t in wood)
    n = len(vals)
    for x, y, a, l in wood:
        lo, hi = bisect.bisect_left(vals, l), bisect.bisect_right(vals, l)
        rank = (lo + hi) / 2 / n
        idx = min(len(palette) - 1, int(rank * len(palette)))
        px[x, y] = tuple(palette[idx]) + (a,)
    return img

zf = zipfile.ZipFile(find_jar())
en, de = {}, {}

for wid, name_en, name_de, planks in WOODS:
    palette = planks_palette(planks)
    cid = f"{wid}_chest"
    full = f"{MOD}:{cid}"
    A = f"{ROOT}/assets/{MOD}"
    D = f"{ROOT}/data/{MOD}"
    write(f"{A}/blockstates/{cid}.json", {"variants": {"": {"model": f"{MOD}:block/{cid}"}}})
    write(f"{A}/models/block/{cid}.json", {"textures": {"particle": f"minecraft:block/{planks}"}})
    write(f"{A}/models/item/{cid}.json", {"parent": "minecraft:item/template_chest",
          "textures": {"particle": f"minecraft:block/{planks}"}})
    write(f"{A}/items/{cid}.json", {"model": {"type": "minecraft:special",
          "base": f"{MOD}:item/{cid}",
          "model": {"type": "minecraft:chest", "texture": f"{MOD}:{wid}"}}})
    write(f"{D}/recipe/{cid}.json", {"type": "minecraft:crafting_shaped", "category": "misc",
          "key": {"#": f"minecraft:{planks}"}, "pattern": ["###", "# #", "###"],
          "result": {"id": full}})
    write(f"{D}/loot_table/blocks/{cid}.json", {"type": "minecraft:block", "pools": [{
          "bonus_rolls": 0.0,
          "conditions": [{"condition": "minecraft:survives_explosion"}],
          "entries": [{"type": "minecraft:item",
                       "functions": [{"function": "minecraft:copy_components",
                                      "include": ["minecraft:custom_name"], "source": "block_entity"}],
                       "name": full}],
          "rolls": 1.0}], "random_sequence": f"{MOD}:blocks/{cid}"})
    en[f"block.{MOD}.{cid}"] = name_en
    de[f"block.{MOD}.{cid}"] = name_de
    for suffix in ("", "_left", "_right"):
        src = f"assets/minecraft/textures/entity/chest/normal{suffix}.png"
        img = Image.open(io.BytesIO(zf.read(src)))
        out = f"{A}/textures/entity/chest/{wid}{suffix}.png"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        recolor(img, palette).save(out)

write(f"{ROOT}/assets/{MOD}/lang/en_us.json", en)
write(f"{ROOT}/assets/{MOD}/lang/de_de.json", de)
write(f"{ROOT}/data/minecraft/tags/block/mineable/axe.json",
      {"values": [f"{MOD}:{w[0]}_chest" for w in WOODS]})
print("Fertig:", len(WOODS), "Holzarten")
