"""Launch the FeederIQ Streamlit frontend."""
import subprocess
import sys
from pathlib import Path

# Ensure we run from the project root
project_root = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run",
                    str(project_root / "feederiq" / "frontend" / "app.py"),
                    "--server.port", "8501"],
                   cwd=str(project_root))
