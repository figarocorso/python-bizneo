from dataclasses import dataclass


@dataclass
class LoggedTime:
    date: int
    total_hours: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            date=data.get("logged_time", {}).get("date"),
            total_hours=data.get("logged_time", {}).get("total_hours"),
        )
