"""Ingredient matching, with explicit alternatives and optional items."""
import csv
import re
import unicodedata
from pathlib import Path
from functools import lru_cache

DATA = Path(__file__).parent / 'data'
ALIASES = {
    'tomatoes':'tomato', 'onions':'onion', 'eggs':'egg', 'potatoes':'potato',
    'carrots':'carrot', 'plantains':'plantain', 'bananas':'banana', 'peas':'pea',
    'cucumbers':'cucumber', 'sardines':'sardine', 'prawns':'shrimp', 'shrimps':'shrimp',
    'bell peppers':'bell pepper', 'green peppers':'green bell pepper', 'red peppers':'red bell pepper',
    'tatashe':'bell pepper', 'rodo':'hot pepper', 'ata rodo':'hot pepper',
    'scotch bonnet':'hot pepper', 'scotch bonnet pepper':'hot pepper', 'habanero':'hot pepper',
    'chilli':'hot pepper', 'chili':'hot pepper', 'chilli pepper':'hot pepper',
    'ground pepper':'hot pepper', 'fresh pepper':'hot pepper', 'black eyed peas':'beans',
    'black eyed beans':'beans', 'brown beans':'beans', 'honey beans':'beans',
    'maggi':'seasoning cube', 'knorr':'seasoning cube', 'bouillon cube':'seasoning cube',
    'seasoning cubes':'seasoning cube', 'stock cube':'seasoning cube', 'bouillon cubes':'seasoning cube',
    'salted butter':'butter', 'all purpose flour':'flour', 'plain flour':'flour',
    'instant yeast':'yeast', 'active dry yeast':'yeast', 'self rising flour':'self raising flour',
    'bicarbonate of soda':'baking soda', 'sodium bicarbonate':'baking soda', 'koun':'baking soda',
    'curry':'curry powder', 'titus':'mackerel', 'titus fish':'mackerel', 'panla':'stockfish',
    'iru':'locust beans', 'dawadawa':'locust beans', 'locust bean':'locust beans',
    'ugwu':'ugu', 'pumpkin leaves':'ugu', 'water leaves':'waterleaf', 'okro':'okra',
    'ponmo':'cow skin', 'pomo':'cow skin', 'kpomo':'cow skin', 'shaki':'tripe',
    'okazi':'afang leaf', 'afang leaves':'afang leaf', 'bitter leaves':'bitter leaf',
    'egusi seeds':'egusi', 'melon seeds':'egusi', 'ehu':'calabash nutmeg',
    'dried shredded cassava':'abacha', 'nkanwu':'potash', 'oats':'oatmeal', 'oat meal':'oatmeal',
    'spagetti':'spaghetti', 'sweetcorn':'sweet corn', 'ground beef':'minced beef',
    'irish potato':'potato', 'long grain rice':'rice', 'parboiled rice':'rice', 'white rice':'rice',
    'basmati rice':'rice', 'oil':'cooking oil', 'sunflower oil':'sunflower oil',
    'breadcrumbs':'breadcrumb', 'spring onions':'spring onion', 'banana leaves':'banana leaf',
    'moi moi leaves':'moi moi leaf', 'gizzards':'chicken gizzard', 'chicken gizzards':'chicken gizzard',
}
# One-way category matches: a specific ingredient can satisfy a generic
# requirement, but a generic ingredient cannot prove a specific one is available.
PARENTS = {
    'vegetable oil': {'cooking oil'}, 'olive oil': {'cooking oil'},
    'sunflower oil': {'cooking oil','vegetable oil'}, 'canola oil': {'cooking oil','vegetable oil'},
    'groundnut oil': {'cooking oil','vegetable oil'}, 'coconut oil': {'cooking oil'},
    'red bell pepper': {'bell pepper','pepper'}, 'green bell pepper': {'bell pepper','pepper'},
    'yellow bell pepper': {'bell pepper','pepper'}, 'bell pepper': {'pepper'},
    'hot pepper': {'pepper'}, 'black pepper': {'pepper'}, 'ofada rice': {'rice'},
    'mackerel': {'fish'}, 'catfish': {'fish'}, 'tilapia': {'fish'},
    'sardine': {'fish'}, 'smoked fish': {'fish'}, 'dried fish': {'fish'},
    'smoked catfish': {'smoked fish','fish'}, 'stockfish': {'dried fish','fish'},
    'minced beef': {'beef'}, 'bread flour': {'flour'},
}
# Pantry ingredients do not establish that a user has a dish's main ingredients.
PANTRY = {'water','salt','pepper','hot pepper','black pepper','bell pepper','red bell pepper',
          'green bell pepper','yellow bell pepper','cooking oil','vegetable oil','palm oil',
          'olive oil','coconut oil','sunflower oil','canola oil','groundnut oil','sesame oil',
          'seasoning cube','sugar','onion','garlic','ginger','curry powder','thyme'}

def normalize(value):
    text = unicodedata.normalize('NFKD', value.lower())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'[^a-z0-9 ]',' ',text)
    text = ' '.join(text.split())
    return ALIASES.get(text, text)

def parse_ingredients(value):
    parts = re.split(r'[,;\n]+|\band\b', value) if isinstance(value,str) else value
    return {n for part in parts if (n := normalize(part))}

def groups(text):
    return [tuple(normalize(x.strip()) for x in g.split('/')) for g in text.split(';') if g.strip()]

@lru_cache(maxsize=1)
def load_recipes():
    with (DATA/'Nigerian meals.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))[1:]
    mapping = {}
    for line in (DATA/'ingredient_requirements.txt').read_text().splitlines():
        if not line or line.startswith('#'): continue
        row, req, opt = line.split('|')
        if int(row) in mapping: raise ValueError(f'Duplicate mapping: {row}')
        mapping[int(row)] = (groups(req),groups(opt))
    if set(mapping) != set(range(1,len(rows)+1)):
        raise ValueError('Recipe CSV and ingredient mapping are out of sync')
    return [dict(id=i, name=r[0].strip(), original_ingredients=r[1].strip(), instructions=r[2].strip(),
                 required=mapping[i][0], optional=mapping[i][1]) for i,r in enumerate(rows,1)]

def satisfies(item, group):
    return any(g == item or g in PARENTS.get(item,set()) for g in group)

def label(group):
    return ' or '.join(group)

def recommend(ingredients, assume_water=True, min_match=0.0, limit=12):
    user = parse_ingredients(ingredients)
    if not user: return []
    available = user | ({'water'} if assume_water else set())
    results = []
    for recipe in load_recipes():
        required = recipe['required']
        matched, missing, optional_missing = [], [], []
        used = set()
        for group in required:
            hits = {item for item in available if satisfies(item,group)}
            if hits:
                matched.append(label(group))
                used.update(hits & user)
            else: missing.append(label(group))
        for group in recipe['optional']:
            if not any(satisfies(item,group) for item in available): optional_missing.append(label(group))
        # Avoid recommending dishes based solely on assumed water or basic seasonings.
        if not (used - PANTRY): continue
        coverage = len(matched)/len(required)
        if coverage < min_match: continue
        results.append(dict(id=recipe['id'],name=recipe['name'],coverage=round(coverage,4),
                            matched_ingredients=matched,missing_ingredients=missing,
                            optional_missing=optional_missing,used_ingredients=sorted(used),
                            can_make=not missing,original_ingredients=recipe['original_ingredients'],
                            instructions=recipe['instructions']))
    results.sort(key=lambda r:(len(r['missing_ingredients']),-r['coverage'],-len(r['used_ingredients']),r['name']))
    return results[:limit]
