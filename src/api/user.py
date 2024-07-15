from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    email: str
    first_name: str
    last_name: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=data.get("id"),
            email=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )

    def has_keyword(self, keyword):
        return keyword.lower() in self.name.lower()
