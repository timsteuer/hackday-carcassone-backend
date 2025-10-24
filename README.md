# Carcassonne Backend API

Backend API for the Carcassonne tile-laying board game. This is a single-player game implementation that provides RESTful API endpoints for game management, tile placement, meeple placement, and scoring.

## Features

- Single-player Carcassonne game
- RESTful API with FastAPI
- Tile placement validation
- Meeple placement logic
- Valid position calculation
- CORS support for frontend integration

## Requirements

- Python 3.11 or higher
- FastAPI
- uvicorn
- pydantic

## Installation

1. Install dependencies using pip:
```bash
pip install fastapi uvicorn pydantic
```

## Running the Server

Start the server on port 3000:

```bash
python main.py
```

The API will be available at `http://localhost:3000`

## API Endpoints

### Game Management

- `POST /api/game/new` - Create a new game
- `GET /api/game/{gameId}/state` - Get current game state

### Tile Placement

- `POST /api/game/{gameId}/place-tile` - Place a tile on the board
- `GET /api/game/{gameId}/valid-positions` - Get valid positions for current tile

### Meeple Placement

- `POST /api/game/{gameId}/place-meeple` - Place a meeple on a tile feature
- `GET /api/game/{gameId}/tile/{tileId}/valid-meeple-positions` - Get valid meeple positions
- `POST /api/game/{gameId}/skip-meeple` - Skip meeple placement

## API Documentation

When the server is running, visit:
- Swagger UI: `http://localhost:3000/docs`
- ReDoc: `http://localhost:3000/redoc`

## Frontend Integration

The backend is configured to work with the Vue 3 frontend. CORS is enabled for:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000`

## Example Usage

### Create a new game
```bash
curl -X POST http://localhost:3000/api/game/new \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Place a tile
```bash
curl -X POST http://localhost:3000/api/game/{gameId}/place-tile \
  -H "Content-Type: application/json" \
  -d '{"tileId": "TILE_001", "x": 0, "y": 1, "rotation": 0}'
```

### Get valid positions
```bash
curl http://localhost:3000/api/game/{gameId}/valid-positions
```

## Game Logic

The backend handles:
- Tile deck management and shuffling
- Starting tile placement at (0, 0)
- Tile placement validation (edge matching)
- Valid position calculation for each tile
- Meeple placement validation
- Feature occupation detection
- Game completion detection

## Tile Configuration

Tile definitions are stored in `data/tile.confg.json`. Each tile has:
- Unique ID
- Image path
- Field connections (T, B, L, R)
- City connections
- Street connections
- Count (number of tiles in the game)

## Development

The backend is built with:
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type hints
- **uvicorn** - ASGI server

## License

See LICENSE file for details.
