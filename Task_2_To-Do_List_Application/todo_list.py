
import json
import os
from datetime import datetime
from pathlib import Path

# Save tasks beside this Python file
FILE_NAME = Path(__file__).with_name("tasks.json")

PRIORITIES = {"1": "High", "2": "Medium", "3": "Low"}
PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}


def load_tasks():
    """Load tasks and upgrade older saved task formats."""
    if not FILE_NAME.exists():
        return []

    try:
        with FILE_NAME.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            print("Warning: Saved data is not a task list.")
            return []

        tasks = []

        for item in data:
            if not isinstance(item, dict) or not item.get("title"):
                continue

            priority = item.get("priority", "Medium")
            if priority not in PRIORITY_ORDER:
                priority = "Medium"

            due_date = item.get("due_date") or ""
            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    due_date = ""

            tasks.append({
                "title": str(item["title"]).strip(),
                "completed": item.get("completed", False) is True,
                "priority": priority,
                "due_date": due_date
            })

        return tasks

    except (OSError, json.JSONDecodeError):
        print("Warning: Could not read tasks.json.")
        print("Your existing file has not been overwritten.")
        return None


def save_tasks(tasks):
    """Save tasks safely, without overwriting the file on failure."""
    temp_file = FILE_NAME.with_suffix(".tmp")

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4, ensure_ascii=False)
            file.write("\n")

        os.replace(temp_file, FILE_NAME)
        return True

    except OSError as error:
        print(f"Error saving tasks: {error}")
        try:
            if temp_file.exists():
                temp_file.unlink()
        except OSError:
            pass
        return False


def get_task_number(tasks, prompt):
    """Return a valid task index, or None."""
    if not tasks:
        print("No tasks available.")
        return None

    show_tasks(tasks)

    try:
        number = int(input(prompt).strip())

        if 1 <= number <= len(tasks):
            return number - 1

        print(f"Please enter a number from 1 to {len(tasks)}.")

    except ValueError:
        print("Please enter a whole number.")

    return None


def show_tasks(tasks):
    if not tasks:
        print("\nNo tasks found.")
        return

    print("\n" + "=" * 42)
    print("YOUR TO-DO LIST")
    print("=" * 42)

    for number, task in enumerate(tasks, start=1):
        status = "Completed" if task["completed"] else "Pending"
        due = task["due_date"] or "Not set"

        print(f"\n{number}. {task['title']}")
        print(f"   Status   : {status}")
        print(f"   Priority : {task['priority']}")
        print(f"   Due date : {due}")


def choose_priority(current="Medium"):
    print("1. High")
    print("2. Medium")
    print("3. Low")
    print("Press Enter to keep the current priority.")

    choice = input(f"Priority [{current}]: ").strip()

    if not choice:
        return current

    if choice in PRIORITIES:
        return PRIORITIES[choice]

    print("Invalid choice. Keeping the current priority.")
    return current


def choose_due_date(current=""):
    print("Enter date as YYYY-MM-DD.")
    print("Press Enter for no deadline or to keep the current date.")

    value = input(f"Due date [{current or 'Not set'}]: ").strip()

    if not value:
        return current

    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        print("Invalid date. Keeping the previous date.")
        return current


def add_task(tasks):
    title = input("Enter task name: ").strip()

    if not title:
        print("Task name cannot be empty.")
        return

    priority = choose_priority()
    due_date = choose_due_date("")

    tasks.append({
        "title": title,
        "completed": False,
        "priority": priority,
        "due_date": due_date
    })

    if save_tasks(tasks):
        print("Task added and saved successfully!")
    else:
        print("Task was added in memory, but could not be saved.")


def update_status(tasks):
    index = get_task_number(tasks, "Choose task number: ")

    if index is None:
        return

    print("\n1. Pending")
    print("2. Completed")
    choice = input("Set status to (1-2): ").strip()

    if choice not in ("1", "2"):
        print("Invalid status choice. No changes made.")
        return

    tasks[index]["completed"] = (choice == "2")

    if save_tasks(tasks):
        print(f"Status updated to {'Completed' if choice == '2' else 'Pending'}.")


def edit_task(tasks):
    index = get_task_number(tasks, "Choose task number to edit: ")

    if index is None:
        return

    task = tasks[index]

    print("Press Enter to keep the existing task name.")
    title = input(f"Task name [{task['title']}]: ").strip()

    if title:
        task["title"] = title

    task["priority"] = choose_priority(task["priority"])
    task["due_date"] = choose_due_date(task["due_date"])

    if save_tasks(tasks):
        print("Task updated successfully!")


def delete_task(tasks):
    index = get_task_number(tasks, "Choose task number to delete: ")

    if index is None:
        return

    title = tasks[index]["title"]
    confirm = input(f"Delete '{title}'? (y/n): ").strip().lower()

    if confirm == "y":
        removed = tasks.pop(index)

        if save_tasks(tasks):
            print(f"Deleted '{removed['title']}'.")
        else:
            tasks.insert(index, removed)
            print("Deletion was not saved; task restored.")
    else:
        print("Deletion cancelled.")


def search_tasks(tasks):
    keyword = input("Search task name: ").strip().lower()

    if not keyword:
        print("Please enter a search word.")
        return

    results = [
        task for task in tasks
        if keyword in task["title"].lower()
    ]

    print(f"\nFound {len(results)} matching task(s).")
    show_tasks(results)


def filter_tasks(tasks):
    print("\n1. All tasks")
    print("2. Pending tasks")
    print("3. Completed tasks")

    choice = input("Choose filter (1-3): ").strip()

    if choice == "1":
        results = tasks
    elif choice == "2":
        results = [task for task in tasks if not task["completed"]]
    elif choice == "3":
        results = [task for task in tasks if task["completed"]]
    else:
        print("Invalid filter choice.")
        return

    show_tasks(results)


def sort_tasks(tasks):
    print("\n1. Priority (High to Low)")
    print("2. Due date (earliest first)")
    print("3. Task name (A-Z)")

    choice = input("Choose sorting option (1-3): ").strip()

    if choice == "1":
        results = sorted(
            tasks,
            key=lambda task: PRIORITY_ORDER[task["priority"]]
        )
    elif choice == "2":
        results = sorted(
            tasks,
            key=lambda task: (
                not bool(task["due_date"]),
                task["due_date"]
            )
        )
    elif choice == "3":
        results = sorted(
            tasks,
            key=lambda task: task["title"].lower()
        )
    else:
        print("Invalid sorting choice.")
        return

    show_tasks(results)


def main():
    tasks = load_tasks()

    # Stop rather than accidentally overwrite unreadable saved data.
    if tasks is None:
        print("Fix or back up tasks.json before restarting.")
        return

    print("Welcome to your To-Do List!")

    while True:
        print("\n========== TO-DO LIST ==========")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Set Task Status")
        print("4. Edit Task")
        print("5. Delete Task")
        print("6. Search Tasks")
        print("7. Filter Tasks")
        print("8. Sort Tasks")
        print("9. Save and Exit")

        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            show_tasks(tasks)
        elif choice == "3":
            update_status(tasks)
        elif choice == "4":
            edit_task(tasks)
        elif choice == "5":
            delete_task(tasks)
        elif choice == "6":
            search_tasks(tasks)
        elif choice == "7":
            filter_tasks(tasks)
        elif choice == "8":
            sort_tasks(tasks)
        elif choice == "9":
            if save_tasks(tasks):
                print("All tasks saved. Goodbye!")
                break
            print("Could not save tasks. Please try again.")
        else:
            print("Invalid choice. Please enter 1-9.")


if __name__ == "__main__":
    main()
