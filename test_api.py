"""Simple integration test for the Carcassonne API."""

import requests
import sys
import time
from typing import Dict, Any


BASE_URL = "http://localhost:3000"


def test_create_game() -> Dict[str, Any]:
    """Test creating a new game."""
    print("Testing: POST /api/game/new")
    response = requests.post(f"{BASE_URL}/api/game/new", json={})
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    data = response.json()
    assert "gameId" in data
    assert data["status"] == "active"
    assert data["score"] == 0
    assert len(data["placedTiles"]) == 1  # Starting tile
    assert data["meeplesRemaining"] == 7
    assert data["currentTile"] is not None
    assert data["validPositions"] is not None
    
    print(f"✓ Game created successfully: {data['gameId']}")
    return data


def test_get_game_state(game_id: str) -> Dict[str, Any]:
    """Test retrieving game state."""
    print(f"Testing: GET /api/game/{game_id}/state")
    response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data["gameId"] == game_id
    
    print(f"✓ Game state retrieved successfully")
    return data


def test_get_valid_positions(game_id: str) -> Dict[str, Any]:
    """Test getting valid positions."""
    print(f"Testing: GET /api/game/{game_id}/valid-positions")
    response = requests.get(f"{BASE_URL}/api/game/{game_id}/valid-positions")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "positions" in data
    assert len(data["positions"]) > 0, "Should have at least one valid position"
    
    print(f"✓ Valid positions retrieved: {len(data['positions'])} positions")
    return data


def test_place_tile(game_id: str, tile_id: str, x: int, y: int, rotation: int) -> Dict[str, Any]:
    """Test placing a tile."""
    print(f"Testing: POST /api/game/{game_id}/place-tile")
    payload = {
        "tileId": tile_id,
        "x": x,
        "y": y,
        "rotation": rotation
    }
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/place-tile", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data["success"] is True
    assert len(data["gameState"]["placedTiles"]) >= 2  # Start + placed tile
    
    print(f"✓ Tile placed successfully at ({x}, {y}) with rotation {rotation}")
    return data


def test_get_valid_meeple_positions(game_id: str, tile_id: str) -> Dict[str, Any]:
    """Test getting valid meeple positions."""
    print(f"Testing: GET /api/game/{game_id}/tile/{tile_id}/valid-meeple-positions")
    response = requests.get(f"{BASE_URL}/api/game/{game_id}/tile/{tile_id}/valid-meeple-positions")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "positions" in data
    
    print(f"✓ Valid meeple positions retrieved: {len(data['positions'])} positions")
    return data


def test_place_meeple(game_id: str, tile_id: str, feature_type: str, position: str) -> Dict[str, Any]:
    """Test placing a meeple."""
    print(f"Testing: POST /api/game/{game_id}/place-meeple")
    payload = {
        "tileId": tile_id,
        "featureType": feature_type,
        "position": position
    }
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/place-meeple", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data["success"] is True
    assert len(data["gameState"]["meeples"]) >= 1
    assert data["gameState"]["meeplesRemaining"] == 6  # Should have one less
    
    print(f"✓ Meeple placed successfully on {feature_type} at {position}")
    return data


def test_skip_meeple(game_id: str) -> Dict[str, Any]:
    """Test skipping meeple placement."""
    print(f"Testing: POST /api/game/{game_id}/skip-meeple")
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/skip-meeple")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data["gameId"] == game_id
    
    print(f"✓ Meeple placement skipped successfully")
    return data


def test_invalid_tile_placement(game_id: str, tile_id: str):
    """Test invalid tile placement."""
    print(f"Testing: Invalid tile placement")
    payload = {
        "tileId": tile_id,
        "x": 999,  # Invalid position
        "y": 999,
        "rotation": 0
    }
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/place-tile", json=payload)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    print(f"✓ Invalid tile placement correctly rejected")


def test_game_not_found():
    """Test accessing non-existent game."""
    print(f"Testing: Game not found")
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{BASE_URL}/api/game/{fake_id}/state")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print(f"✓ Non-existent game correctly handled")


def run_integration_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Carcassonne Backend API Integration Tests")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Create a game
        game_data = test_create_game()
        game_id = game_data["gameId"]
        current_tile_id = game_data["currentTile"]["id"]
        print()
        
        # Test 2: Get game state
        test_get_game_state(game_id)
        print()
        
        # Test 3: Get valid positions
        valid_positions = test_get_valid_positions(game_id)
        print()
        
        # Test 4: Place a tile
        if valid_positions["positions"]:
            pos = valid_positions["positions"][0]
            x, y = pos["x"], pos["y"]
            rotation = pos["validRotations"][0]
            
            place_result = test_place_tile(game_id, current_tile_id, x, y, rotation)
            placed_tile_id = place_result["gameState"]["placedTiles"][-1]["id"]
            print()
            
            # Test 5: Get valid meeple positions
            meeple_positions = test_get_valid_meeple_positions(game_id, placed_tile_id)
            print()
            
            # Test 6: Place a meeple (if valid positions exist)
            if meeple_positions["positions"]:
                meeple_pos = meeple_positions["positions"][0]
                test_place_meeple(
                    game_id,
                    placed_tile_id,
                    meeple_pos["featureType"],
                    meeple_pos["position"]
                )
                print()
        
        # Test 7: Create another game and test skip meeple
        game_data2 = test_create_game()
        game_id2 = game_data2["gameId"]
        current_tile_id2 = game_data2["currentTile"]["id"]
        print()
        
        # Get valid positions and place a tile
        valid_positions2 = test_get_valid_positions(game_id2)
        if valid_positions2["positions"]:
            pos = valid_positions2["positions"][0]
            test_place_tile(game_id2, current_tile_id2, pos["x"], pos["y"], pos["validRotations"][0])
            print()
            
            # Skip meeple placement
            test_skip_meeple(game_id2)
            print()
        
        # Test 8: Invalid tile placement
        test_invalid_tile_placement(game_id, current_tile_id)
        print()
        
        # Test 9: Game not found
        test_game_not_found()
        print()
        
        print("=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        return 1
    except requests.exceptions.ConnectionError:
        print()
        print("=" * 60)
        print("❌ Connection error: Is the server running on http://localhost:3000?")
        print("=" * 60)
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Unexpected error: {e}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    # Wait a bit for server to start
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    sys.exit(run_integration_tests())
