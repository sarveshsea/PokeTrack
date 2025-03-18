from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import Database
from api import TCGPlayerAPI
from typing import List, Optional
from pydantic import BaseModel
import uvicorn

app = FastAPI()
db = Database('pokemon_cards.db')
tcg_api = TCGPlayerAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Card(BaseModel):
    id: str
    name: str
    set: str
    number: str
    rarity: str
    type: str
    price: float
    image: str
    artist: str
    releaseDate: str

class SearchParams(BaseModel):
    query: str
    rarity: Optional[str] = None
    set: Optional[str] = None
    minPrice: Optional[float] = None
    maxPrice: Optional[float] = None
    sortBy: Optional[str] = None

# Routes
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/sets")
def get_sets() -> List[str]:
    return db.get_sets()

@app.post("/search")
def search_cards(params: SearchParams) -> List[Card]:
    try:
        cards = tcg_api.search_cards(
            query=params.query,
            rarity=params.rarity,
            set_name=params.set,
            min_price=params.minPrice,
            max_price=params.maxPrice
        )
        
        if params.sortBy:
            field, order = params.sortBy.split('-')
            reverse = order == 'desc'
            cards.sort(key=lambda x: getattr(x, field), reverse=reverse)
        
        return cards
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cards/{card_id}")
def get_card(card_id: str) -> Card:
    try:
        return tcg_api.get_card(card_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Card not found")

@app.get("/collection")
def get_collection() -> List[Card]:
    try:
        return db.get_collection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collection/{card_id}")
def add_to_collection(card_id: str):
    try:
        card = tcg_api.get_card(card_id)
        db.add_to_collection(card)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/collection/{card_id}")
def remove_from_collection(card_id: str):
    try:
        db.remove_from_collection(card_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wishlist")
def get_wishlist() -> List[Card]:
    try:
        return db.get_wishlist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wishlist/{card_id}")
def add_to_wishlist(card_id: str):
    try:
        card = tcg_api.get_card(card_id)
        db.add_to_wishlist(card)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/wishlist/{card_id}")
def remove_from_wishlist(card_id: str):
    try:
        db.remove_from_wishlist(card_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/discover")
def get_discover():
    try:
        featured = tcg_api.get_featured_cards()
        new_releases = tcg_api.get_new_releases()
        trending = tcg_api.get_trending_cards()
        
        return {
            "featured": featured,
            "newReleases": new_releases,
            "trending": trending
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
