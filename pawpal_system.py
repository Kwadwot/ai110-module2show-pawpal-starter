from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    special_needs: List[str] = field(default_factory=list)

    def get_relevant_tasks(self, all_tasks: List["Task"]) -> List["Task"]:
        """Return tasks relevant to this pet (species/needs filter)."""
        raise NotImplementedError

    def update_info(self, name: str = None, species: str = None, age: int = None, special_needs: List[str] = None):
        raise NotImplementedError


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str = "general"
    time_constraint: str = "any"

    def is_feasible_at(self, time_slot: Tuple[int, int]) -> bool:
        """Check if task fits in the given time slot."""
        raise NotImplementedError

    def get_priority_score(self) -> int:
        """Convert priority string to numeric score for sorting."""
        raise NotImplementedError


class Schedule:
    def __init__(self):
        self.scheduled_tasks: List[Dict] = []
        self.total_time_used: int = 0
        self.explanation: str = ""

    def add_task(self, task: Task, start_time: int):
        raise NotImplementedError

    def generate_explanation(self):
        raise NotImplementedError

    def display_plan(self) -> str:
        raise NotImplementedError


class Owner:
    def __init__(
        self,
        name: str,
        available_time_per_day: int = 120,
        preferences: Dict = None,
        pets: List[Pet] = None,
    ):
        self.name = name
        self.available_time_per_day = available_time_per_day
        self.preferences: Dict = preferences or {}
        self.pets: List[Pet] = pets or []
        self.tasks: List[Task] = []
        self.schedule: Schedule = Schedule()

    def get_available_slots(self) -> List[Tuple[int, int]]:
        raise NotImplementedError

    def add_pet(self, pet: Pet):
        raise NotImplementedError

    def add_task(self, task: Task):
        raise NotImplementedError

    def create_schedule(self):
        raise NotImplementedError

    def update_preferences(self, new_prefs: Dict):
        raise NotImplementedError