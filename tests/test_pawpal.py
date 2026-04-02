import sys
from pathlib import Path
from datetime import date, timedelta

import pytest

# Add parent directory to path so we can import pawpal_system
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_sort_by_time_ascending_uses_duration_minutes_hhmm():
    """Verify Scheduler.sort_by_time() sorts by HH:MM computed from duration_minutes."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    tasks = [
        Task(name="task_130", duration_minutes=130, priority="low", category="care"),
        Task(name="task_5", duration_minutes=5, priority="high", category="care"),
        Task(name="task_65", duration_minutes=65, priority="medium", category="care"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.name for task in sorted_tasks] == ["task_5", "task_65", "task_130"]


def test_sort_by_time_descending_uses_duration_minutes_hhmm():
    """Verify Scheduler.sort_by_time() supports descending chronological sort order."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    tasks = [
        Task(name="task_5", duration_minutes=5, priority="high", category="care"),
        Task(name="task_130", duration_minutes=130, priority="low", category="care"),
        Task(name="task_65", duration_minutes=65, priority="medium", category="care"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks, descending=True)

    assert [task.name for task in sorted_tasks] == ["task_130", "task_65", "task_5"]


def test_sort_by_time_uses_name_tie_breaker_for_equal_duration():
    """Verify deterministic ordering when two tasks have the same duration."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    tasks = [
        Task(name="beta", duration_minutes=30, priority="high", category="care"),
        Task(name="alpha", duration_minutes=30, priority="high", category="care"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.name for task in sorted_tasks] == ["alpha", "beta"]


def test_filter_tasks_by_completion_status_only():
    """Verify filtering by completion status returns only matching tasks."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    feed_task = Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed")
    walk_task = Task(name="walk_lucky", duration_minutes=30, priority="medium", category="walk")
    walk_task.mark_completed()
    lucky.add_task(feed_task)
    lucky.add_task(walk_task)

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    completed_tasks = scheduler.filter_tasks(is_completed=True)
    incomplete_tasks = scheduler.filter_tasks(is_completed=False)

    assert [task.name for task in completed_tasks] == ["walk_lucky"]
    assert [task.name for task in incomplete_tasks] == ["feed_lucky"]


def test_filter_tasks_by_pet_name_only():
    """Verify filtering by pet name includes only tasks for that pet."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    mochi = Pet(name="Mochi", species="cat", age=2)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    mochi.add_task(Task(name="litter_mochi", duration_minutes=15, priority="high", category="litter"))

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky, mochi])
    scheduler = Scheduler(owner)

    lucky_tasks = scheduler.filter_tasks(pet_name="  lucky  ")

    assert [task.name for task in lucky_tasks] == ["feed_lucky"]


def test_filter_tasks_by_completion_and_pet_name():
    """Verify filters can be combined to narrow the task list."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    mochi = Pet(name="Mochi", species="cat", age=2)

    lucky_done = Task(name="walk_lucky", duration_minutes=30, priority="medium", category="walk")
    lucky_done.mark_completed()
    lucky_todo = Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed")
    mochi_done = Task(name="litter_mochi", duration_minutes=15, priority="high", category="litter")
    mochi_done.mark_completed()

    lucky.add_task(lucky_done)
    lucky.add_task(lucky_todo)
    mochi.add_task(mochi_done)

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky, mochi])
    scheduler = Scheduler(owner)

    filtered = scheduler.filter_tasks(is_completed=True, pet_name="Lucky")

    assert [task.name for task in filtered] == ["walk_lucky"]


def test_daily_task_next_due_date_uses_timedelta_one_day():
    """Verify daily tasks advance to today + 1 day using timedelta."""
    task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
        due_date=date(2026, 4, 1),
    )

    next_due_date = task.get_next_due_date(date(2026, 4, 1))

    assert next_due_date == date(2026, 4, 2)


def test_weekly_task_next_due_date_uses_timedelta_seven_days():
    """Verify weekly tasks advance by exactly 7 days using timedelta."""
    task = Task(
        name="groom_lucky",
        duration_minutes=20,
        priority="medium",
        category="grooming",
        frequency="weekly",
        due_date=date(2026, 4, 1),
    )

    next_due_date = task.get_next_due_date(date(2026, 4, 1))

    assert next_due_date == date(2026, 4, 8)


def test_complete_task_for_pet_creates_next_recurring_instance():
    """Verify completing a recurring task appends the next occurrence to the same pet."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    recurring_task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
        due_date=date(2026, 4, 1),
    )
    lucky.add_task(recurring_task)

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    next_task = scheduler.complete_task_for_pet("Lucky", "feed_lucky", completed_on=date(2026, 4, 1))

    assert recurring_task.is_done()
    assert next_task is not None
    assert next_task.get_due_date() == date(2026, 4, 2)
    assert next_task.get_name() == "feed_lucky_2026-04-02"
    assert [task.get_name() for task in lucky.get_tasks()] == ["feed_lucky", "feed_lucky_2026-04-02"]


def test_detect_schedule_conflicts_for_different_pets_returns_warning():
    """Verify conflicts at the same time across pets produce a warning message."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    mochi = Pet(name="Mochi", species="cat", age=2)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    mochi.add_task(Task(name="litter_mochi", duration_minutes=15, priority="high", category="litter"))

    owner = Owner(name="Jordan", available_time_minutes=90, preferences=[], pets=[lucky, mochi])
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_schedule_conflicts(
        {"feed_lucky": "09:00", "litter_mochi": "09:00"}
    )

    assert len(warnings) == 1
    assert "multi-pet conflict at 09:00" in warnings[0]


def test_detect_schedule_conflicts_for_same_pet_returns_warning():
    """Verify two tasks for one pet at the same time produce a same-pet warning."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    lucky.add_task(Task(name="walk_lucky", duration_minutes=30, priority="medium", category="walk"))

    owner = Owner(name="Jordan", available_time_minutes=90, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_schedule_conflicts(
        {"feed_lucky": "07:30", "walk_lucky": "07:30"}
    )

    assert len(warnings) == 1
    assert "same-pet conflict at 07:30" in warnings[0]


def test_detect_schedule_conflicts_invalid_time_returns_warning_not_exception():
    """Verify invalid times are reported as warnings without raising exceptions."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))

    owner = Owner(name="Jordan", available_time_minutes=90, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_schedule_conflicts({"feed_lucky": "9:00"})

    assert len(warnings) == 1
    assert "invalid time '9:00'" in warnings[0]


def test_filter_tasks_returns_empty_for_pet_with_no_tasks():
    """Verify filtering is safe when a pet has no tasks."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks() == []
    assert scheduler.filter_tasks(is_completed=False) == []


def test_generate_plan_with_no_pets_returns_empty_result_and_message():
    """Verify planning works for owners without pets/tasks."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    result = scheduler.generate_plan()

    assert result.scheduled_tasks == []
    assert result.skipped_tasks == []
    assert result.summary == "Scheduled 0 task(s), skipped 0 task(s). Used 0/60 minutes."
    assert scheduler.explain_plan(result) == "No tasks available to plan."


def test_complete_task_for_pet_raises_for_unknown_pet_or_task():
    """Verify completion fails clearly for unknown pet/task names."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    with pytest.raises(ValueError, match="task 'feed_lucky' not found for pet 'Mochi'"):
        scheduler.complete_task_for_pet("Mochi", "feed_lucky")

    with pytest.raises(ValueError, match="task 'walk_lucky' not found for pet 'Lucky'"):
        scheduler.complete_task_for_pet("Lucky", "walk_lucky")


def test_complete_as_needed_task_marks_done_and_creates_no_next_instance():
    """Verify one-off tasks are completed without creating recurring follow-up tasks."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    one_off = Task(
        name="vet_visit_lucky",
        duration_minutes=25,
        priority="high",
        category="health",
        frequency="as_needed",
    )
    lucky.add_task(one_off)
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    next_task = scheduler.complete_task_for_pet("Lucky", "vet_visit_lucky")

    assert one_off.is_done()
    assert next_task is None
    assert [task.name for task in lucky.get_tasks()] == ["vet_visit_lucky"]


def test_recurring_next_due_date_without_due_date_uses_today_fallback():
    """Verify recurring next dates use date.today() when no base date is provided."""
    daily_task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
    )
    weekly_task = Task(
        name="groom_lucky",
        duration_minutes=20,
        priority="medium",
        category="grooming",
        frequency="weekly",
    )

    assert daily_task.get_next_due_date() == date.today() + timedelta(days=1)
    assert weekly_task.get_next_due_date() == date.today() + timedelta(days=7)


def test_recurring_next_due_date_handles_calendar_boundaries():
    """Verify recurring dates cross month/year boundaries correctly."""
    daily_task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
    )
    weekly_task = Task(
        name="groom_lucky",
        duration_minutes=20,
        priority="medium",
        category="grooming",
        frequency="weekly",
    )

    assert daily_task.get_next_due_date(date(2026, 1, 31)) == date(2026, 2, 1)
    assert weekly_task.get_next_due_date(date(2026, 12, 28)) == date(2027, 1, 4)


def test_complete_recurring_task_raises_when_next_occurrence_name_collides():
    """Verify duplicate recurring names surface a clear uniqueness error."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    recurring_task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
        due_date=date(2026, 4, 1),
    )
    existing_next_task = Task(
        name="feed_lucky_2026-04-02",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
        due_date=date(2026, 4, 2),
    )
    lucky.add_task(recurring_task)
    lucky.add_task(existing_next_task)

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    with pytest.raises(ValueError, match="task name 'feed_lucky_2026-04-02' already exists"):
        scheduler.complete_task_for_pet("Lucky", "feed_lucky", completed_on=date(2026, 4, 1))


def test_sort_by_time_returns_empty_for_empty_task_list():
    """Verify sorting handles empty input lists."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    assert scheduler.sort_by_time([]) == []


def test_sort_by_time_handles_large_durations():
    """Verify sorting still works when durations are very large."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    tasks = [
        Task(name="short", duration_minutes=90, priority="high", category="care"),
        Task(name="long", duration_minutes=24 * 60 + 5, priority="high", category="care"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.name for task in sorted_tasks] == ["short", "long"]


def test_generate_plan_exact_time_budget_schedules_all_tasks():
    """Verify exact available minutes schedules all pending tasks."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    lucky.add_task(Task(name="walk_lucky", duration_minutes=20, priority="medium", category="walk"))
    owner = Owner(name="Jordan", available_time_minutes=30, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    result = scheduler.generate_plan()

    assert [task.name for task in result.scheduled_tasks] == ["feed_lucky", "walk_lucky"]
    assert result.skipped_tasks == []


def test_generate_plan_with_zero_available_time_skips_all_tasks():
    """Verify zero available minutes skips every incomplete task."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    lucky.add_task(Task(name="walk_lucky", duration_minutes=20, priority="medium", category="walk"))
    owner = Owner(name="Jordan", available_time_minutes=0, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    result = scheduler.generate_plan()

    assert result.scheduled_tasks == []
    assert [task.name for task in result.skipped_tasks] == ["feed_lucky", "walk_lucky"]
