
import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox


APP_TITLE = "Smart Password Generator Pro"
AMBIGUOUS_CHARACTERS = "O0Il1"
MAX_PASSWORD_LENGTH = 128
MAX_BULK_COUNT = 100


# -------------------- PASSWORD ENGINE --------------------

class PasswordGenerator:
    """Generate passwords using Python's cryptographically secure RNG."""

    @staticmethod
    def generate(
        length=16,
        uppercase=True,
        lowercase=True,
        numbers=True,
        symbols=True,
        exclude_ambiguous=False
    ):
        pools = []

        if uppercase:
            pools.append(string.ascii_uppercase)
        if lowercase:
            pools.append(string.ascii_lowercase)
        if numbers:
            pools.append(string.digits)
        if symbols:
            pools.append(string.punctuation)

        if exclude_ambiguous:
            pools = [
                "".join(
                    char for char in pool
                    if char not in AMBIGUOUS_CHARACTERS
                )
                for pool in pools
            ]

        pools = [pool for pool in pools if pool]

        if not pools:
            raise ValueError(
                "Select at least one character type."
            )

        if not 1 <= length <= MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"Length must be between 1 and {MAX_PASSWORD_LENGTH}."
            )

        if length < len(pools):
            raise ValueError(
                "Length is too short for the selected character types."
            )

        # Guarantee at least one character from each selected group.
        characters = [
            secrets.choice(pool) for pool in pools
        ]

        all_characters = "".join(pools)

        characters.extend(
            secrets.choice(all_characters)
            for _ in range(length - len(characters))
        )

        secrets.SystemRandom().shuffle(characters)
        return "".join(characters)

    @classmethod
    def generate_many(cls, count, **settings):
        """Generate unique passwords within a requested batch."""

        if not 1 <= count <= MAX_BULK_COUNT:
            raise ValueError(
                f"Count must be between 1 and {MAX_BULK_COUNT}."
            )

        passwords = set()

        while len(passwords) < count:
            passwords.add(cls.generate(**settings))

        return list(passwords)


# -------------------- SECURITY ANALYZER --------------------

class PasswordAnalyzer:
    """Provide a simple educational password assessment."""

    COMMON_PASSWORDS = {
        "password", "password123", "12345678",
        "qwerty123", "admin123", "letmein",
        "welcome123", "iloveyou"
    }

    @classmethod
    def analyze(cls, password):
        if not password:
            return {
                "rating": "No password entered",
                "score": 0,
                "feedback": ["Enter a password to analyze."]
            }

        score = 0
        feedback = []

        # Length
        if len(password) >= 16:
            score += 2
        elif len(password) >= 12:
            score += 1
        else:
            feedback.append(
                "Use at least 12 characters; 16 or more is preferable."
            )

        # Character variety
        groups = [
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(c in string.punctuation for c in password)
        ]
        variety = sum(groups)

        score += min(variety, 4)

        if variety < 3:
            feedback.append(
                "Consider using more character types."
            )

        # Repetition
        if len(set(password)) < len(password) * 0.5:
            score -= 1
            feedback.append(
                "Many characters repeat; consider a less repetitive password."
            )

        # Simple sequences and common patterns
        lowered = password.lower()

        if lowered in cls.COMMON_PASSWORDS:
            score = 0
            feedback.append(
                "This matches a commonly used password pattern."
            )

        if any(
            sequence in lowered
            for sequence in (
                "123456", "abcdef", "qwerty", "111111"
            )
        ):
            score -= 2
            feedback.append(
                "Avoid predictable sequences and keyboard patterns."
            )

        score = max(0, min(score, 6))

        if score >= 5:
            rating = "Strong (estimated)"
        elif score >= 3:
            rating = "Moderate (estimated)"
        else:
            rating = "Weak (estimated)"

        if not feedback:
            feedback.append(
                "No obvious issues detected by these basic checks."
            )

        return {
            "rating": rating,
            "score": score,
            "feedback": feedback
        }


# -------------------- DESKTOP APPLICATION --------------------

class PasswordApp:
    """Tkinter GUI for password generation and analysis."""

    PROFILES = {
        "Strong Password": {
            "length": 20,
            "uppercase": True,
            "lowercase": True,
            "numbers": True,
            "symbols": True,
            "exclude_ambiguous": False
        },
        "Website": {
            "length": 16,
            "uppercase": True,
            "lowercase": True,
            "numbers": True,
            "symbols": True,
            "exclude_ambiguous": False
        },
        "Wi-Fi": {
            "length": 20,
            "uppercase": True,
            "lowercase": True,
            "numbers": True,
            "symbols": False,
            "exclude_ambiguous": True
        },
        "Numeric PIN": {
            "length": 8,
            "uppercase": False,
            "lowercase": False,
            "numbers": True,
            "symbols": False,
            "exclude_ambiguous": False
        }
    }

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("760x690")
        self.root.minsize(650, 600)

        self.profile_var = tk.StringVar(
            value="Strong Password"
        )
        self.length_var = tk.IntVar(value=20)
        self.count_var = tk.IntVar(value=5)

        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.number_var = tk.BooleanVar(value=True)
        self.symbol_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)

        self.generated_passwords = []

        self.build_interface()
        self.apply_profile()

    def build_interface(self):
        main = ttk.Frame(self.root, padding=14)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text=APP_TITLE,
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(
            main,
            text="Generate passwords and inspect basic security indicators."
        ).pack(anchor="w", pady=(0, 12))

        notebook = ttk.Notebook(main)
        notebook.pack(fill="both", expand=True)

        self.generator_tab = ttk.Frame(notebook, padding=14)
        self.analyzer_tab = ttk.Frame(notebook, padding=14)

        notebook.add(self.generator_tab, text="Generator")
        notebook.add(self.analyzer_tab, text="Security Analyzer")

        self.build_generator_tab()
        self.build_analyzer_tab()

    def build_generator_tab(self):
        tab = self.generator_tab

        profile_row = ttk.Frame(tab)
        profile_row.pack(fill="x", pady=5)

        ttk.Label(
            profile_row, text="Profile:"
        ).pack(side="left")

        profile_box = ttk.Combobox(
            profile_row,
            textvariable=self.profile_var,
            values=list(self.PROFILES.keys()),
            state="readonly",
            width=24
        )
        profile_box.pack(side="left", padx=8)
        profile_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.apply_profile()
        )

        length_row = ttk.Frame(tab)
        length_row.pack(fill="x", pady=8)

        ttk.Label(
            length_row, text="Password length:"
        ).pack(side="left")

        ttk.Spinbox(
            length_row,
            from_=1,
            to=MAX_PASSWORD_LENGTH,
            textvariable=self.length_var,
            width=8
        ).pack(side="left", padx=8)

        ttk.Label(
            length_row, text="Number to generate:"
        ).pack(side="left", padx=(16, 0))

        ttk.Spinbox(
            length_row,
            from_=1,
            to=MAX_BULK_COUNT,
            textvariable=self.count_var,
            width=8
        ).pack(side="left", padx=8)

        options = ttk.LabelFrame(
            tab, text="Character options", padding=10
        )
        options.pack(fill="x", pady=8)

        ttk.Checkbutton(
            options, text="Uppercase (A-Z)",
            variable=self.upper_var
        ).grid(row=0, column=0, sticky="w", padx=5, pady=4)

        ttk.Checkbutton(
            options, text="Lowercase (a-z)",
            variable=self.lower_var
        ).grid(row=0, column=1, sticky="w", padx=5, pady=4)

        ttk.Checkbutton(
            options, text="Numbers (0-9)",
            variable=self.number_var
        ).grid(row=1, column=0, sticky="w", padx=5, pady=4)

        ttk.Checkbutton(
            options, text="Symbols (!@#...)",
            variable=self.symbol_var
        ).grid(row=1, column=1, sticky="w", padx=5, pady=4)

        ttk.Checkbutton(
            options,
            text="Exclude confusing characters (O, 0, I, l, 1)",
            variable=self.ambiguous_var
        ).grid(
            row=2, column=0, columnspan=2,
            sticky="w", padx=5, pady=4
        )

        ttk.Button(
            tab,
            text="Generate Passwords",
            command=self.generate_passwords
        ).pack(fill="x", pady=(8, 10))

        ttk.Label(
            tab, text="Generated passwords (select one to copy):"
        ).pack(anchor="w")

        list_frame = ttk.Frame(tab)
        list_frame.pack(fill="both", expand=True, pady=5)

        self.password_list = tk.Listbox(
            list_frame,
            height=8,
            font=("Consolas", 11),
            selectmode=tk.SINGLE,
            exportselection=False
        )
        self.password_list.pack(
            side="left", fill="both", expand=True
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.password_list.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.password_list.config(
            yscrollcommand=scrollbar.set
        )

        button_row = ttk.Frame(tab)
        button_row.pack(fill="x", pady=5)

        ttk.Button(
            button_row,
            text="Copy Selected",
            command=self.copy_selected
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            button_row,
            text="Clear Results",
            command=self.clear_results
        ).pack(side="left")

        ttk.Label(
            tab,
            text="Passwords stay in this window unless you copy them. "
                 "Avoid sharing or saving real passwords in plain text.",
            wraplength=650
        ).pack(anchor="w", pady=(8, 0))

    def build_analyzer_tab(self):
        tab = self.analyzer_tab

        ttk.Label(
            tab,
            text="Enter a password to check basic security indicators."
        ).pack(anchor="w", pady=(0, 8))

        self.analysis_input = ttk.Entry(
            tab, show="*", font=("Consolas", 12)
        )
        self.analysis_input.pack(fill="x", pady=5)

        self.show_password_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            tab,
            text="Show password while typing",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        ).pack(anchor="w", pady=4)

        ttk.Button(
            tab,
            text="Analyze Password",
            command=self.analyze_password
        ).pack(fill="x", pady=10)

        self.analysis_result = ttk.Label(
            tab,
            text="Your result will appear here.",
            font=("Segoe UI", 13, "bold")
        )
        self.analysis_result.pack(anchor="w", pady=8)

        ttk.Label(
            tab, text="Suggestions:"
        ).pack(anchor="w")

        self.feedback_box = tk.Text(
            tab,
            height=10,
            wrap="word",
            state="disabled"
        )
        self.feedback_box.pack(
            fill="both", expand=True, pady=5
        )

        ttk.Label(
            tab,
            text=(
                "This analyzer uses simple heuristics. It does not "
                "check leaked-password databases and cannot guarantee "
                "that a password is secure. Analysis happens locally."
            ),
            wraplength=650
        ).pack(anchor="w", pady=(6, 0))

    def apply_profile(self):
        profile = self.PROFILES[self.profile_var.get()]

        self.length_var.set(profile["length"])
        self.upper_var.set(profile["uppercase"])
        self.lower_var.set(profile["lowercase"])
        self.number_var.set(profile["numbers"])
        self.symbol_var.set(profile["symbols"])
        self.ambiguous_var.set(profile["exclude_ambiguous"])

    def read_settings(self):
        try:
            length = int(self.length_var.get())
            count = int(self.count_var.get())
        except (ValueError, tk.TclError):
            raise ValueError(
                "Length and count must be whole numbers."
            )

        if not 1 <= length <= MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"Length must be between 1 and {MAX_PASSWORD_LENGTH}."
            )

        if not 1 <= count <= MAX_BULK_COUNT:
            raise ValueError(
                f"Count must be between 1 and {MAX_BULK_COUNT}."
            )

        return {
            "length": length,
            "count": count,
            "uppercase": self.upper_var.get(),
            "lowercase": self.lower_var.get(),
            "numbers": self.number_var.get(),
            "symbols": self.symbol_var.get(),
            "exclude_ambiguous": self.ambiguous_var.get()
        }

    def generate_passwords(self):
        try:
            settings = self.read_settings()
            count = settings.pop("count")

            passwords = PasswordGenerator.generate_many(
                count, **settings
            )

            self.generated_passwords = passwords
            self.password_list.delete(0, tk.END)

            for password in passwords:
                self.password_list.insert(tk.END, password)

        except ValueError as error:
            messagebox.showerror(
                "Invalid Settings", str(error)
            )

    def copy_selected(self):
        selection = self.password_list.curselection()

        if not selection:
            messagebox.showinfo(
                "Select a Password",
                "Select a password from the list first."
            )
            return

        password = self.password_list.get(selection[0])

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()

            messagebox.showinfo(
                "Copied", "Selected password copied to clipboard."
            )
        except tk.TclError:
            messagebox.showerror(
                "Clipboard Error",
                "Could not copy the password."
            )

    def clear_results(self):
        self.generated_passwords.clear()
        self.password_list.delete(0, tk.END)

    def toggle_password_visibility(self):
        self.analysis_input.config(
            show="" if self.show_password_var.get() else "*"
        )

    def analyze_password(self):
        password = self.analysis_input.get()

        if not password:
            messagebox.showwarning(
                "Missing Password",
                "Enter a password to analyze."
            )
            return

        result = PasswordAnalyzer.analyze(password)

        self.analysis_result.config(
            text=f"{result['rating']} — Score: "
                 f"{result['score']}/6"
        )

        self.feedback_box.config(state="normal")
        self.feedback_box.delete("1.0", tk.END)

        for suggestion in result["feedback"]:
            self.feedback_box.insert(
                tk.END, f"• {suggestion}\n\n"
            )

        self.feedback_box.config(state="disabled")


def main():
    root = tk.Tk()
    PasswordApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
