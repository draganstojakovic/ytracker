from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def get(self) -> 'State':
        pass

    @abstractmethod
    def add(self, new_value) -> 'State':
        pass

    @abstractmethod
    def remove(self, value) -> 'State':
        pass

    @abstractmethod
    def delete(self) -> 'State':
        pass


class YouTubeIDs(State):
    __slots__ = '_youtube_urls'

    def __init__(self):
        self._youtube_urls: list[str] | list[None] = []

    @property
    def get(self) -> list[str] | list[None]:
        return self._youtube_urls

    def add(self, new_url: str) -> 'YouTubeIDs':
        self._youtube_urls = [*self._youtube_urls, new_url]
        return self

    def remove(self, value: str) -> 'YouTubeIDs':
        self._youtube_urls = [x for x in self._youtube_urls if x != value]
        return self

    def delete(self) -> 'YouTubeIDs':
        self._youtube_urls = []
        return self
