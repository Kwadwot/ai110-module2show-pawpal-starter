import importlib.util
from pathlib import Path
import sys


# Load pawpal_system.py from the same directory as this file.
MODULE_PATH = Path(__file__).resolve().parent / "pawpal_system.py"

spec = importlib.util.spec_from_file_location("pawpal_system", MODULE_PATH)
if spec is None or spec.loader is None:
	raise ImportError("Could not load pawpal_system module.")

pawpal_system = importlib.util.module_from_spec(spec)
sys.modules["pawpal_system"] = pawpal_system
spec.loader.exec_module(pawpal_system)

Owner = pawpal_system.Owner
Pet = pawpal_system.Pet
Scheduler = pawpal_system.Scheduler
Task = pawpal_system.Task


def create_demo_data() -> Owner:
	lucky = Pet(name="Lucky", species="dog", age=4)
	mochi = Pet(name="Mochi", species="cat", age=2)

	# Intentionally add tasks out of time order to demonstrate sort_by_time().
	lucky.add_task(
		Task(
			name=Task.build_task_name("walk", lucky.name),
			duration_minutes=95,
			priority="medium",
			category="walk",
			description="Long park walk.",
			frequency="daily",
		)
	)
	lucky.add_task(
		Task(
			name=Task.build_task_name("feed", lucky.name),
			duration_minutes=10,
			priority="high",
			category="feed",
			description="Serve morning meal.",
			frequency="daily",
		)
	)

	lucky_play = Task(
		name=Task.build_task_name("play", lucky.name),
		duration_minutes=35,
		priority="low",
		category="enrichment",
		description="Indoor enrichment game.",
		frequency="daily",
	)
	lucky_play.mark_completed()
	lucky.add_task(lucky_play)

	mochi.add_task(
		Task(
			name=Task.build_task_name("litter_clean", mochi.name),
			duration_minutes=15,
			priority="high",
			category="litter_clean",
			description="Clean litter box and refresh litter.",
			frequency="daily",
		)
	)
	mochi.add_task(
		Task(
			name=Task.build_task_name("brushing", mochi.name),
			duration_minutes=5,
			priority="low",
			category="grooming",
			description="Quick brushing session.",
			frequency="daily",
		)
	)

	return Owner(
		name="Jordan",
		available_time_minutes=90,
		preferences=["prioritize feeding", "include enrichment"],
		pets=[lucky, mochi],
	)


def minutes_to_hhmm(total_minutes: int) -> str:
	"""Format a minute duration as HH:MM."""
	hours, minutes = divmod(total_minutes, 60)
	return f"{hours:02d}:{minutes:02d}"


def print_schedule(owner: Owner) -> None:
	scheduler = Scheduler(owner)
	result = scheduler.generate_plan()

	print("Today's Schedule")
	print("-" * 16)
	print(f"Owner: {owner.get_name()}")
	print(f"Time available: {owner.get_available_time()} minutes")
	print("")

	if not result.scheduled_tasks:
		print("No tasks could be scheduled today.")
	else:
		for i, task in enumerate(result.scheduled_tasks, start=1):
			print(
				f"{i}. {task.get_name()} | {task.get_duration()} min | "
				f"priority={task.get_priority()}"
			)

	print("")
	print(scheduler.explain_plan(result))


def print_sorting_and_filtering_demo(owner: Owner) -> None:
	"""Print terminal output proving sort_by_time() and filter_tasks() behavior."""
	scheduler = Scheduler(owner)
	all_tasks = scheduler.collect_tasks_from_owner_pets()

	print("\nSorting + Filtering Demo")
	print("-" * 24)

	print("All tasks (in insertion order):")
	for task in all_tasks:
		print(
			f"- {task.get_name()} | duration={task.get_duration()} min "
			f"({minutes_to_hhmm(task.get_duration())}) | done={task.is_done()}"
		)

	print("\nSorted by computed HH:MM from duration:")
	sorted_tasks = scheduler.sort_by_time(all_tasks)
	for task in sorted_tasks:
		print(f"- {task.get_name()} -> {minutes_to_hhmm(task.get_duration())}")

	print("\nFiltered: completed tasks")
	for task in scheduler.filter_tasks(is_completed=True):
		print(f"- {task.get_name()} | done={task.is_done()}")

	print("\nFiltered: incomplete tasks for Lucky")
	for task in scheduler.filter_tasks(is_completed=False, pet_name="Lucky"):
		print(f"- {task.get_name()} | done={task.is_done()}")


def print_conflict_demo(owner: Owner) -> None:
	"""Print terminal output proving detect_schedule_conflicts() warnings."""
	scheduler = Scheduler(owner)

	# Intentionally assign two tasks to the same time to trigger a warning.
	scheduled_times_by_task_name = {
		"feed_lucky": "09:00",
		"litter_clean_mochi": "09:00",
		"brushing_mochi": "09:30",
	}

	print("\nConflict Detection Demo")
	print("-" * 23)
	print("Assigned task times:")
	for task_name, hhmm in scheduled_times_by_task_name.items():
		print(f"- {task_name} at {hhmm}")

	conflict_warnings = scheduler.detect_schedule_conflicts(scheduled_times_by_task_name)

	if conflict_warnings:
		print("\nConflict warnings:")
		for warning in conflict_warnings:
			print(f"- {warning}")
	else:
		print("\nNo conflicts detected.")


if __name__ == "__main__":
	demo_owner = create_demo_data()
	print_schedule(demo_owner)
	print_sorting_and_filtering_demo(demo_owner)
	print_conflict_demo(demo_owner)
