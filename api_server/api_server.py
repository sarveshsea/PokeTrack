from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import create_table, add_card_to_database, get_all_cards, delete_card, delete_all_cards, get_collection_stats
from database import add_card_to_wishlist, get_all_wishlist_cards, delete_wishlist_card, delete_all_wishlist_cards
import requests
import json

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
create_table()

# Card collection endpoints
@app.get("/api/cards/")
async def get_cards():
    return get_all_cards()

@app.post("/api/cards/")
async def add_card(card: dict):
    return add_card_to_database(card)

@app.delete("/api/cards/{card_id}")
async def remove_card(card_id: str):
    return delete_card(card_id)

@app.delete("/api/cards/")
async def remove_all_cards():
    return delete_all_cards()

# Wishlist endpoints
@app.get("/api/wishlist/")
async def get_wishlist():
    return get_all_wishlist_cards()

@app.post("/api/wishlist/")
async def add_to_wishlist(card: dict):
    return add_card_to_wishlist(card)

@app.delete("/api/wishlist/{card_id}")
async def remove_from_wishlist(card_id: str):
    return delete_wishlist_card(card_id)

@app.delete("/api/wishlist/")
async def clear_wishlist():
    return delete_all_wishlist_cards()

# Search endpoint
@app.get("/api/search/")
async def search_cards(query: str):
    try:
        # Make request to Pokemon TCG API
        response = requests.get(
            f"https://api.pokemontcg.io/v2/cards",
            params={"q": f"name:{query}*", "orderBy": "name", "pageSize": 20},
            headers={"X-Api-Key": ""}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stats endpoint
@app.get("/api/stats/")
async def get_stats():
    return get_collection_stats()