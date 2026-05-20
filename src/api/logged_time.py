from dataclasses import dataclass, field


def _parse_hours(time_str):
    if not time_str:
        return 0.0
    parts = time_str.split(":")
    h = int(parts[0])
    m = int(parts[1]) if len(parts) > 1 else 0
    s = int(parts[2]) if len(parts) > 2 else 0
    return h + m / 60 + s / 3600


@dataclass
class LoggedTime:
    date: str
    total_hours: float
    project_hours: float = 0.0
    project_ids: set = field(default_factory=set)

    @classmethod
    def from_dict(cls, data: dict):
        lt = data.get("logged_time", {})
        project_hours = 0.0
        project_ids = set()
        for lh in lt.get("logged_hours", []):
            projects = lh.get("projects") or []
            if not projects:
                continue
            start = lh.get("start_at")
            end = lh.get("end_at")
            if start and end:
                duration = _parse_hours(end) - _parse_hours(start)
                if duration < 0:
                    duration += 24
                project_hours += duration
            project_ids.update(projects)
        return cls(
            date=lt.get("date"),
            total_hours=float(lt.get("total_hours")),
            project_hours=project_hours,
            project_ids=project_ids,
        )

    @property
    def has_logged_time(self):
        return self.total_hours > 0

    @property
    def regular_hours(self):
        return self.total_hours - self.project_hours

    @property
    def has_projects(self):
        return bool(self.project_ids)
