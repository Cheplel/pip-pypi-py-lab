import argparse
from html import escape
from typing import List


# ==========================================
# 1. OOP CLASSES (The Business Logic)
# ==========================================
class Task:

    def __init__(self, description):
        self.description = description
        self.is_completed = False

    def mark_complete(self):
        self.is_completed = True

    def __str__(self):
        status = "✅" if self.is_completed else "❌"
        return f"[{status}] {self.description}"


class UserAccount:

    def __init__(self, username):
        self.username = username
        self.tasks = []

    def add_task(self, description):
        new_task = Task(description)
        self.tasks.append(new_task)
        print(f"Added task: '{description}' to user '{self.username}'.")

    def complete_task(self, task_index):
        try:
            self.tasks[task_index].mark_complete()
            print(
                f"Marked task #{task_index} as complete for '{self.username}'."
            )
        except IndexError:
            print(f"Error: Task index {task_index} does not exist.")

    def show_tasks(self):
        print(f"\n--- {self.username}'s To-Do List ---")
        if not self.tasks:
            print("No tasks found.")
        for idx, task in enumerate(self.tasks):
            print(f"{idx}: {task}")


# ==========================================
# 2. CLI SETUP (The Interface)
# ==========================================
def main():
    # Base parser
    parser = argparse.ArgumentParser(
        description="CLI Task Manager with OOP principles."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: add-task
    add_parser = subparsers.add_parser(
        "add-task", help="Add a new task to a user account"
    )
    add_parser.add_argument(
        "--user", required=True, help="The username of the account"
    )
    add_parser.add_argument(
        "--task", required=True, help="The description of the task"
    )

    # Subcommand: complete-task
    complete_parser = subparsers.add_parser(
        "complete-task", help="Mark a task as complete via its index"
    )
    complete_parser.add_argument(
        "--user", required=True, help="The username of the account"
    )
    complete_parser.add_argument(
        "--index",
        required=True,
        type=int,
        help="The numeric index of the task",
    )

    # Subcommand: export-tasks -> create interactive HTML file
    export_parser = subparsers.add_parser(
        "export-tasks", help="Export tasks to an interactive HTML file"
    )
    export_parser.add_argument(
        "--user", required=True, help="The username of the account"
    )
    export_parser.add_argument(
        "--out", required=False, default="tasks.html", help="Output HTML filename"
    )
    export_parser.add_argument(
        "--task",
        required=False,
        nargs="*",
        help="Optional task descriptions to include in the exported file",
    )

    # Subcommand: export-viewer -> write a runnable Python file that shows tasks (Tkinter)
    viewer_parser = subparsers.add_parser(
        "export-viewer", help="Export a runnable Python viewer that displays tasks"
    )
    viewer_parser.add_argument(
        "--user", required=True, help="The username of the account"
    )
    viewer_parser.add_argument(
        "--out", required=False, default="tasks_viewer.py", help="Output Python filename"
    )
    viewer_parser.add_argument(
        "--task",
        required=False,
        nargs="*",
        help="Optional task descriptions to include in the exported viewer",
    )

    # Parse args
    args = parser.parse_args()

    # Simulation setup
    # Note: In a real app, you would load/save this user data from a file or database.
    user = UserAccount(username=args.user)

    # Pre-populating a dummy task for testing 'complete-task' command easily
    if args.command == "complete-task":
        user.add_task("Sample baseline task")

    # Route arguments to correct OOP methods
    if args.command == "add-task":
        user.add_task(args.task)
        user.show_tasks()

    elif args.command == "complete-task":
        user.complete_task(args.index)
        user.show_tasks()

    elif args.command == "export-tasks":
        # If the caller passed explicit tasks to include use them, otherwise use current user's tasks
        provided = args.task if getattr(args, 'task', None) else []
        export_tasks(user, provided, args.out)
    elif args.command == "export-viewer":
        provided = args.task if getattr(args, 'task', None) else []
        export_viewer(user, provided, args.out)


def export_tasks(user: UserAccount, provided_tasks: List[str], out_filename: str = "tasks.html") -> str:
        """Generate a simple interactive HTML file showing tasks for `user`.

        - If `provided_tasks` is non-empty, use those descriptions instead of the user's current tasks.
        - The generated HTML is client-side only; it allows clicking checkboxes to toggle visual state.
        """
        task_texts = provided_tasks if provided_tasks else [t.description for t in user.tasks]

        items = []
        for i, txt in enumerate(task_texts):
                safe = escape(txt)
                items.append(f'<li><label><input type="checkbox" data-idx="{i}"> {safe}</label></li>')

        html_doc = f"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width,initial-scale=1" />
            <title>Tasks for {escape(user.username)}</title>
            <style>
                body {{ font-family: Segoe UI, Arial, sans-serif; max-width: 780px; margin: 24px; }}
                li {{ margin: 8px 0; }}
            </style>
        </head>
        <body>
            <h1>Tasks for {escape(user.username)}</h1>
            <ul>
                {''.join(items)}
            </ul>
            <p><em>Click checkboxes to mark complete (UI-only).</em></p>
            <script>
                document.querySelectorAll('input[type="checkbox"]').forEach(cb => {{
                    cb.addEventListener('change', e => {{
                        const lbl = e.target.parentElement;
                        lbl.style.textDecoration = e.target.checked ? 'line-through' : '';
                    }});
                }});
            </script>
        </body>
        </html>
        """

        with open(out_filename, 'w', encoding='utf-8') as f:
                f.write(html_doc)

        print(f"Exported tasks to {out_filename}")
        return out_filename


def export_viewer(user: UserAccount, provided_tasks: List[str], out_filename: str = "tasks_viewer.py") -> str:
    """Write a runnable Python file (`out_filename`) that launches a Tkinter GUI showing tasks.

    The generated file is a self-contained Python script that, when executed, displays clickable
    checkboxes for each task. This file is created in the project only when `export-viewer` runs.
    """
    # Prepare tasks to embed
    tasks = provided_tasks if provided_tasks else [t.description for t in user.tasks]

    # Create a Python script content that builds a Tkinter GUI
    safe_tasks_repr = repr(tasks)
    viewer_code = f'''"""Auto-generated tasks viewer for user: {escape(user.username)}"""
import tkinter as tk
from tkinter import ttk, messagebox

TASKS = {safe_tasks_repr}

def main():
    root = tk.Tk()
    root.title('Tasks Viewer - {escape(user.username)}')
    frm = ttk.Frame(root, padding=12)
    frm.pack(fill='both', expand=True)

    lbl = ttk.Label(frm, text='Tasks for {escape(user.username)}', font=('Segoe UI', 14, 'bold'))
    lbl.pack(anchor='w')

    checks = []
    for t in TASKS:
        var = tk.BooleanVar(value=False)
        cb = ttk.Checkbutton(frm, text=t, variable=var)
        cb.pack(anchor='w', pady=2)
        checks.append((t, var))

    def on_save():
        completed = [t for t, v in checks if v.get()]
        messagebox.showinfo('Saved', f'Completed: {{len(completed)}} task(s)')

    btn = ttk.Button(frm, text='Save (UI-only)', command=on_save)
    btn.pack(pady=8)

    root.mainloop()

if __name__ == '__main__':
    main()
'''

    with open(out_filename, 'w', encoding='utf-8') as f:
        f.write(viewer_code)

    print(f"Exported runnable viewer to {out_filename}")
    return out_filename


if __name__ == "__main__":
    main()