"""Entry point for running the Carcassonne backend server."""

import uvicorn
from hackday_carcassone_backend.main import app


def main():
    """Run the FastAPI application."""
    uvicorn.run(app, host="0.0.0.0", port=3000)


if __name__ == "__main__":
    main()
