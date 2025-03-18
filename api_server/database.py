import sqlite3
from datetime import datetime

def create_table():
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    # Create pokemon_cards table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon_cards (
        id TEXT PRIMARY KEY,
        name TEXT,
        set_name TEXT,
        rarity TEXT,
        image_url TEXT,
        condition TEXT DEFAULT 'Near Mint',
        quantity INTEGER DEFAULT 1,
        price REAL,
        card_number TEXT,
        added_date TEXT DEFAULT (datetime('now'))
    )
    ''')
    
    # Create price_history table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id TEXT,
        price REAL,
        date TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (card_id) REFERENCES pokemon_cards (id)
    )
    ''')
    
    # Create card_conditions table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS card_conditions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    ''')
    
    # Insert default conditions if they don't exist
    conditions = ['Near Mint', 'Lightly Played', 'Moderately Played', 'Heavily Played', 'Damaged']
    for condition in conditions:
        cursor.execute('INSERT OR IGNORE INTO card_conditions (name) VALUES (?)', (condition,))
    
    # Create wishlist table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wishlist (
        id TEXT PRIMARY KEY,
        name TEXT,
        set_name TEXT,
        rarity TEXT,
        image_url TEXT,
        condition TEXT DEFAULT 'Near Mint',
        quantity INTEGER DEFAULT 1,
        price REAL,
        card_number TEXT,
        added_date TEXT DEFAULT (datetime('now'))
    )
    ''')
    
    conn.commit()
    conn.close()

def get_all_cards():
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pokemon_cards')
    columns = [description[0] for description in cursor.description]
    cards = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return cards

def add_card_to_database(card_data):
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    try:
        # Check if card already exists
        cursor.execute('SELECT quantity FROM pokemon_cards WHERE id = ?', (card_data['id'],))
        existing_card = cursor.fetchone()
        
        if existing_card:
            # Update quantity if card exists
            new_quantity = existing_card[0] + 1
            cursor.execute('UPDATE pokemon_cards SET quantity = ? WHERE id = ?',
                          (new_quantity, card_data['id']))
            print(f"Updated quantity for card {card_data['name']}")
        else:
            # Insert new card if it doesn't exist
            cursor.execute('''
                INSERT INTO pokemon_cards (id, name, set_name, rarity, image_url, price, card_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                card_data['id'],
                card_data['name'],
                card_data['set_name'],
                card_data['rarity'],
                card_data['image_url'],
                card_data['price'],
                card_data['card_number']
            ))
            print(f"Added new card {card_data['name']}")
        
        # Add price history entry
        cursor.execute('''
            INSERT INTO price_history (card_id, price)
            VALUES (?, ?)
        ''', (card_data['id'], card_data['price']))
        
        conn.commit()
        return {"message": "Card added successfully"}
    
    except Exception as e:
        print(f"Error adding card: {e}")
        conn.rollback()
        return {"error": str(e)}
    
    finally:
        conn.close()

def delete_card(card_id):
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    try:
        # Check if card exists and get current quantity
        cursor.execute('SELECT quantity FROM pokemon_cards WHERE id = ?', (card_id,))
        result = cursor.fetchone()
        
        if result:
            quantity = result[0]
            
            if quantity > 1:
                # Decrease quantity by 1
                cursor.execute('UPDATE pokemon_cards SET quantity = quantity - 1 WHERE id = ?', (card_id,))
            else:
                # Delete the card if quantity would become 0
                cursor.execute('DELETE FROM pokemon_cards WHERE id = ?', (card_id,))
            
            conn.commit()
            return {"message": "Card deleted successfully"}
        else:
            return {"error": "Card not found"}
    
    except Exception as e:
        print(f"Error deleting card: {e}")
        conn.rollback()
        return {"error": str(e)}
    
    finally:
        conn.close()

def delete_all_cards():
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM pokemon_cards')
        cursor.execute('DELETE FROM price_history')
        conn.commit()
        return {"message": "All cards deleted successfully"}
    
    except Exception as e:
        print(f"Error deleting all cards: {e}")
        conn.rollback()
        return {"error": str(e)}
    
    finally:
        conn.close()

def get_collection_stats():
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    try:
        # Get total number of unique cards
        cursor.execute('SELECT COUNT(*) FROM pokemon_cards')
        unique_cards = cursor.fetchone()[0]
        
        # Get total number of cards (including duplicates)
        cursor.execute('SELECT SUM(quantity) FROM pokemon_cards')
        total_cards = cursor.fetchone()[0] or 0
        
        # Get total collection value
        cursor.execute('SELECT SUM(price * quantity) FROM pokemon_cards')
        total_value = cursor.fetchone()[0] or 0
        
        # Calculate average card value
        average_card_value = total_value / total_cards if total_cards > 0 else 0
        
        # Get rarity distribution
        cursor.execute('''
            SELECT rarity, COUNT(*) as count
            FROM pokemon_cards
            GROUP BY rarity
            ORDER BY count DESC
        ''')
        rarity_distribution = [{
            "rarity": row[0],
            "count": row[1]
        } for row in cursor.fetchall()]
        
        # Get set distribution
        cursor.execute('''
            SELECT 
                set_name as set,
                COUNT(*) as count,
                SUM(quantity) as total_quantity,
                SUM(price * quantity) as total_value
            FROM pokemon_cards
            GROUP BY set_name
            ORDER BY total_value DESC
        ''')
        set_distribution = [{
            "set": row[0],
            "count": row[1],
            "total_quantity": row[2],
            "total_value": row[3]
        } for row in cursor.fetchall()]
        
        # Get value history
        cursor.execute('''
            SELECT 
                date,
                SUM(price) as value
            FROM price_history
            GROUP BY date
            ORDER BY date
        ''')
        value_history = [{
            "date": row[0],
            "value": row[1]
        } for row in cursor.fetchall()]
        
        return {
            "total_cards": total_cards,
            "unique_cards": unique_cards,
            "total_value": total_value,
            "average_card_value": average_card_value,
            "rarity_distribution": rarity_distribution,
            "set_distribution": set_distribution,
            "value_history": value_history
        }
    
    except Exception as e:
        print(f"Error getting collection stats: {e}")
        return {"error": str(e)}
    
    finally:
        conn.close()

def get_all_wishlist_cards():
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wishlist')
    columns = [description[0] for description in cursor.description]
    cards = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return cards

def add_card_to_wishlist(card_data):
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    try:
        # Check if card already exists in wishlist
        cursor.execute('SELECT quantity FROM wishlist WHERE id = ?', (card_data['id'],))
        existing_card = cursor.fetchone()
        
        if existing_card:
            # Update quantity if card exists
            new_quantity = existing_card[0] + 1
            cursor.execute('UPDATE wishlist SET quantity = ? WHERE id = ?',
                          (new_quantity, card_data['id']))
            print(f"Updated quantity for wishlist card {card_data['name']}")
        else:
            # Insert new card if it doesn't exist
            cursor.execute('''
                INSERT INTO wishlist (id, name, set_name, rarity, image_url, price, card_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                card_data['id'],
                card_data['name'],
                card_data['set_name'],
                card_data['rarity'],
                card_data['image_url'],
                card_data['price'],
                card_data['card_number']
            ))
            print(f"Added new card to wishlist {card_data['name']}")
        
        conn.commit()
        return {"message": "Card added to wishlist successfully"}
    
    except Exception as e:
        print(f"Error adding card to wishlist: {e}")
        conn.rollback()
        return {"error": str(e)}
    
    finally:
        conn.close()

def delete_wishlist_card(card_id):
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM wishlist WHERE id = ?', (card_id,))
        conn.commit()
        return {"message": "Card removed from wishlist successfully"}
    
    except Exception as e:
        print(f"Error removing card from wishlist: {e}")
        conn.rollback()
        return {"error": str(e)}
    
    finally:
        conn.close()

def delete_all_wishlist_cards():
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM wishlist')
        conn.commit()
        return {"message": "Wishlist cleared successfully"}
    
    except Exception as e:
        print(f"Error clearing wishlist: {e}")
        conn.rollback()
        return {"error": str(e)}
    
    finally:
        conn.close()

def get_wishlist_card_details(card_id):
    conn = sqlite3.connect('pokemon_cards.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM wishlist WHERE id = ?', (card_id,))
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        
        if row:
            return dict(zip(columns, row))
        else:
            return None
    
    except Exception as e:
        print(f"Error getting wishlist card details: {e}")
        return None
    
    finally:
        conn.close()