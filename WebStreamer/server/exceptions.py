
class InvalidHash(Exception):
    message = "Invalid hash"

class FIleNotFound(Exception):
    message = "File not found"

class FIleExpired(Exception):
    def __init__(self, text) -> None:
        self.text=text

    @property
    def message(self):
        return self.text