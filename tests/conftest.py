import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("DR_MEMORY_PATH", str(Path(tempfile.mkdtemp()) / "memory.json"))
os.environ.setdefault("DR_AGENT_MODE", "offline")
