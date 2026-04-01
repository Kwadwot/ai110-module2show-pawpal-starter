from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
	name: str
	duration_minutes: int
	priority: str
	category: str

	def get_name(self) -> str:
		raise NotImplementedError

	def get_duration(self) -> int:
		raise NotImplementedError

	def get_priority(self) -> str:
		raise NotImplementedError

	def get_category(self) -> str:
		raise NotImplementedError

	def is_high_priority(self) -> bool:
		raise NotImplementedError


@dataclass
class Pet:
	name: str
	type: str
	age: int
	special_needs: list[str] = field(default_factory=list)
	tasks: list[Task] = field(default_factory=list)

	def get_name(self) -> str:
		raise NotImplementedError

	def get_type(self) -> str:
		raise NotImplementedError

	def get_age(self) -> int:
		raise NotImplementedError

	def get_special_needs(self) -> list[str]:
		raise NotImplementedError

	def get_tasks(self) -> list[Task]:
		raise NotImplementedError

	def add_task(self, task: Task) -> None:
		raise NotImplementedError

	def remove_task(self, task_name: str) -> None:
		raise NotImplementedError

	def clear_tasks(self) -> None:
		raise NotImplementedError


class Owner:
	def __init__(
		self,
		name: str,
		available_time_minutes: int,
		preferences: list[str],
		pet: Pet,
	) -> None:
		self.name = name
		self.available_time_minutes = available_time_minutes
		self.preferences = preferences
		self.pet = pet

	def get_name(self) -> str:
		raise NotImplementedError

	def get_available_time(self) -> int:
		raise NotImplementedError

	def get_preferences(self) -> list[str]:
		raise NotImplementedError

	def get_pet(self) -> Pet:
		raise NotImplementedError

	def update_preferences(self, new_preferences: list[str]) -> None:
		raise NotImplementedError

	def update_available_time(self, new_minutes: int) -> None:
		raise NotImplementedError


class Scheduler:
	def __init__(self, owner: Owner) -> None:
		self.owner = owner

	def generate_plan(self) -> tuple[list[Task], str]:
		raise NotImplementedError

	def explain_plan(self, plan: list[Task]) -> str:
		raise NotImplementedError
