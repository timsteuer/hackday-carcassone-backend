"""Game logic for Carcassonne backend."""

import json
import random
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import (
    Tile, PlacedTile, Meeple, GameState, ValidPosition, ValidMeeplePosition
)


class GameLogic:
    """Handles all game logic for Carcassonne."""
    
    def __init__(self, tile_config_path: str):
        """Initialize game logic with tile configuration."""
        self.tile_config_path = tile_config_path
        self.tiles_config: List[Tile] = []
        self.games: Dict[str, GameState] = {}
        self._load_tiles()
    
    def _load_tiles(self):
        """Load tile configurations from JSON file."""
        with open(self.tile_config_path, 'r') as f:
            data = json.load(f)
            self.tiles_config = [Tile(**tile) for tile in data['tiles']]
    
    def _create_tile_deck(self) -> List[Tile]:
        """Create a shuffled deck of tiles based on count."""
        deck = []
        for tile_config in self.tiles_config:
            # Skip the start tile (TILE_025_start)
            if tile_config.id == "TILE_025_start":
                continue
            for _ in range(tile_config.count):
                deck.append(tile_config.model_copy())
        random.shuffle(deck)
        return deck
    
    def create_new_game(self) -> GameState:
        """Create a new game with initial state."""
        game_id = str(uuid.uuid4())
        
        # Create tile deck
        tile_deck = self._create_tile_deck()
        
        # Find and place starting tile at (0, 0)
        start_tile_config = next(
            (t for t in self.tiles_config if t.id == "TILE_025_start"),
            None
        )
        if not start_tile_config:
            raise ValueError("Start tile not found in configuration")
        
        start_placed_tile = PlacedTile(
            id=str(uuid.uuid4()),
            x=0,
            y=0,
            rotation=0,
            image=start_tile_config.image,
            tileType=start_tile_config.id
        )
        
        # Draw first tile
        current_tile = tile_deck.pop(0) if tile_deck else None
        
        # Create initial game state
        game_state = GameState(
            gameId=game_id,
            status="active",
            score=0,
            placedTiles=[start_placed_tile],
            meeples=[],
            remainingTilesCount=len(tile_deck),
            currentTile=current_tile,
            validPositions=None,
            meeplesRemaining=7
        )
        
        # Calculate valid positions for current tile
        if current_tile:
            game_state.validPositions = self._calculate_valid_positions(game_state, current_tile)
        
        # Store game state
        self.games[game_id] = game_state
        
        # Store the tile deck separately for this game
        if not hasattr(self, 'game_decks'):
            self.game_decks = {}
        self.game_decks[game_id] = tile_deck
        
        return game_state
    
    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """Get the current state of a game."""
        return self.games.get(game_id)
    
    def _rotate_connection(self, connection: str, rotation: int) -> str:
        """Rotate a connection (T/R/B/L) by given degrees."""
        directions = ['T', 'R', 'B', 'L']
        if connection not in directions:
            return connection
        
        idx = directions.index(connection)
        steps = rotation // 90
        new_idx = (idx + steps) % 4
        return directions[new_idx]
    
    def _get_rotated_connections(self, tile: Tile, rotation: int) -> Tuple[List[str], List[str], List[str]]:
        """Get tile connections after rotation."""
        rotated_fields = [self._rotate_connection(c.strip(), rotation) for c in tile.field_connections]
        rotated_cities = [self._rotate_connection(c.strip(), rotation) for c in tile.city_connections]
        rotated_streets = [self._rotate_connection(c.strip(), rotation) for c in tile.street_connections]
        return rotated_fields, rotated_cities, rotated_streets
    
    def _get_tile_at_position(self, game_state: GameState, x: int, y: int) -> Optional[PlacedTile]:
        """Get the tile at a specific position."""
        for tile in game_state.placedTiles:
            if tile.x == x and tile.y == y:
                return tile
        return None
    
    def _get_tile_config(self, tile_type: str) -> Optional[Tile]:
        """Get tile configuration by tile type ID."""
        for tile in self.tiles_config:
            if tile.id == tile_type:
                return tile
        return None
    
    def _check_connection_match(self, side1: List[str], side2: List[str], direction: str) -> bool:
        """Check if two sides match (both have or don't have the connection)."""
        has_field1 = direction in side1
        has_field2 = direction in side2
        return has_field1 == has_field2
    
    def _is_valid_placement(self, game_state: GameState, tile: Tile, x: int, y: int, rotation: int) -> bool:
        """Check if placing a tile at position with rotation is valid."""
        # Get rotated connections
        fields, cities, streets = self._get_rotated_connections(tile, rotation)
        
        # Check each adjacent position
        adjacents = [
            (x, y - 1, 'T', 'B'),  # Top neighbor
            (x + 1, y, 'R', 'L'),  # Right neighbor
            (x, y + 1, 'B', 'T'),  # Bottom neighbor
            (x - 1, y, 'L', 'R'),  # Left neighbor
        ]
        
        has_adjacent = False
        for adj_x, adj_y, our_side, their_side in adjacents:
            adjacent_tile = self._get_tile_at_position(game_state, adj_x, adj_y)
            if not adjacent_tile:
                continue
            
            has_adjacent = True
            
            # Get adjacent tile configuration and rotation
            adj_config = self._get_tile_config(adjacent_tile.tileType)
            if not adj_config:
                continue
            
            adj_fields, adj_cities, adj_streets = self._get_rotated_connections(
                adj_config, adjacent_tile.rotation
            )
            
            # Check field connection
            our_field = our_side in fields
            their_field = their_side in adj_fields
            if our_field != their_field:
                return False
            
            # Check city connection
            our_city = our_side in cities
            their_city = their_side in adj_cities
            if our_city != their_city:
                return False
            
            # Check street connection
            our_street = our_side in streets
            their_street = their_side in adj_streets
            if our_street != their_street:
                return False
        
        # Must have at least one adjacent tile
        return has_adjacent
    
    def _calculate_valid_positions(self, game_state: GameState, tile: Tile) -> List[ValidPosition]:
        """Calculate all valid positions where the current tile can be placed."""
        valid_positions = []
        
        # Find all positions adjacent to existing tiles
        adjacent_positions = set()
        for placed_tile in game_state.placedTiles:
            adjacent_positions.add((placed_tile.x, placed_tile.y - 1))  # Top
            adjacent_positions.add((placed_tile.x + 1, placed_tile.y))  # Right
            adjacent_positions.add((placed_tile.x, placed_tile.y + 1))  # Bottom
            adjacent_positions.add((placed_tile.x - 1, placed_tile.y))  # Left
        
        # Check each adjacent position
        for x, y in adjacent_positions:
            # Skip if position is already occupied
            if self._get_tile_at_position(game_state, x, y):
                continue
            
            # Check which rotations are valid
            valid_rotations = []
            for rotation in [0, 90, 180, 270]:
                if self._is_valid_placement(game_state, tile, x, y, rotation):
                    valid_rotations.append(rotation)
            
            if valid_rotations:
                valid_positions.append(ValidPosition(
                    x=x,
                    y=y,
                    validRotations=valid_rotations
                ))
        
        return valid_positions
    
    def place_tile(self, game_id: str, tile_id: str, x: int, y: int, rotation: int) -> Tuple[bool, GameState, Optional[str]]:
        """Place a tile on the board."""
        game_state = self.games.get(game_id)
        if not game_state:
            return False, None, "Game not found"
        
        if game_state.status != "active":
            return False, game_state, "Game is not active"
        
        if not game_state.currentTile or game_state.currentTile.id != tile_id:
            return False, game_state, "Invalid tile ID"
        
        # Validate rotation
        if rotation not in [0, 90, 180, 270]:
            return False, game_state, "Invalid rotation"
        
        # Check if position is valid
        valid_position = None
        for pos in game_state.validPositions or []:
            if pos.x == x and pos.y == y:
                valid_position = pos
                break
        
        if not valid_position:
            return False, game_state, "Invalid position"
        
        if rotation not in valid_position.validRotations:
            return False, game_state, "Invalid rotation for this position"
        
        # Place the tile
        placed_tile = PlacedTile(
            id=str(uuid.uuid4()),
            x=x,
            y=y,
            rotation=rotation,
            image=game_state.currentTile.image,
            tileType=game_state.currentTile.id
        )
        game_state.placedTiles.append(placed_tile)
        
        # Draw next tile
        tile_deck = self.game_decks.get(game_id, [])
        if tile_deck:
            game_state.currentTile = tile_deck.pop(0)
            game_state.remainingTilesCount = len(tile_deck)
            game_state.validPositions = self._calculate_valid_positions(game_state, game_state.currentTile)
        else:
            game_state.currentTile = None
            game_state.remainingTilesCount = 0
            game_state.validPositions = []
        
        # Store the recently placed tile ID for meeple placement
        if not hasattr(self, 'last_placed_tiles'):
            self.last_placed_tiles = {}
        self.last_placed_tiles[game_id] = placed_tile.id
        
        return True, game_state, None
    
    def _get_feature_at_position(self, tile: Tile, rotation: int, position: str) -> Optional[str]:
        """Determine what feature is at a given position on the tile."""
        fields, cities, streets = self._get_rotated_connections(tile, rotation)
        
        # Map position to direction
        position_to_direction = {
            'top': 'T',
            'right': 'R',
            'bottom': 'B',
            'left': 'L',
            'center': 'center'
        }
        
        direction = position_to_direction.get(position)
        
        # Check for monastery at center
        if position == 'center':
            # Monastery is typically on tiles with church in the name
            # For simplicity, we'll check if it's a church tile
            if 'church' in tile.name.lower() or 'Church' in tile.name:
                return 'monastery'
            return None
        
        # Check what's at this direction
        if direction in cities:
            return 'city'
        elif direction in streets:
            return 'road'
        elif direction in fields:
            return 'field'
        
        return None
    
    def _is_feature_occupied(self, game_state: GameState, tile_id: str, feature_type: str, position: str) -> bool:
        """Check if a feature is already occupied by a meeple."""
        # For now, simple check - just see if meeple exists on this exact tile/position
        # A more complete implementation would check connected features
        for meeple in game_state.meeples:
            if meeple.tileId == tile_id and meeple.position == position:
                return True
        return False
    
    def get_valid_meeple_positions(self, game_id: str, tile_id: str) -> List[ValidMeeplePosition]:
        """Get valid positions where a meeple can be placed on a tile."""
        game_state = self.games.get(game_id)
        if not game_state:
            return []
        
        # Find the placed tile
        placed_tile = None
        for tile in game_state.placedTiles:
            if tile.id == tile_id:
                placed_tile = tile
                break
        
        if not placed_tile:
            return []
        
        # Get tile configuration
        tile_config = self._get_tile_config(placed_tile.tileType)
        if not tile_config:
            return []
        
        valid_positions = []
        
        # Check each position
        for position in ['top', 'right', 'bottom', 'left', 'center']:
            feature = self._get_feature_at_position(tile_config, placed_tile.rotation, position)
            
            if feature and not self._is_feature_occupied(game_state, tile_id, feature, position):
                valid_positions.append(ValidMeeplePosition(
                    featureType=feature,
                    position=position
                ))
        
        return valid_positions
    
    def place_meeple(self, game_id: str, tile_id: str, feature_type: str, position: str) -> Tuple[bool, GameState, Optional[str]]:
        """Place a meeple on a tile feature."""
        game_state = self.games.get(game_id)
        if not game_state:
            return False, None, "Game not found"
        
        if game_state.meeplesRemaining <= 0:
            return False, game_state, "No meeples remaining"
        
        # Check if this is the last placed tile
        last_placed_id = getattr(self, 'last_placed_tiles', {}).get(game_id)
        if last_placed_id != tile_id:
            return False, game_state, "Can only place meeple on the last placed tile"
        
        # Validate the position is valid
        valid_positions = self.get_valid_meeple_positions(game_id, tile_id)
        is_valid = any(
            pos.featureType == feature_type and pos.position == position
            for pos in valid_positions
        )
        
        if not is_valid:
            return False, game_state, "Invalid meeple position"
        
        # Place the meeple
        meeple = Meeple(
            id=str(uuid.uuid4()),
            tileId=tile_id,
            featureType=feature_type,
            position=position
        )
        game_state.meeples.append(meeple)
        game_state.meeplesRemaining -= 1
        
        # Check for completed features and score
        self._score_completed_features(game_state)
        
        # Clear last placed tile
        if hasattr(self, 'last_placed_tiles') and game_id in self.last_placed_tiles:
            del self.last_placed_tiles[game_id]
        
        # Check if game is finished
        if game_state.currentTile is None:
            game_state.status = "finished"
            self._score_incomplete_features(game_state)
        
        return True, game_state, None
    
    def skip_meeple(self, game_id: str) -> Optional[GameState]:
        """Skip meeple placement for this turn."""
        game_state = self.games.get(game_id)
        if not game_state:
            return None
        
        # Check for completed features and score
        self._score_completed_features(game_state)
        
        # Clear last placed tile
        if hasattr(self, 'last_placed_tiles') and game_id in self.last_placed_tiles:
            del self.last_placed_tiles[game_id]
        
        # Check if game is finished
        if game_state.currentTile is None:
            game_state.status = "finished"
            self._score_incomplete_features(game_state)
        
        return game_state
    
    def _score_completed_features(self, game_state: GameState):
        """Score completed features and return meeples."""
        # This is a simplified scoring implementation
        # A complete implementation would need to:
        # 1. Identify all connected features
        # 2. Check if each feature is complete
        # 3. Calculate scores based on feature type
        # 4. Return meeples from completed features
        
        # For now, we'll implement basic scoring
        # TODO: Implement proper feature completion detection and scoring
        pass
    
    def _score_incomplete_features(self, game_state: GameState):
        """Score incomplete features at game end."""
        # This is a simplified end-game scoring
        # A complete implementation would score:
        # - Incomplete cities (1 point per tile)
        # - Incomplete roads (1 point per tile)
        # - Incomplete monasteries (1 point per surrounding tile)
        # - Fields (3 points per completed adjacent city)
        
        # For now, we'll add basic scoring
        # TODO: Implement proper end-game scoring
        pass
