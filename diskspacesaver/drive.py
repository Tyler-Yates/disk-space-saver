from dataclasses import dataclass


@dataclass
class Drive:
    drive_letter: str
    capacity_bytes: int
    free_bytes: int
    used_bytes: int
