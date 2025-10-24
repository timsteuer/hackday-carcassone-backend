# Quick Start Guide - Carcassonne Backend API

## Installation & Running

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic
```

### 2. Start the Server

```bash
python main.py
```

The server will start on `http://localhost:3000`

### 3. View API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## Testing the API

### Run the Integration Tests

```bash
# In one terminal, start the server:
python main.py

# In another terminal, run the tests:
python test_api.py
```

Expected output:
```
============================================================
Carcassonne Backend API Integration Tests
============================================================

Testing: POST /api/game/new
✓ Game created successfully: [game-id]

Testing: GET /api/game/[game-id]/state
✓ Game state retrieved successfully

...

============================================================
✅ All tests passed successfully!
============================================================
```

## Example Game Flow

### 1. Create a New Game

```bash
curl -X POST http://localhost:3000/api/game/new \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{
  "gameId": "abc-123-def-456",
  "status": "active",
  "score": 0,
  "placedTiles": [...],
  "currentTile": {...},
  "validPositions": [...],
  "meeplesRemaining": 7
}
```

### 2. Get Valid Positions

```bash
curl http://localhost:3000/api/game/abc-123-def-456/valid-positions
```

Response:
```json
{
  "positions": [
    {
      "x": 1,
      "y": 0,
      "validRotations": [0, 90, 180]
    }
  ]
}
```

### 3. Place a Tile

```bash
curl -X POST http://localhost:3000/api/game/abc-123-def-456/place-tile \
  -H "Content-Type: application/json" \
  -d '{
    "tileId": "TILE_001_CHURCH_FIELD",
    "x": 1,
    "y": 0,
    "rotation": 0
  }'
```

### 4. Get Valid Meeple Positions

```bash
curl http://localhost:3000/api/game/abc-123-def-456/tile/xyz-789/valid-meeple-positions
```

Response:
```json
{
  "positions": [
    {
      "featureType": "city",
      "position": "top"
    },
    {
      "featureType": "field",
      "position": "bottom"
    }
  ]
}
```

### 5. Place a Meeple

```bash
curl -X POST http://localhost:3000/api/game/abc-123-def-456/place-meeple \
  -H "Content-Type: application/json" \
  -d '{
    "tileId": "xyz-789",
    "featureType": "city",
    "position": "top"
  }'
```

### 6. Skip Meeple Placement

```bash
curl -X POST http://localhost:3000/api/game/abc-123-def-456/skip-meeple
```

## Game Rules

### Tile Placement
- Tiles must connect to existing tiles
- Edges must match: city-to-city, road-to-road, field-to-field
- Tiles can be rotated 90°, 180°, or 270°

### Meeple Placement
- Meeples can only be placed on the most recently placed tile
- A feature (city, road, monastery, field) can only have one meeple
- Players start with 7 meeples
- Meeples are returned when features are completed (future feature)

### Game End
- Game ends when all tiles are placed
- Final scoring occurs for incomplete features (future feature)

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/game/new` | Create new game |
| GET | `/api/game/{gameId}/state` | Get game state |
| POST | `/api/game/{gameId}/place-tile` | Place a tile |
| GET | `/api/game/{gameId}/valid-positions` | Get valid positions |
| POST | `/api/game/{gameId}/place-meeple` | Place a meeple |
| GET | `/api/game/{gameId}/tile/{tileId}/valid-meeple-positions` | Get valid meeple positions |
| POST | `/api/game/{gameId}/skip-meeple` | Skip meeple placement |

## Error Handling

The API returns appropriate HTTP status codes:
- `200 OK` - Successful request
- `201 Created` - Game created
- `400 Bad Request` - Invalid input or game rules violation
- `404 Not Found` - Game not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

Common error codes:
- `GAME_NOT_FOUND` - Game ID doesn't exist
- `INVALID_PLACEMENT` - Tile placement violates game rules
- `NO_MEEPLES_REMAINING` - No meeples left
- `FEATURE_OCCUPIED` - Feature already has a meeple

## Frontend Integration

The backend is ready for integration with the Vue 3 frontend. CORS is configured to allow requests from:
- `http://localhost:5173` (Vite default port)
- `http://localhost:3000`

Configure your frontend to use `http://localhost:3000/api` as the base URL.

## Troubleshooting

### Server won't start
- Make sure port 3000 is not already in use
- Verify all dependencies are installed: `pip install fastapi uvicorn pydantic`

### CORS errors
- Check that your frontend is running on an allowed origin
- Add your frontend URL to the CORS origins in `hackday_carcassone_backend/main.py`

### Tile placement fails
- Verify the tile connects properly to adjacent tiles
- Check that the rotation is valid for that position
- Ensure you're using a valid position from the `/valid-positions` endpoint

## Support

For issues or questions:
1. Check the API documentation at http://localhost:3000/docs
2. Run the integration tests to verify everything is working
3. Review the logs for error messages
