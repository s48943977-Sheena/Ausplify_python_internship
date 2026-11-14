"""
Enhanced To-Do List Application — Desktop GUI
Auspify Technologies — Python Development Internship

A modern Tkinter/ttk desktop GUI that shares the same persistent 'tasks.json'
file and atomic write architecture as todo_list.py.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

# Use the same data file as todo_list.py
FILE_NAME = Path(__file__).with_name("tasks.json")
PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}
PRIORITIES = ["High", "Medium", "Low"]


def load_tasks():
    """Load and migrate tasks from tasks.json safely."""
    if not FILE_NAME.exists():
        return []

    try:
        with FILE_NAME.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
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
        return []


def save_tasks(tasks):
    """Save tasks safely using an atomic temporary file swap."""
    temp_file = FILE_NAME.with_suffix(".tmp")
    try:
        with temp_file.open("w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
            f.write("\n")
        os.replace(temp_file, FILE_NAME)
        return True
    except OSError:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass
        return False


class TodoAppGUI(tk.Tk):
    """Modern Desktop To-Do List Application."""

    def __init__(self):
        super().__init__()
        self.title("To-Do List Application — Auspify Technologies")
        self.geometry("820x620")
        self.minsize(700, 500)

        # Apply modern ttk theme
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.tasks = load_tasks()
        self.active_filter = "All"
        self.active_sort = "Default"

        self._create_widgets()
        self.refresh_task_list()

    def _create_widgets(self):
        # Header banner
        header_frame = ttk.Frame(self, padding=(16, 12))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(
            header_frame,
            text="📝 To-Do List Manager",
            font=("Segoe UI", 16, "bold")
        )
        title_lbl.pack(side=tk.LEFT)

        subtitle_lbl = ttk.Label(
            header_frame,
            text="Auspify Python Internship — Task 2",
            font=("Segoe UI", 9, "italic")
        )
        subtitle_lbl.pack(side=tk.RIGHT, pady=4)

        # Input Frame (Card style)
        input_card = ttk.LabelFrame(self, text=" Add New Task ", padding=12)
        input_card.pack(fill=tk.X, padx=16, pady=4)

        # Title
        ttk.Label(input_card, text="Task Name:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.title_entry = ttk.Entry(input_card, width=32)
        self.title_entry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.title_entry.bind("<Return>", lambda e: self.add_task())

        # Priority
        ttk.Label(input_card, text="Priority:").grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_combo = ttk.Combobox(
            input_card,
            textvariable=self.priority_var,
            values=PRIORITIES,
            state="readonly",
            width=10
        )
        self.priority_combo.grid(row=0, column=3, sticky=tk.W, padx=4, pady=4)

        # Due date
        ttk.Label(input_card, text="Due Date (YYYY-MM-DD):").grid(row=0, column=4, sticky=tk.W, padx=4, pady=4)
        self.due_entry = ttk.Entry(input_card, width=14)
        self.due_entry.grid(row=0, column=5, sticky=tk.W, padx=4, pady=4)
        self.due_entry.bind("<Return>", lambda e: self.add_task())

        # Add Button
        add_btn = ttk.Button(input_card, text="➕ Add Task", command=self.add_task)
        add_btn.grid(row=0, column=6, padx=8, pady=4)

        # Controls & Filter Bar
        ctrl_frame = ttk.Frame(self, padding=(16, 6))
        ctrl_frame.pack(fill=tk.X)

        # Search box
        ttk.Label(ctrl_frame, text="🔍 Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_task_list())
        search_entry = ttk.Entry(ctrl_frame, textvariable=self.search_var, width=18)
        search_entry.pack(side=tk.LEFT, padx=(0, 16))

        # Filter radio buttons
        ttk.Label(ctrl_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 4))
        self.filter_var = tk.StringVar(value="All")
        for f_mode in ["All", "Pending", "Completed"]:
            r = ttk.Radiobutton(
                ctrl_frame,
                text=f_mode,
                value=f_mode,
                variable=self.filter_var,
                command=self.refresh_task_list
            )
            r.pack(side=tk.LEFT, padx=3)

        # Sort Dropdown
        self.sort_var = tk.StringVar(value="Default")
        sort_lbl = ttk.Label(ctrl_frame, text="Sort By:")
        sort_lbl.pack(side=tk.LEFT, padx=(16, 4))
        sort_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=self.sort_var,
            values=["Default", "Priority (High-Low)", "Due Date", "Title (A-Z)"],
            state="readonly",
            width=18
        )
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_task_list())

        # Tasks Table (Treeview)
        table_frame = ttk.Frame(self, padding=(16, 6))
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "title", "status", "priority", "due_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="#", anchor=tk.CENTER)
        self.tree.heading("title", text="Task Title", anchor=tk.W)
        self.tree.heading("status", text="Status", anchor=tk.CENTER)
        self.tree.heading("priority", text="Priority", anchor=tk.CENTER)
        self.tree.heading("due_date", text="Due Date", anchor=tk.CENTER)

        self.tree.column("id", width=45, minwidth=40, stretch=False, anchor=tk.CENTER)
        self.tree.column("title", width=340, minwidth=200, stretch=True)
        self.tree.column("status", width=110, minwidth=90, stretch=False, anchor=tk.CENTER)
        self.tree.column("priority", width=100, minwidth=80, stretch=False, anchor=tk.CENTER)
        self.tree.column("due_date", width=110, minwidth=90, stretch=False, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Double click to toggle status
        self.tree.bind("<Double-1>", lambda e: self.toggle_status())

        # Tag configurations for coloring
        self.tree.tag_configure("completed", foreground="#6c757d", background="#f8f9fa")
        self.tree.tag_configure("pending_high", foreground="#d90429")
        self.tree.tag_configure("pending_medium", foreground="#1d3557")
        self.tree.tag_configure("pending_low", foreground="#2b9348")

        # Action Buttons Toolbar
        btn_frame = ttk.Frame(self, padding=(16, 8))
        btn_frame.pack(fill=tk.X)

        toggle_btn = ttk.Button(btn_frame, text="✔ Toggle Status", command=self.toggle_status)
        toggle_btn.pack(side=tk.LEFT, padx=4)

        edit_btn = ttk.Button(btn_frame, text="✏ Edit Task", command=self.edit_task)
        edit_btn.pack(side=tk.LEFT, padx=4)

        del_btn = ttk.Button(btn_frame, text="🗑 Delete Task", command=self.delete_task)
        del_btn.pack(side=tk.LEFT, padx=4)

        reload_btn = ttk.Button(btn_frame, text="🔄 Reload", command=self.reload_from_disk)
        reload_btn.pack(side=tk.RIGHT, padx=4)

        # Status Bar
        self.status_bar = ttk.Label(
            self,
            text="",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(10, 4),
            font=("Segoe UI", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def refresh_task_list(self):
        """Filter, sort, and render tasks into the Treeview."""
        self.tree.delete(*self.tree.get_children())

        # Apply search keyword
        keyword = self.search_var.get().strip().lower()
        filtered = [
            (idx, t) for idx, t in enumerate(self.tasks)
            if not keyword or keyword in t["title"].lower()
        ]

        # Apply status filter
        f_val = self.filter_var.get()
        if f_val == "Pending":
            filtered = [item for item in filtered if not item[1]["completed"]]
        elif f_val == "Completed":
            filtered = [item for item in filtered if item[1]["completed"]]

        # Apply sorting
        s_val = self.sort_var.get()
        if s_val == "Priority (High-Low)":
            filtered.sort(key=lambda item: PRIORITY_ORDER.get(item[1]["priority"], 2))
        elif s_val == "Due Date":
            filtered.sort(key=lambda item: (not bool(item[1]["due_date"]), item[1]["due_date"]))
        elif s_val == "Title (A-Z)":
            filtered.sort(key=lambda item: item[1]["title"].lower())

        # Populate treeview
        for display_num, (orig_idx, task) in enumerate(filtered, start=1):
            status_text = "Completed" if task["completed"] else "Pending"
            due_text = task["due_date"] if task["due_date"] else "—"

            # Assign styling tag
            if task["completed"]:
                tag = "completed"
            elif task["priority"] == "High":
                tag = "pending_high"
            elif task["priority"] == "Medium":
                tag = "pending_medium"
            else:
                tag = "pending_low"

            self.tree.insert(
                "",
                tk.END,
                iid=str(orig_idx),
                values=(display_num, task["title"], status_text, task["priority"], due_text),
                tags=(tag,)
            )

        # Update status bar counts
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks if not t["completed"])
        completed = sum(1 for t in self.tasks if t["completed"])
        self.status_bar.config(
            text=f"Total: {total} tasks | ⏳ Pending: {pending} | ✅ Completed: {completed} | Stored in: {FILE_NAME.name}"
        )

    def add_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Validation Error", "Task name cannot be empty.")
            return

        priority = self.priority_var.get()
        due_date = self.due_entry.get().strip()
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format, or leave it blank.")
                return

        new_task = {
            "title": title,
            "completed": False,
            "priority": priority,
            "due_date": due_date
        }
        self.tasks.append(new_task)
        if save_tasks(self.tasks):
            self.title_entry.delete(0, tk.END)
            self.due_entry.delete(0, tk.END)
            self.priority_var.set("Medium")
            self.refresh_task_list()
        else:
            messagebox.showerror("Save Error", "Could not save the task to tasks.json.")

    def _get_selected_task_index(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a task from the list first.")
            return None
        return int(selected[0])

    def toggle_status(self):
        idx = self._get_selected_task_index()
        if idx is None:
            return

        self.tasks[idx]["completed"] = not self.tasks[idx]["completed"]
        save_tasks(self.tasks)
        self.refresh_task_list()

    def edit_task(self):
        idx = self._get_selected_task_index()
        if idx is None:
            return

        task = self.tasks[idx]

        # Edit dialog modal
        dialog = tk.Toplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("400x230")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Task Name:").pack(anchor=tk.W, padx=16, pady=(12, 2))
        t_var = tk.StringVar(value=task["title"])
        t_entry = ttk.Entry(dialog, textvariable=t_var, width=40)
        t_entry.pack(fill=tk.X, padx=16)

        ttk.Label(dialog, text="Priority:").pack(anchor=tk.W, padx=16, pady=(8, 2))
        p_var = tk.StringVar(value=task["priority"])
        p_combo = ttk.Combobox(dialog, textvariable=p_var, values=PRIORITIES, state="readonly")
        p_combo.pack(anchor=tk.W, padx=16)

        ttk.Label(dialog, text="Due Date (YYYY-MM-DD):").pack(anchor=tk.W, padx=16, pady=(8, 2))
        d_var = tk.StringVar(value=task["due_date"])
        d_entry = ttk.Entry(dialog, textvariable=d_var, width=20)
        d_entry.pack(anchor=tk.W, padx=16)

        def save_edit():
            new_title = t_var.get().strip()
            if not new_title:
                messagebox.showwarning("Validation Error", "Task name cannot be empty.", parent=dialog)
                return

            new_due = d_var.get().strip()
            if new_due:
                try:
                    datetime.strptime(new_due, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Invalid Date", "Date must be YYYY-MM-DD or empty.", parent=dialog)
                    return

            task["title"] = new_title
            task["priority"] = p_var.get()
            task["due_date"] = new_due

            save_tasks(self.tasks)
            self.refresh_task_list()
            dialog.destroy()

        btn_box = ttk.Frame(dialog)
        btn_box.pack(fill=tk.X, padx=16, pady=16)
        ttk.Button(btn_box, text="Save Changes", command=save_edit).pack(side=tk.RIGHT, padx=4)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def delete_task(self):
        idx = self._get_selected_task_index()
        if idx is None:
            return

        task = self.tasks[idx]
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete task:\n\n'{task['title']}'?"
        )
        if confirm:
            self.tasks.pop(idx)
            save_tasks(self.tasks)
            self.refresh_task_list()

    def reload_from_disk(self):
        self.tasks = load_tasks()
        self.refresh_task_list()
        messagebox.showinfo("Reloaded", "Tasks reloaded from tasks.json.")


def main():
    app = TodoAppGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
