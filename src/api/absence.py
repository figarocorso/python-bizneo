from dataclasses import dataclass


@dataclass
class Absence:
    absence_id: int
    kind_id: int
    user_id: int
    start_at: str
    end_at: str
    comment: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            absence_id=data.get("id"),
            kind_id=data.get("kind_id"),
            user_id=data.get("user_id"),
            start_at=data.get("start_at"),
            end_at=data.get("end_at"),
            comment=data.get("comment", ""),
        )

    def matches_dates(self, start_at: str, end_at: str) -> bool:
        """Check if this absence matches the given date range."""
        return self.start_at == start_at and self.end_at == end_at

    def matches_user(self, user_id: int) -> bool:
        """Check if this absence belongs to the given user."""
        return self.user_id == user_id
