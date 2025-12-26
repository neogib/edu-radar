class GeocodingError(Exception):
    """Raised when geocoding fails."""

    address: str

    def __init__(self, message: str, address: str):
        self.address = address
        super().__init__(f"{message} (address={address!r})")
