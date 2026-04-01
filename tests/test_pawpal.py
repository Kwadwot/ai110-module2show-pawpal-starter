import sys
from pathlib import Path

# Add parent directory to path so we can import pawpal_system
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task


def test_task_completion():
    """Verify that calling mark_completed() changes the task's status."""
    task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        description="Feed the dog.",
    )

    # Initially, task should not be completed
    assert not task.is_done(), "Task should not be completed initially"

    # Mark task as completed
    task.mark_completed()

    # Now task should be completed
    assert task.is_done(), "Task should be completed after calling mark_completed()"

    # Mark task as incomplete
    task.mark_incomplete()

    # Task should no longer be completed
    assert not task.is_done(), "Task should not be completed after calling mark_incomplete()"


def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Lucky", species="dog", age=4)

    # Initially, pet should have no tasks
    assert len(pet.get_tasks()) == 0, "Pet should have no tasks initially"

    # Create and add first task
    task1 = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
    )
    pet.add_task(task1)

    # Pet should now have 1 task
    assert len(pet.get_tasks()) == 1, "Pet should have 1 task after adding one"

    # Create and add second task
    task2 = Task(
        name="walk_lucky",
        duration_minutes=30,
        priority="medium",
        category="walk",
    )
    pet.add_task(task2)

    # Pet should now have 2 tasks
    assert len(pet.get_tasks()) == 2, "Pet should have 2 tasks after adding a second task"
