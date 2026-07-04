"""Launch the FeederIQ FastAPI backend."""
import sys
from pathlib import Path

# Ensure the project root is on the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("feederiq.backend.main:app", host="0.0.0.0", port=8000, reload=True)
