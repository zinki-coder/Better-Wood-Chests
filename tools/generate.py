import glob, json, os, sys, zipfile, io
from PIL import Image

MOD = "better-wood-chests"
ROOT = "src/main/resources"

# ============ HIER ANPASSEN ============
# id, English, Deutsch, Planken-Item, Farbe (R, G, B)
WOODS = [
    ("oak",       "Oak Chest",        "Eichentruhe",        "oak_planks",       (162, 130, 78)),
    ("spruce",    "Spruce Chest",     "Fichtentruhe",       "spruce_planks",    (114, 84, 48)),
    ("birch",     "Birch Chest",      "Birkentruhe",        "birch_planks",     (216, 203, 155)),
    ("jungle",    "Jungle Chest",     "Tropenholztruhe",    "jungle_planks",    (160, 115, 80)),
    ("acacia",    "Acacia Chest",     "Akazientruhe",       "acacia_planks",    (186, 99, 54)),
    ("dark_oak",  "Dark Oak Chest",   "Schwarzeichentruhe", "dark_oak_planks",  (66, 43, 20)),
    ("mangrove",  "Mangrove Chest",   "Mangrovenholztruhe", "mangrove_planks",  (117, 54, 48)),
    ("cherry",    "Cherry Chest",     "Kirschholztruhe",    "cherry_planks",    (226, 178, 172)),
    ("pale_oak",  "Pale Oak Chest",   "Blasseichentruhe",   "pale_oak_planks",  (228, 218, 212)),
    ("bamboo",    "Bamboo Chest",     "Bambustruhe",        "bamboo_planks",    (193, 173, 80)),
    ("crimson",   "Crimson Chest",    "Karmesintruhe",      "crimson_planks",   (126, 58, 86)),
    ("warped",    "Warped Chest",     "Wirrtruhe",          "warped_planks",    (52, 122, 116)),
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

def recolor(img, target):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    lums = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and max(r, g, b) and (max(r, g, b) - min(r, g, b)) / max(r, g, b) >= 0.18:
                lums.append(0.299 * r + 0.587 * g + 0.114 * b)
    ref = sum(lums) / len(lums)
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            if mx and (mx - mn) / mx < 0.18:
                continue  # Metall (Schloss) unveraendert
            f = (0.299 * r + 0.587 * g + 0.114 * b) / ref
            px[x, y] = tuple(min(255, int(c * f)) for c in target) + (a,)
    return img

zf = zipfile.ZipFile(find_jar())
en, de = {}, {}

for wid, name_en, name_de, planks, color in WOODS:
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
        recolor(img, color).save(out)

write(f"{ROOT}/assets/{MOD}/lang/en_us.json", en)
write(f"{ROOT}/assets/{MOD}/lang/de_de.json", de)
write(f"{ROOT}/data/minecraft/tags/block/mineable/axe.json",
      {"values": [f"{MOD}:{w[0]}_chest" for w in WOODS]})
print("Fertig:", len(WOODS), "Holzarten")
