"""Optional static fallback repository used for tests/offline development."""
import json
from pathlib import Path
from app.schemas import Place
class PlaceRepository:
    def __init__(self, path: Path | None = None):
        self.path=path or Path(__file__).resolve().parents[1]/"data"/"fallback_places.json"
        if self.path.exists():
            self._places=[Place.model_validate(x) for x in json.loads(self.path.read_text())]
        else: self._places=[]
    def all(self): return list(self._places)
