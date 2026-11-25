from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from recipes import load_recipes, recommend

app = FastAPI(title='Food Recommender')

class RecommendRequest(BaseModel):
    ingredients: list[str] | str
    assume_water: bool = True
    min_match: float = Field(default=0, ge=0, le=1)
    limit: int = Field(default=12, ge=1, le=84)

@app.post('/api/recommend')
def recommendations(body: RecommendRequest):
    return {'recipes': recommend(body.ingredients,body.assume_water,body.min_match,body.limit)}

@app.get('/api/health')
def health():
    return {'status':'ok','recipe_count':len(load_recipes())}

app.mount('/',StaticFiles(directory=Path(__file__).parent/'frontend',html=True),name='frontend')
