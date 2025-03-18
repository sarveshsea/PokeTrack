# PokéTrack

A modern web application for tracking your Pokémon card collection, monitoring card prices, and managing your wishlist.

## Features

- **Card Search**: Search through the extensive Pokémon Trading Card Game database
- **Collection Management**: Add, remove, and track cards in your collection
- **Wishlist System**: Keep track of cards you want to acquire
- **Price Monitoring**: Track market prices and collection value
- **Statistics Dashboard**: View detailed statistics about your collection
- **Discover Feature**: Find new cards based on various criteria
- **Responsive Design**: Beautiful, modern interface that works on all devices

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python with FastAPI
- **Database**: SQLite
- **APIs**: TCGPlayer API integration for pricing data

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for development)
- Git

### Installation

1. Clone the repository
```bash
git clone https://github.com/sarveshsea/poketrack.git
cd poketrack
```

2. Set up the backend
```bash
cd api_server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Start the backend server
```bash
uvicorn api_server:app --reload
```

4. Open the frontend
```bash
cd ../frontend
python -m http.server 8080  # Or use any static file server
```

5. Visit `http://localhost:8080` in your browser

## Project Structure

```
poketrack/
├── api_server/
│   ├── api_server.py     # FastAPI backend server
│   ├── database.py       # Database operations
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # Main HTML file
│   ├── app.js           # Frontend JavaScript
│   └── styles.css       # CSS styles
└── README.md
```

## Features in Detail

### Collection Management
- Add cards to your collection
- Track card quantities
- Monitor card conditions
- Remove cards individually or clear entire collection

### Wishlist System
- Add desired cards to wishlist
- Track market prices for wishlist items
- Easy transfer from wishlist to collection
- Organize and prioritize wanted cards

### Statistics and Analytics
- Total collection value
- Value trends over time
- Rarity distribution
- Set distribution
- Most valuable cards

### Card Discovery
- Browse cards by type
- Filter by rarity
- Sort by various criteria
- Random card suggestions

## API Endpoints

### Cards
- `GET /api/cards/` - Get all collection cards
- `POST /api/cards/` - Add card to collection
- `DELETE /api/cards/{card_id}` - Remove card from collection
- `DELETE /api/cards/` - Clear collection

### Wishlist
- `GET /api/wishlist/` - Get wishlist cards
- `POST /api/wishlist/` - Add card to wishlist
- `DELETE /api/wishlist/{card_id}` - Remove from wishlist
- `DELETE /api/wishlist/` - Clear wishlist

### Search
- `GET /api/search/?query={query}` - Search for cards

### Statistics
- `GET /api/stats/` - Get collection statistics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Pokémon TCG API for card data
- TCGPlayer for market pricing data
- FastAPI team for the excellent web framework