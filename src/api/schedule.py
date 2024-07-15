from dataclasses import dataclass


@dataclass
class Schedule:
    name: str
    date: str
    kind: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name"),
            date=data.get("date"),
            kind=data.get("kind"),
        )

    @property
    def is_working_day(self):
        return self.kind == "working_day"
