class GeocodingError(Exception):
    """Raised when geocoding fails."""

    def __init__(self, message: str, address: str):
        self.address: str = address
        super().__init__(f"{message} (address={address!r})")
