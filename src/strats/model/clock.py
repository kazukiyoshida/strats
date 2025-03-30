from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Clock:
    t: Optional[datetime] = field(default=None)
