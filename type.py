from dataclasses import dataclass

@dataclass
class Type:
    method: str
    path: str
    has_query: bool
    has_body: bool

    def __str__(self):
        s = "---- HTTP Message Type ----\n" \
            f"Method: {self.method}\n" \
            f"Path: {self.path}\n" \
            f"Has Query: {self.has_query}\n" \
            f"Has Body: {self.has_body}"
        return s