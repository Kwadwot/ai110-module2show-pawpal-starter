from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from dataclasses import dataclass, field


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
FREQUENCY_DAILY = "daily"
FREQUENCY_WEEKLY = "weekly"
FREQUENCY_AS_NEEDED = "as_needed"


@dataclass
class Task:
	name: str
	duration_minutes: int
	priority: str
	category: str
	description: str = ""
	frequency: str = FREQUENCY_DAILY
	is_completed: bool = False
	due_date: date | None = None

	def __post_init__(self) -> None:
		"""Validate task fields after initialization."""
		self.priority = self.priority.lower().strip()
		if self.priority not in PRIORITY_ORDER:
			raise ValueError("priority must be one of: high, medium, low")

		self.frequency = self.frequency.lower().strip()
		if self.frequency not in {
			FREQUENCY_DAILY,
			FREQUENCY_WEEKLY,
			FREQUENCY_AS_NEEDED,
		}:
			raise ValueError("frequency must be daily, weekly, or as_needed")

		if self.duration_minutes <= 0:
			raise ValueError("duration_minutes must be greater than 0")

	def get_name(self) -> str:
		"""Return the task name."""
		return self.name

	def get_duration(self) -> int:
		"""Return the task duration in minutes."""
		return self.duration_minutes

	def get_priority(self) -> str:
		"""Return the task priority level."""
		return self.priority

	def get_category(self) -> str:
		"""Return the task category."""
		return self.category

	def get_description(self) -> str:
		"""Return the task description."""
		return self.description

	def get_frequency(self) -> str:
		"""Return the task frequency label."""
		return self.frequency

	def get_due_date(self) -> date | None:
		"""Return the task due date, if one is set."""
		return self.due_date

	def mark_completed(self) -> None:
		"""Mark this task as completed."""
		self.is_completed = True

	def mark_incomplete(self) -> None:
		"""Mark this task as not completed."""
		self.is_completed = False

	def is_done(self) -> bool:
		"""Return whether this task is completed."""
		return self.is_completed

	def is_high_priority(self) -> bool:
		"""Return True if this task has high priority."""
		return self.priority == "high"

	def is_recurring(self) -> bool:
		"""Return True if this task repeats on a schedule."""
		return self.frequency in {FREQUENCY_DAILY, FREQUENCY_WEEKLY}

	def get_next_due_date(self, completed_on: date | None = None) -> date | None:
		"""Return the next due date for a recurring task."""
		if not self.is_recurring():
			return None

		base_date = completed_on or self.due_date or date.today()
		interval_days = 1 if self.frequency == FREQUENCY_DAILY else 7
		return base_date + timedelta(days=interval_days)

	def create_next_occurrence(self, completed_on: date | None = None) -> Task | None:
		"""Create the next recurring task instance, if applicable."""
		next_due_date = self.get_next_due_date(completed_on)
		if next_due_date is None:
			return None

		return Task(
			name=f"{self.name}_{next_due_date.isoformat()}",
			duration_minutes=self.duration_minutes,
			priority=self.priority,
			category=self.category,
			description=self.description,
			frequency=self.frequency,
			due_date=next_due_date,
		)

	@staticmethod
	def build_task_name(category: str, pet_name: str) -> str:
		"""Build a normalized task name from category and pet name."""
		normalized_category = "_".join(category.lower().strip().split())
		normalized_pet_name = "_".join(pet_name.lower().strip().split())
		return f"{normalized_category}_{normalized_pet_name}"


@dataclass
class PlanResult:
	scheduled_tasks: list[Task] = field(default_factory=list)
	skipped_tasks: list[Task] = field(default_factory=list)
	reasons_by_task_name: dict[str, str] = field(default_factory=dict)
	summary: str = ""


@dataclass
class Pet:
	name: str
	species: str
	age: int
	special_needs: list[str] = field(default_factory=list)
	tasks: list[Task] = field(default_factory=list)

	def __post_init__(self) -> None:
		"""Validate pet fields after initialization."""
		if self.age < 0:
			raise ValueError("age cannot be negative")

	def get_name(self) -> str:
		"""Return the pet name."""
		return self.name

	def get_species(self) -> str:
		"""Return the pet species."""
		return self.species

	def get_age(self) -> int:
		"""Return the pet age in years."""
		return self.age

	def get_special_needs(self) -> list[str]:
		"""Return a copy of the pet special-needs list."""
		return list(self.special_needs)

	def get_tasks(self) -> list[Task]:
		"""Return a copy of the pet tasks."""
		return list(self.tasks)

	def add_task(self, task: Task) -> None:
		"""Add a task if its name is unique for this pet."""
		if self.has_task(task.name):
			raise ValueError(f"task name '{task.name}' already exists for pet '{self.name}'")
		self.tasks.append(task)

	def remove_task(self, task_name: str) -> None:
		"""Remove a task by name from this pet."""
		for i, task in enumerate(self.tasks):
			if task.name == task_name:
				del self.tasks[i]
				return
		raise ValueError(f"task '{task_name}' not found for pet '{self.name}'")

	def has_task(self, task_name: str) -> bool:
		"""Return whether a task name already exists for this pet."""
		return any(task.name == task_name for task in self.tasks)

	def clear_tasks(self) -> None:
		"""Remove all tasks from this pet."""
		self.tasks.clear()


class Owner:
	def __init__(
		self,
		name: str,
		available_time_minutes: int,
		preferences: list[str],
		pets: list[Pet],
	) -> None:
		"""Initialize an owner with preferences, time, and pets."""
		if available_time_minutes < 0:
			raise ValueError("available_time_minutes cannot be negative")
		self.name = name
		self.available_time_minutes = available_time_minutes
		self.preferences = list(preferences)
		self.pets = list(pets)

	def get_name(self) -> str:
		"""Return the owner name."""
		return self.name

	def get_available_time(self) -> int:
		"""Return the owner's available care time in minutes."""
		return self.available_time_minutes

	def get_preferences(self) -> list[str]:
		"""Return a copy of owner preferences."""
		return list(self.preferences)

	def get_pets(self) -> list[Pet]:
		"""Return a copy of the owner's pets."""
		return list(self.pets)

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet if its name is unique for this owner."""
		if any(existing_pet.name == pet.name for existing_pet in self.pets):
			raise ValueError(f"pet '{pet.name}' already exists for owner '{self.name}'")
		self.pets.append(pet)

	def remove_pet(self, pet_name: str) -> None:
		"""Remove a pet by name from this owner."""
		for i, pet in enumerate(self.pets):
			if pet.name == pet_name:
				del self.pets[i]
				return
		raise ValueError(f"pet '{pet_name}' not found for owner '{self.name}'")

	def update_preferences(self, new_preferences: list[str]) -> None:
		"""Replace owner preferences with a new list."""
		self.preferences = list(new_preferences)

	def update_available_time(self, new_minutes: int) -> None:
		"""Update available care time in minutes."""
		if new_minutes < 0:
			raise ValueError("available time cannot be negative")
		self.available_time_minutes = new_minutes


class Scheduler:
	def __init__(self, owner: Owner) -> None:
		"""Initialize the scheduler with an owner."""
		self.owner = owner

	@staticmethod
	def _is_valid_hhmm(value: str) -> bool:
		"""Return True when a string matches strict 24-hour HH:MM format."""
		parts = value.split(":")
		if len(parts) != 2:
			return False

		hour_text, minute_text = parts
		if len(hour_text) != 2 or len(minute_text) != 2:
			return False
		if not hour_text.isdigit() or not minute_text.isdigit():
			return False

		hour = int(hour_text)
		minute = int(minute_text)
		return 0 <= hour <= 23 and 0 <= minute <= 59

	def detect_schedule_conflicts(self, scheduled_times_by_task_name: dict[str, str]) -> list[str]:
		"""Return warning messages for tasks that share the same scheduled time."""
		warnings: list[str] = []
		time_slots: dict[str, list[tuple[str, str]]] = defaultdict(list)

		for pet in self.owner.get_pets():
			for task in pet.get_tasks():
				time_value = scheduled_times_by_task_name.get(task.name)
				if time_value is None:
					continue

				normalized_time = time_value.strip()
				if not self._is_valid_hhmm(normalized_time):
					warnings.append(
						f"Warning: task '{task.name}' has invalid time '{time_value}'. Expected HH:MM."
					)
					continue

				time_slots[normalized_time].append((pet.name, task.name))

		for time_value, assignments in sorted(time_slots.items()):
			if len(assignments) < 2:
				continue

			task_descriptions = ", ".join(
				f"{task_name} ({pet_name})" for pet_name, task_name in assignments
			)
			conflict_type = "same-pet" if len({pet_name for pet_name, _ in assignments}) == 1 else "multi-pet"
			warnings.append(
				f"Warning: {conflict_type} conflict at {time_value} for {task_descriptions}."
			)

		return warnings

	def filter_tasks(
		self,
		*,
		is_completed: bool | None = None,
		pet_name: str | None = None,
	) -> list[Task]:
		"""Return tasks filtered by completion status and/or pet name."""
		filtered_tasks: list[Task] = []
		normalized_pet_name = pet_name.lower().strip() if pet_name is not None else None

		for pet in self.owner.get_pets():
			if normalized_pet_name is not None and pet.name.lower().strip() != normalized_pet_name:
				continue

			for task in pet.get_tasks():
				if is_completed is not None and task.is_done() != is_completed:
					continue
				filtered_tasks.append(task)

		return filtered_tasks

	def complete_task_for_pet(
		self,
		pet_name: str,
		task_name: str,
		*,
		completed_on: date | None = None,
	) -> Task | None:
		"""Complete a pet task and add the next recurring instance when applicable."""
		normalized_pet_name = pet_name.lower().strip()
		normalized_task_name = task_name.lower().strip()

		for pet in self.owner.get_pets():
			if pet.name.lower().strip() != normalized_pet_name:
				continue

			for task in pet.tasks:
				if task.name.lower().strip() != normalized_task_name:
					continue

				task.mark_completed()
				next_task = task.create_next_occurrence(completed_on)
				if next_task is not None:
					pet.add_task(next_task)
				return next_task

		raise ValueError(f"task '{task_name}' not found for pet '{pet_name}'")

	def collect_tasks_from_owner_pets(self) -> list[Task]:
		"""Collect all tasks from every pet owned by the owner."""
		all_tasks: list[Task] = []
		for pet in self.owner.get_pets():
			all_tasks.extend(pet.get_tasks())
		return all_tasks

	def generate_plan(self) -> PlanResult:
		"""Generate a prioritized plan within the owner's time limit."""
		available_time = self.owner.get_available_time()
		candidate_tasks = [task for task in self.collect_tasks_from_owner_pets() if not task.is_done()]

		sorted_tasks = sorted(
			candidate_tasks,
			key=lambda task: (PRIORITY_ORDER.get(task.priority, 99), task.duration_minutes),
		)

		result = PlanResult()
		used_time = 0

		for task in sorted_tasks:
			if used_time + task.duration_minutes <= available_time:
				result.scheduled_tasks.append(task)
				result.reasons_by_task_name[task.name] = (
					f"Scheduled: fits remaining time and priority '{task.priority}'."
				)
				used_time += task.duration_minutes
			else:
				result.skipped_tasks.append(task)
				result.reasons_by_task_name[task.name] = (
					"Skipped: not enough remaining time."
				)

		result.summary = (
			f"Scheduled {len(result.scheduled_tasks)} task(s), skipped "
			f"{len(result.skipped_tasks)} task(s). Used {used_time}/{available_time} minutes."
		)
		return result

	def explain_plan(self, result: PlanResult) -> str:
		"""Return a readable explanation of scheduling decisions."""
		if not result.scheduled_tasks and not result.skipped_tasks:
			return "No tasks available to plan."

		lines = [result.summary, "", "Task decisions:"]
		for task in result.scheduled_tasks + result.skipped_tasks:
			reason = result.reasons_by_task_name.get(task.name, "No reason recorded.")
			lines.append(f"- {task.name}: {reason}")

		return "\n".join(lines)

	@staticmethod
	def _duration_to_hhmm(duration_minutes: int) -> str:
		"""Convert a task duration in minutes into HH:MM format."""
		hours, minutes = divmod(duration_minutes, 60)
		return f"{hours:02d}:{minutes:02d}"

	@staticmethod
	def _duration_sort_key(task: Task) -> tuple[int, int, str]:
		"""Return a stable sort key derived from a task's duration minutes."""
		hours, minutes = divmod(task.duration_minutes, 60)
		return hours, minutes, task.name.lower()

	def sort_by_time(self, tasks: list[Task], *, descending: bool = False) -> list[Task]:
		"""Return tasks sorted by duration-derived HH:MM, with optional reverse order."""
		return sorted(tasks, key=self._duration_sort_key, reverse=descending)
