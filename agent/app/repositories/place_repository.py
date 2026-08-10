"""Repository for querying Chicago place data."""

import json
from pathlib import Path

from app.schemas import Place


DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "chicago_places.generated.json"
)


class PlaceRepository:
    """Provide structured access to the Chicago place dataset."""

    def __init__(self,dataset_path: Path = DEFAULT_DATASET_PATH,) -> None:
        self.dataset_path = dataset_path
        self._places = self._load_places()

    def _load_places(self) -> list[Place]:
        """Load and validate places from the dataset."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Place dataset not found: {self.dataset_path}"
            )

        raw_data = json.loads(
            self.dataset_path.read_text()
        )

        return [
            Place.model_validate(item)
            for item in raw_data
        ]

    def all(self) -> list[Place]:
        """Return all places."""
        return list(self._places)

    def get_by_id(self,provider_id: str,) -> Place | None:
        """Find a place by provider ID."""
        for place in self._places:
            if place.provider_id == provider_id:
                return place

        return None

    def find_by_category(self,category: str,) -> list[Place]:
        """Return places matching a category."""
        return [
            place
            for place in self._places
            if place.category == category
        ]

    def find_by_neighborhood(self,neighborhood: str,) -> list[Place]:
        """Return places in a neighborhood."""
        normalized = neighborhood.strip().lower()

        return [
            place
            for place in self._places
            if place.neighborhood.lower() == normalized
        ]

    def find_by_tags(self,tags: list[str],) -> list[Place]:
        """Return places matching at least one requested tag."""
        requested = {
            tag.strip().lower()
            for tag in tags
        }

        matches: list[Place] = []

        for place in self._places:
            place_tags = {
                tag.lower()
                for tag in place.tags
            }

            if requested & place_tags:
                matches.append(place)

        return matches