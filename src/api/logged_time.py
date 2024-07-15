from dataclasses import dataclass


@dataclass
class LoggedTime:
    date: int
    total_hours: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            date=data.get("logged_time", {}).get("date"),
            total_hours=float(data.get("logged_time", {}).get("total_hours")),
        )

    @property
    def has_logged_time(self):
        return self.total_hours > 0
