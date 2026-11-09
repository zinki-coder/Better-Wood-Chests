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

def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def planks_palette(planks):
    img = Image.open(io.BytesIO(zf.read(f"assets/minecraft/textures/block/{planks}.png"))).convert("RGBA")
    return img

def otsu(values):
    hist = [0] * 256
    for v in values:
        hist[min(255, int(v))] += 1
    total = len(values)
    sum_all = sum(i * h for i, h in enumerate(hist))
    best, thr, w0, s0 = -1, 0, 0, 0
    for t in range(256):
        w0 += hist[t]
        if w0 == 0:
            continue
        w1 = total - w0
        if w1 == 0:
            break
        s0 += t * hist[t]
        m0 = s0 / w0
        m1 = (sum_all - s0) / w1
        var = w0 * w1 * (m0 - m1) ** 2
        if var > best:
            best, thr = var, t
    return thr

def recolor(img, planks):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    pp = planks.load()
    pw, ph = planks.size
    cand = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            if mx and (mx - mn) / mx < 0.18:
                continue  # Metall (Schloss) unveraendert
            cand.append((x, y, lum((r, g, b))))
    thr = min(100, otsu([c[2] for c in cand]))
    wood = [c for c in cand if c[2] > thr]  # dunkle Pixel (Rand, Innenraum) bleiben wie Vanilla
    ref = sum(c[2] for c in wood) / len(wood)
    for x, y, l in wood:
        a = px[x, y][3]
        base = pp[x % pw, y % ph]
        f = 1 + (l / ref - 1) * 0.6
        px[x, y] = tuple(max(0, min(255, int(base[i] * f))) for i in range(3)) + (a,)
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
    write(f"{D}/advancement/recipes/misc/{cid}.json", {
        "parent": "minecraft:recipes/root",
        "criteria": {
            "has_planks": {"trigger": "minecraft:inventory_changed",
                           "conditions": {"items": [{"items": f"minecraft:{planks}"}]}},
            "has_the_recipe": {"trigger": "minecraft:recipe_unlocked",
                               "conditions": {"recipe": full}}},
        "requirements": [["has_planks", "has_the_recipe"]],
        "rewards": {"recipes": [full]}})
    en[f"block.{MOD}.{cid}"] = name_en
    de[f"block.{MOD}.{cid}"] = name_de
    for suffix in ("", "_left", "_right"):
        src = f"assets/minecraft/textures/entity/chest/normal{suffix}.png"
        img = Image.open(io.BytesIO(zf.read(src)))
        out = f"{A}/textures/entity/chest/{wid}{suffix}.png"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        recolor(img, palette).save(out)

en["container.better-wood-chests.large"] = "Large %s"
de["container.better-wood-chests.large"] = "Große %s"
write(f"{ROOT}/assets/{MOD}/lang/en_us.json", en)
write(f"{ROOT}/assets/{MOD}/lang/de_de.json", de)
write(f"{ROOT}/data/minecraft/tags/block/mineable/axe.json",
      {"values": [f"{MOD}:{w[0]}_chest" for w in WOODS]})
# Vanilla-Truhen aus dem Survival-Crafting entfernen
NEVER = [{"condition": "fabric:all_mods_loaded", "values": ["better-wood-chests-never-installed"]}]
for vanilla in ("chest", "trapped_chest"):
    write(f"{ROOT}/data/minecraft/recipe/{vanilla}.json", {
        "fabric:load_conditions": NEVER,
        "type": "minecraft:crafting_shaped", "category": "misc",
        "key": {"#": "minecraft:barrier"}, "pattern": ["###", "# #", "###"],
        "result": {"id": f"minecraft:{vanilla}"}})
write(f"{ROOT}/data/minecraft/tags/block/guarded_by_piglins.json",
      {"values": [f"{MOD}:{w[0]}_chest" for w in WOODS]})
print("Fertig:", len(WOODS), "Holzarten")
