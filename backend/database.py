import sqlite3
from typing import List, Dict, Any
from datetime import datetime

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create collection table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collection (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    set_name TEXT NOT NULL,
                    number TEXT NOT NULL,
                    rarity TEXT NOT NULL,
                    type TEXT NOT NULL,
                    price REAL NOT NULL,
                    image TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    release_date TEXT NOT NULL,
                    added_date TEXT NOT NULL
                )
            """)
            
            # Create wishlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wishlist (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    set_name TEXT NOT NULL,
                    number TEXT NOT NULL,
                    rarity TEXT NOT NULL,
                    type TEXT NOT NULL,
                    price REAL NOT NULL,
                    image TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    release_date TEXT NOT NULL,
                    added_date TEXT NOT NULL
                )
            """)
            
            # Create price history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id TEXT,
                    price REAL NOT NULL,
                    date TEXT NOT NULL,
                    PRIMARY KEY (id, date)
                )
            """)
            
            conn.commit()
    
    def _dict_factory(self, cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        d = {}
        for idx, col in enumerate(cursor.description):
            value = row[idx]
            # Convert database column names to API format
            key = col[0]
            if key == 'set_name':
                key = 'set'
            elif key == 'release_date':
                key = 'releaseDate'
            d[key] = value
        return d
    
    def get_sets(self) -> List[str]:
        """Get list of all sets in the collection."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT set_name FROM collection ORDER BY set_name")
            return [row[0] for row in cursor.fetchall()]
    
    def get_collection(self) -> List[Dict[str, Any]]:
        """Get all cards in the collection."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM collection ORDER BY name")
            return cursor.fetchall()
    
    def add_to_collection(self, card: Dict[str, Any]):
        """Add a card to the collection."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if card already exists
            cursor.execute("SELECT id FROM collection WHERE id = ?", (card['id'],))
            if cursor.fetchone() is not None:
                raise ValueError("Card already in collection")
            
            # Add card to collection
            cursor.execute("""
                INSERT INTO collection (
                    id, name, set_name, number, rarity, type,
                    price, image, artist, release_date, added_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card['id'], card['name'], card['set'], card['number'],
                card['rarity'], card['type'], card['price'], card['image'],
                card['artist'], card['releaseDate'], datetime.now().isoformat()
            ))
            
            # Add initial price history entry
            cursor.execute("""
                INSERT INTO price_history (id, price, date)
                VALUES (?, ?, ?)
            """, (card['id'], card['price'], datetime.now().isoformat()))
            
            conn.commit()
    
    def remove_from_collection(self, card_id: str):
        """Remove a card from the collection."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM collection WHERE id = ?", (card_id,))
            if cursor.rowcount == 0:
                raise ValueError("Card not found in collection")
            conn.commit()
    
    def get_wishlist(self) -> List[Dict[str, Any]]:
        """Get all cards in the wishlist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM wishlist ORDER BY name")
            return cursor.fetchall()
    
    def add_to_wishlist(self, card: Dict[str, Any]):
        """Add a card to the wishlist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if card already exists
            cursor.execute("SELECT id FROM wishlist WHERE id = ?", (card['id'],))
            if cursor.fetchone() is not None:
                raise ValueError("Card already in wishlist")
            
            # Add card to wishlist
            cursor.execute("""
                INSERT INTO wishlist (
                    id, name, set_name, number, rarity, type,
                    price, image, artist, release_date, added_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card['id'], card['name'], card['set'], card['number'],
                card['rarity'], card['type'], card['price'], card['image'],
                card['artist'], card['releaseDate'], datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def remove_from_wishlist(self, card_id: str):
        """Remove a card from the wishlist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM wishlist WHERE id = ?", (card_id,))
            if cursor.rowcount == 0:
                raise ValueError("Card not found in wishlist")
            conn.commit()
    
    def get_price_history(self, card_id: str) -> List[Dict[str, Any]]:
        """Get price history for a card."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("""
                SELECT price, date
                FROM price_history
                WHERE id = ?
                ORDER BY date
            """, (card_id,))
            return cursor.fetchall()
    
    def update_price(self, card_id: str, new_price: float):
        """Update the price of a card and record in price history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update price in collection
            cursor.execute("""
                UPDATE collection
                SET price = ?
                WHERE id = ?
            """, (new_price, card_id))
            
            # Update price in wishlist
            cursor.execute("""
                UPDATE wishlist
                SET price = ?
                WHERE id = ?
            """, (new_price, card_id))
            
            # Add price history entry
            cursor.execute("""
                INSERT INTO price_history (id, price, date)
                VALUES (?, ?, ?)
            """, (card_id, new_price, datetime.now().isoformat()))
            
            conn.commit()
