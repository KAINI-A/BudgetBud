# BudgetBud

***Budget Buddy***

This is a personal budgeting app built using Python and Tkinter. I created it as my final project for my computer programming course, but I also wanted something practical for myself — a way to manage my income, expenses, and savings goals easily in one place.

Features

- Tabbed GUI with Transactions, Goals, Categories, and Dashboard
- Add/edit/delete transactions and savings goals
- Pie chart showing spending by category
- Bar chart comparing income, expenses, and savings
- Data saved locally in a JSON file (`records.json`)
- Date and time are auto-filled when adding new transactions

Why I Made This

I wanted to build something real using what I learned in class, and I also just needed a basic budget tracker for my own use. This project helped me apply what I know, and also pushed me to learn new things like saving data and showing charts inside a Python app.

What I Learned (and Where)

Tkinter (GUI)

- [Codemy.com YouTube](https://www.youtube.com/@Codemycom) — beginner-friendly projects
- [freeCodeCamp Tkinter crash course](https://www.youtube.com/watch?v=YXPyB4XeYLA) — helped with overall structure

Matplotlib (Charts)

- [Corey Schafer YouTube](https://www.youtube.com/watch?v=UO98lJQ3QGI)
- Official Matplotlib docs (especially for pie/bar charts in GUIs)

JSON & File Handling

- StackOverflow (for lots of little issues with loading/saving)

How ChatGPT Helped

I used ChatGPT to help figure out certain parts of the code that were hard for me as a student, especially:

- Embedding Matplotlib charts inside a Tkinter GUI
- Designing helper functions like `to_decimal()` using `Decimal` (I didn’t know float was bad for money...)
- Handling category-based totals and goal progress bars
- Debugging issues while saving/loading JSON (like when I had strings instead of Decimal objects)
- Writing UI code for editing transactions and goals (dialogs with entry fields)


Small Touch: Backward Compatibility
One helpful thing ChatGPT suggested was a small snippet in the code:
if isinstance(data, list):
    data = {"transactions": data, "goals": []}

Educational Purpose

This project was developed for a college programming course (CS196 Final Project).
All code was reviewed, tested, and understood before submission.  
The intent was to learn and complete the project, not bypass effort.
