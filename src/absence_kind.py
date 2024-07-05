from dataclasses import dataclass


@dataclass
class AbsenceKind:
    name: str
    kind_id: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name"),
            kind_id=data.get("id"),
        )

    def has_keyword(self, keyword):
        return keyword.lower() in self.name.lower()
