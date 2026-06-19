from abc import ABC, abstractmethod
from typing import List, Dict, Any


class MusicProvider(ABC):
    name: str = "unknown"

    @abstractmethod
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Return a list of normalized song dicts."""
        ...

    @abstractmethod
    def song(self, song_id: str) -> Dict[str, Any] | None:
        """Return a single normalized song dict or None."""
        ...

    def trending(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Optional. Default falls back to a generic search."""
        return self.search("trending", limit)
      
