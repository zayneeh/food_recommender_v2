# Food Archive: ingredient-first recommender

A standalone replacement MVP for the recommender, not a replacement for the original archive website. It uses the original CSV (84 recipes), with a manually prepared companion ingredient mapping. No API key, external model, or vector database is needed.

## Run

Python 3.10+ recommended. From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn server:app --reload
```

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs.

```bash
python -m unittest -v
```

## Structure

- `data/Nigerian meals.csv`: unchanged original recipe dataset.
- `data/ingredient_requirements.txt`: row number | required groups | optional groups. Semicolons separate groups, slashes separate alternatives. Keep rows aligned with the original CSV. This initial manual mapping should be reviewed against original ingredients and instructions before production use.
- `recipes.py`: normalization, directional category matching, scoring and ranking.
- `server.py`: FastAPI and same-origin static frontend.
- `frontend/`: simple standalone web UI.
- `test_recipes.py`: basic regression tests.

## Ranking

Coverage = matched required groups / total required groups. Results are ordered by fewest missing groups, then highest coverage, then number of supplied ingredients used. Basic pantry items alone do not trigger recommendations. Water is assumed by default and can be switched off. No other pantry ingredients are silently assumed. Optional ingredients don't affect coverage. An ingredient can satisfy multiple compatible groups; quantities are not checked. Generic terms such as pepper don't automatically satisfy specific types. The system does not assume tomato equals tomato paste, garri equals cassava, or palm oil equals vegetable oil.

## API

POST `/api/recommend` with JSON, for example:

```json
{"ingredients":["rice","salt"],"assume_water":true,"min_match":0,"limit":12}
```

Returns a `recipes` array with coverage, missing ingredients, optional ingredients, original ingredient text and instructions.

## Limitations

The source contains international dishes as well as Nigerian ones; not all recipes have fully specified ingredients or consistent instructions. The hand-curated mapping is a first-pass interpretation, not validated by a culinary expert. It does not handle quantities, ingredient inventory depletion, allergen guarantees, all aliases, or substitutions not explicitly encoded. A complete match means all modeled requirement groups match, not that the dish is guaranteed cookable. The original article site, chatbot and deployment were not modified; you can integrate the endpoint into the original site later. No model training is performed.
