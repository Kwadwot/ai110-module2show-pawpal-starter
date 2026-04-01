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
	lucky.add_task(
		Task(
			name=Task.build_task_name("walk", lucky.name),
			duration_minutes=30,
			priority="medium",
			category="walk",
			description="Afternoon walk around the block.",
			frequency="daily",
		)
	)
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

	return Owner(
		name="Jordan",
		available_time_minutes=50,
		preferences=["prioritize feeding", "include enrichment"],
		pets=[lucky, mochi],
	)


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


if __name__ == "__main__":
	demo_owner = create_demo_data()
	print_schedule(demo_owner)
