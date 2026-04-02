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

    One tradeoff is that the scheduler only checks for exact time matches when it detects conflicts instead of calculating overlapping task durations. That keeps the logic lightweight and easy to explain, but it can miss conflicts where two tasks overlap without starting at the exact same time.


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
