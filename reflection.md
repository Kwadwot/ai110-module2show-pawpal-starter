# PawPal+ Project Reflection

## 1. System Design
Three core actions a user should be able to perform:
- Add a pet
- Add and view tasks
- Create a plan/ schedule base on task constaints (time available, priority, owner preferences)

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My UML design details the skeleton for the PawPal system by creating four classes for the user (Owner), pet (Pet), tasks (Task), and scheduling (Scheduler). The Owner owns a pet, which has tasks it need to completed (walks, feeding, etc.), and scheduler take an owner object and outputs a plan/schedule based on the owner's contraints and their pet's necessary tasks.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I revised the design from one-pet ownership to multi-pet ownership by changing Owner to store a list of pets. I also simplified relationships by making Scheduler depend only on Owner and collect tasks through the owner’s pets instead of storing a separate pet reference. To make planning explanations clearer, I introduced a PlanResult object that separates scheduled tasks, skipped tasks, and reasoning. I introduced a naming rule where each task name is built from category plus pet name (for example, feed_lucky), and I added duplicate prevention so a pet cannot have two tasks with the same identifier. These changes made the class relationships more consistent and the scheduler output easier to explain and test.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

    Scheduler considers time (owner's available time and task duration) and task priority
- How did you decide which constraints mattered most?

    I determined which constraints to prioritize based on what revelant to scheduling tasks for the Owner based on their pets' necessary tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

     The scheduler makes a few practical tradeoffs for this project scope:

     1. Conflict detection checks exact HH:MM matches only, instead of full overlap math using start time plus duration.
         This is reasonable because it keeps conflict logic simple, predictable, and easy to test for a first implementation.

     2. The current app flow does not let users mark tasks as completed from the UI.
         This is reasonable for now because the core goal was to implement planning behavior first; completion tracking can be added as a follow-up interaction layer.

     3. Task category input is currently fixed to "care" in the UI instead of letting users choose from multiple categories.
         This is reasonable because category does not yet change scheduling priority, so a single default category reduced UI complexity while core algorithms were being validated.


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

    I used AI tools for design brainstorming/ planning, debugging, refactoring, and creating test.
- What kinds of prompts or questions were most helpful?

    The kinds of prompts I found most helpful were designing/planning class relationships, reviewing implemented code, testing edge cases, brainstorming class upgrades (attributes or functions), and refactoring (especially when I had to start over).

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

    When implementing the Scheduler functions for the UI in `app.py`, I reviewed and decided to undo the AI's suggested code changes because it opted to recreate functions and code already covered by the Scheduler for handling tasks. These changes would have introduced redundant code and messied the structured  of the file.
- How did you evaluate or verify what the AI suggested?

    I evaluated the code by systematically comparing the code signature of both the code implements and the already completed Scheduler class. After comfirming major similarities (and mostly exact code), I prompted the AI to instead use the `st.session_state`'s Scheduler object and contained methods instead, drastically reducing the lines of code needed for the implementation.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

    The tests I covered include task completion state changes, task addition, sorting by duration, filtering by completion and pet name, recurring task next-date logic and follow-up creation, conflict detection (same-pet and multi-pet), and important edge cases such as empty task/pet states, not-found completion paths, non-recurring completion behavior, calendar-boundary recurring dates, duplicate recurring name collisions, and plan-generation boundaries. These tests were important to ensure the user is able to input valid information, receive feedback (confirmations or warnings)m, and then receive a generate schedule.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

    I am fairly confident the the Scheduler works correctly and smartly; however, I would like to implement and test user input for task category and completion during task creation. I would also want to implement updates for the task attributes (and that of other classes).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

    I am very happy that I completed the implementation of the core logic and it functions well with the client side (UI).

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

    I would add update logic to task attributes for the user and the missing task complete and category input functions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

    I learned the advantage that comes from creating a new chat when working on different parts/ stages of a project with the assistance of AI. I used to largely keep to one long chat session when working on projects (mostly because I was actively coding everything and sparsely used the AI), but I now see the disavantage of that approach.
