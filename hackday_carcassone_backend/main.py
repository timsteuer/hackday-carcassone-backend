"""FastAPI application for Carcassonne game backend."""

from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    GameState, PlaceTileRequest, PlaceTileResponse,
    PlaceMeepleRequest, PlaceMeepleResponse,
    ValidPositionsResponse, ValidMeeplePositionsResponse,
    ErrorResponse
)
from .game_logic import GameLogic


# Initialize FastAPI app
app = FastAPI(
    title="Carcassonne Game API",
    description="Backend API for Carcassonne tile-laying board game",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

# Initialize game logic
tile_config_path = Path(__file__).parent.parent / "data" / "tile.confg.json"
game_logic = GameLogic(str(tile_config_path))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Carcassonne Game API",
        "version": "1.0.0",
        "endpoints": {
            "create_game": "POST /api/game/new",
            "get_state": "GET /api/game/{gameId}/state",
            "place_tile": "POST /api/game/{gameId}/place-tile",
            "valid_positions": "GET /api/game/{gameId}/valid-positions",
            "place_meeple": "POST /api/game/{gameId}/place-meeple",
            "valid_meeple_positions": "GET /api/game/{gameId}/tile/{tileId}/valid-meeple-positions",
            "skip_meeple": "POST /api/game/{gameId}/skip-meeple"
        }
    }


@app.post("/api/game/new", response_model=GameState, status_code=status.HTTP_201_CREATED)
async def create_new_game():
    """
    Create a new single-player game session.
    
    Returns:
        GameState: Initial game state with starting tile placed and first tile drawn
    """
    try:
        game_state = game_logic.create_new_game()
        return game_state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Failed to create game: {str(e)}",
                "code": "GAME_CREATION_FAILED"
            }
        )


@app.get("/api/game/{game_id}/state", response_model=GameState)
async def get_game_state(game_id: str):
    """
    Get the current state of a game.
    
    Args:
        game_id: Unique identifier of the game
        
    Returns:
        GameState: Current game state
    """
    game_state = game_logic.get_game_state(game_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Game not found",
                "code": "GAME_NOT_FOUND"
            }
        )
    return game_state


@app.post("/api/game/{game_id}/place-tile", response_model=PlaceTileResponse)
async def place_tile(game_id: str, request: PlaceTileRequest):
    """
    Place a tile on the board at specified coordinates with rotation.
    
    Args:
        game_id: Current game ID
        request: Tile placement request with tileId, x, y, and rotation
        
    Returns:
        PlaceTileResponse: Response with success status and updated game state
    """
    success, game_state, message = game_logic.place_tile(
        game_id,
        request.tileId,
        request.x,
        request.y,
        request.rotation
    )
    
    if not success:
        if message == "Game not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": message,
                    "code": "GAME_NOT_FOUND"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": message,
                    "code": "INVALID_PLACEMENT"
                }
            )
    
    return PlaceTileResponse(
        success=True,
        gameState=game_state,
        message="Tile placed successfully"
    )


@app.get("/api/game/{game_id}/valid-positions", response_model=ValidPositionsResponse)
async def get_valid_positions(game_id: str):
    """
    Get all valid positions where the current tile can be placed.
    
    Args:
        game_id: Current game ID
        
    Returns:
        ValidPositionsResponse: List of valid positions with valid rotations
    """
    game_state = game_logic.get_game_state(game_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Game not found",
                "code": "GAME_NOT_FOUND"
            }
        )
    
    return ValidPositionsResponse(
        positions=game_state.validPositions or []
    )


@app.post("/api/game/{game_id}/place-meeple", response_model=PlaceMeepleResponse)
async def place_meeple(game_id: str, request: PlaceMeepleRequest):
    """
    Place a meeple on a specific feature of a tile.
    
    Args:
        game_id: Current game ID
        request: Meeple placement request with tileId, featureType, and position
        
    Returns:
        PlaceMeepleResponse: Response with success status and updated game state
    """
    success, game_state, message = game_logic.place_meeple(
        game_id,
        request.tileId,
        request.featureType,
        request.position
    )
    
    if not success:
        if message == "Game not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": message,
                    "code": "GAME_NOT_FOUND"
                }
            )
        elif message == "No meeples remaining":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": message,
                    "code": "NO_MEEPLES_REMAINING"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": message,
                    "code": "FEATURE_OCCUPIED"
                }
            )
    
    return PlaceMeepleResponse(
        success=True,
        gameState=game_state,
        message="Meeple placed successfully"
    )


@app.get("/api/game/{game_id}/tile/{tile_id}/valid-meeple-positions", 
         response_model=ValidMeeplePositionsResponse)
async def get_valid_meeple_positions(game_id: str, tile_id: str):
    """
    Get valid positions where a meeple can be placed on a specific tile.
    
    Args:
        game_id: Current game ID
        tile_id: Tile to check for valid meeple positions
        
    Returns:
        ValidMeeplePositionsResponse: List of valid meeple positions
    """
    game_state = game_logic.get_game_state(game_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Game not found",
                "code": "GAME_NOT_FOUND"
            }
        )
    
    valid_positions = game_logic.get_valid_meeple_positions(game_id, tile_id)
    
    return ValidMeeplePositionsResponse(
        positions=valid_positions
    )


@app.post("/api/game/{game_id}/skip-meeple", response_model=GameState)
async def skip_meeple(game_id: str):
    """
    Skip meeple placement after placing a tile.
    
    Args:
        game_id: Current game ID
        
    Returns:
        GameState: Updated game state
    """
    game_state = game_logic.skip_meeple(game_id)
    if not game_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Game not found",
                "code": "GAME_NOT_FOUND"
            }
        )
    
    return game_state


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
