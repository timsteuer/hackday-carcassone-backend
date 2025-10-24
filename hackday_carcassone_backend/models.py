"""Data models for the Carcassonne game backend."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Tile(BaseModel):
    """Tile configuration from tile.config.json."""
    id: str
    name: str
    image: str
    field_connections: List[str]
    city_connections: List[str]
    street_connections: List[str]
    count: int


class PlacedTile(BaseModel):
    """A tile that has been placed on the game board."""
    id: str  # Instance ID (unique for each placement)
    x: int
    y: int
    rotation: int = Field(..., description="Rotation in degrees: 0, 90, 180, or 270")
    image: str
    tileType: str  # The tile configuration ID


class Meeple(BaseModel):
    """A meeple placed on a tile feature."""
    id: str
    tileId: str  # The placed tile ID this meeple is on
    featureType: Literal["city", "road", "monastery", "field"]
    position: Literal["top", "right", "bottom", "left", "center"]


class ValidPosition(BaseModel):
    """A valid position where a tile can be placed."""
    x: int
    y: int
    validRotations: List[int] = Field(..., description="Valid rotations for this position")


class ValidMeeplePosition(BaseModel):
    """A valid position where a meeple can be placed on a tile."""
    featureType: Literal["city", "road", "monastery", "field"]
    position: Literal["top", "right", "bottom", "left", "center"]


class GameState(BaseModel):
    """Complete state of the game."""
    gameId: str
    status: Literal["active", "finished"]
    score: int
    placedTiles: List[PlacedTile]
    meeples: List[Meeple]
    remainingTilesCount: int
    currentTile: Optional[Tile] = None
    validPositions: Optional[List[ValidPosition]] = None
    meeplesRemaining: int


class PlaceTileRequest(BaseModel):
    """Request to place a tile."""
    tileId: str
    x: int
    y: int
    rotation: int = Field(..., description="Rotation in degrees: 0, 90, 180, or 270")


class PlaceTileResponse(BaseModel):
    """Response from placing a tile."""
    success: bool
    gameState: GameState
    message: Optional[str] = None


class PlaceMeepleRequest(BaseModel):
    """Request to place a meeple."""
    tileId: str
    featureType: Literal["city", "road", "monastery", "field"]
    position: Literal["top", "right", "bottom", "left", "center"]


class PlaceMeepleResponse(BaseModel):
    """Response from placing a meeple."""
    success: bool
    gameState: GameState
    message: Optional[str] = None


class ValidPositionsResponse(BaseModel):
    """Response containing valid positions for current tile."""
    positions: List[ValidPosition]


class ValidMeeplePositionsResponse(BaseModel):
    """Response containing valid meeple positions for a tile."""
    positions: List[ValidMeeplePosition]


class ErrorResponse(BaseModel):
    """Error response format."""
    message: str
    code: str
    details: Optional[dict] = None
