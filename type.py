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

    def __hash__(self):
        return hash((self.method, self.path, self.has_query, self.has_body))

    def __eq__(self, other):
        return (self.method, self.path, self.has_query, self.has_body) == (other.method, other.path, other.has_query, other.has_body)

    def __ne__(self, other):
        return not(self == other)