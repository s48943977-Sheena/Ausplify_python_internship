"""
calculator_gui.py
=================
Task 3: Modern Desktop GUI Calculator Application
Auspify Technologies — Python Development Internship

A production-quality graphical calculator developed in Python with Tkinter.
Features:
- Pure Python Standard Library (Tkinter) with zero external dependencies.
- AST-based safe evaluation engine (no dangerous eval()).
- Full arithmetic operations: +, -, *, /, %, ^ (power), √ (square root), parentheses.
- Sign toggle (±), Backspace (DEL), and Clear (C).
- Slide-out / interactive Calculation History drawer with 1-click re-insertion.
- One-click copy-to-clipboard functionality with feedback banner.
- Full keyboard integration (0-9, operators, Enter, Backspace, Esc, Ctrl+C).
- High-contrast, polished modern dark aesthetic with responsive hover transitions.
"""

import math
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

try:
    from calculator_core import (
        CalculationHistory,
        InvalidExpressionError,
        format_result,
        safe_evaluate,
    )
except ImportError:
    from .calculator_core import (
        CalculationHistory,
        InvalidExpressionError,
        format_result,
        safe_evaluate,
    )

# ---------- Palette & Styling Constants ----------
THEME = {
    "bg_root": "#0B1120",        # Very dark navy root
    "bg_card": "#1E293B",        # Card / panel slate
    "bg_display": "#0F172A",     # Ultra-dark display well
    "border_display": "#334155", # Display border stroke
    "fg_primary": "#F8FAFC",     # Bright white primary text
    "fg_secondary": "#94A3B8",   # Muted slate secondary text
    "fg_accent": "#38BDF8",      # Light sky blue accent
    # Keypad Colors
    "btn_num_bg": "#1E293B",     # Number buttons
    "btn_num_hover": "#334155",
    "btn_num_fg": "#F8FAFC",
    "btn_op_bg": "#6366F1",      # Basic operators (+, -, *, /)
    "btn_op_hover": "#4F46E5",
    "btn_op_fg": "#FFFFFF",
    "btn_fn_bg": "#0284C7",      # Scientific / functions (^, %, √)
    "btn_fn_hover": "#0369A1",
    "btn_fn_fg": "#FFFFFF",
    "btn_clear_bg": "#EF4444",   # Clear (C)
    "btn_clear_hover": "#DC2626",
    "btn_clear_fg": "#FFFFFF",
    "btn_del_bg": "#F59E0B",     # Backspace (DEL)
    "btn_del_hover": "#D97706",
    "btn_del_fg": "#FFFFFF",
    "btn_eq_bg": "#10B981",      # Equals (=)
    "btn_eq_hover": "#059669",
    "btn_eq_fg": "#FFFFFF",
    "btn_paren_bg": "#334155",   # Parentheses & ±
    "btn_paren_hover": "#475569",
    "btn_paren_fg": "#E2E8F0",
}


class CalculatorApp:
    """Main desktop GUI calculator application built with Tkinter."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Auspify Calculator Pro")
        self.root.geometry("420x680")
        self.root.minsize(390, 640)
        self.root.configure(bg=THEME["bg_root"])

        # History and State
        self.history_mgr = CalculationHistory(max_items=30)
        self.expression: str = ""
        self.just_calculated: bool = False
        self.error_active: bool = False
        self.history_drawer_open: bool = False

        self._center_window()
        self._build_ui()
        self._bind_keyboard_events()

    def _center_window(self):
        """Center window on screen during initialization."""
        self.root.update_idletasks()
        width = 420
        height = 680
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        pos_x = max(0, (screen_w - width) // 2)
        pos_y = max(0, (screen_h - height) // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def _build_ui(self):
        """Construct the visual hierarchy."""
        # Top Header Bar
        header = tk.Frame(self.root, bg=THEME["bg_root"])
        header.pack(fill="x", padx=16, pady=(14, 8))

        brand_frame = tk.Frame(header, bg=THEME["bg_root"])
        brand_frame.pack(side="left")

        tk.Label(
            brand_frame,
            text="AUSPIFY CALCULATOR",
            font=("Segoe UI", 13, "bold"),
            bg=THEME["bg_root"],
            fg=THEME["fg_accent"],
        ).pack(anchor="w")

        tk.Label(
            brand_frame,
            text="Task 3 • Python GUI",
            font=("Segoe UI", 9),
            bg=THEME["bg_root"],
            fg=THEME["fg_secondary"],
        ).pack(anchor="w")

        # Top Action Buttons (History & Copy)
        action_bar = tk.Frame(header, bg=THEME["bg_root"])
        action_bar.pack(side="right")

        self.btn_copy = tk.Button(
            action_bar,
            text="📋 Copy",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["fg_secondary"],
            activebackground=THEME["btn_paren_hover"],
            activeforeground=THEME["fg_primary"],
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.copy_to_clipboard,
        )
        self.btn_copy.pack(side="left", padx=(0, 6))

        self.btn_history = tk.Button(
            action_bar,
            text="🕒 History",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["fg_secondary"],
            activebackground=THEME["btn_paren_hover"],
            activeforeground=THEME["fg_primary"],
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.toggle_history_drawer,
        )
        self.btn_history.pack(side="left")

        # Main Container (Holds Display & Keypad OR History)
        self.main_container = tk.Frame(self.root, bg=THEME["bg_root"])
        self.main_container.pack(fill="both", expand=True, padx=14, pady=4)

        # Calculator View Frame
        self.calc_frame = tk.Frame(self.main_container, bg=THEME["bg_root"])
        self.calc_frame.pack(fill="both", expand=True)

        # Display Card
        display_panel = tk.Frame(
            self.calc_frame,
            bg=THEME["bg_display"],
            highlightbackground=THEME["border_display"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        display_panel.pack(fill="x", pady=(4, 10))

        # Secondary (History / Active Expression) Display
        self.lbl_history = tk.Label(
            display_panel,
            text="Ready to calculate",
            font=("Segoe UI", 11),
            anchor="e",
            bg=THEME["bg_display"],
            fg=THEME["fg_secondary"],
        )
        self.lbl_history.pack(fill="x", pady=(0, 4))

        # Primary Numeric Display
        self.lbl_display = tk.Label(
            display_panel,
            text="0",
            font=("Segoe UI", 32, "bold"),
            anchor="e",
            bg=THEME["bg_display"],
            fg=THEME["fg_primary"],
        )
        self.lbl_display.pack(fill="x", pady=(2, 4))

        # Status / Feedback Toast inside Display Panel
        self.lbl_toast = tk.Label(
            display_panel,
            text="",
            font=("Segoe UI", 9, "bold"),
            anchor="e",
            bg=THEME["bg_display"],
            fg=THEME["fg_accent"],
        )
        self.lbl_toast.pack(fill="x")

        # Keypad Grid Frame
        self.keypad_frame = tk.Frame(self.calc_frame, bg=THEME["bg_root"])
        self.keypad_frame.pack(fill="both", expand=True, pady=(2, 6))

        self._build_keypad()

        # History View Frame (Hidden by default)
        self.history_frame = tk.Frame(self.main_container, bg=THEME["bg_root"])

        self._build_history_view()

        # Footer Info
        footer = tk.Frame(self.root, bg=THEME["bg_root"])
        footer.pack(fill="x", pady=(2, 10))
        tk.Label(
            footer,
            text="Auspify Python Internship • Task 3: GUI Calculator",
            font=("Segoe UI", 8),
            bg=THEME["bg_root"],
            fg=THEME["fg_secondary"],
        ).pack()

    def _build_keypad(self):
        """Construct the 6-row mathematical button grid."""
        layout = [
            # Row 0: Clear & Parentheses & Advanced
            [
                ("C", THEME["btn_clear_bg"], THEME["btn_clear_hover"], THEME["btn_clear_fg"]),
                ("DEL", THEME["btn_del_bg"], THEME["btn_del_hover"], THEME["btn_del_fg"]),
                ("(", THEME["btn_paren_bg"], THEME["btn_paren_hover"], THEME["btn_paren_fg"]),
                (")", THEME["btn_paren_bg"], THEME["btn_paren_hover"], THEME["btn_paren_fg"]),
            ],
            # Row 1: Scientific / Functions
            [
                ("√", THEME["btn_fn_bg"], THEME["btn_fn_hover"], THEME["btn_fn_fg"]),
                ("^", THEME["btn_fn_bg"], THEME["btn_fn_hover"], THEME["btn_fn_fg"]),
                ("%", THEME["btn_fn_bg"], THEME["btn_fn_hover"], THEME["btn_fn_fg"]),
                ("÷", THEME["btn_op_bg"], THEME["btn_op_hover"], THEME["btn_op_fg"]),
            ],
            # Row 2: 7, 8, 9, *
            [
                ("7", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("8", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("9", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("×", THEME["btn_op_bg"], THEME["btn_op_hover"], THEME["btn_op_fg"]),
            ],
            # Row 3: 4, 5, 6, -
            [
                ("4", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("5", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("6", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("−", THEME["btn_op_bg"], THEME["btn_op_hover"], THEME["btn_op_fg"]),
            ],
            # Row 4: 1, 2, 3, +
            [
                ("1", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("2", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("3", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("+", THEME["btn_op_bg"], THEME["btn_op_hover"], THEME["btn_op_fg"]),
            ],
            # Row 5: ±, 0, ., =
            [
                ("±", THEME["btn_paren_bg"], THEME["btn_paren_hover"], THEME["btn_paren_fg"]),
                ("0", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                (".", THEME["btn_num_bg"], THEME["btn_num_hover"], THEME["btn_num_fg"]),
                ("=", THEME["btn_eq_bg"], THEME["btn_eq_hover"], THEME["btn_eq_fg"]),
            ],
        ]

        # Configure rows & columns to expand equally
        for r in range(len(layout)):
            self.keypad_frame.rowconfigure(r, weight=1)
        for c in range(4):
            self.keypad_frame.columnconfigure(c, weight=1)

        for r, row in enumerate(layout):
            for c, (text, bg, hover, fg) in enumerate(row):
                btn = tk.Button(
                    self.keypad_frame,
                    text=text,
                    font=("Segoe UI", 15, "bold"),
                    bg=bg,
                    fg=fg,
                    activebackground=hover,
                    activeforeground=fg,
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                    command=lambda val=text: self.on_button_click(val),
                )
                btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3, ipady=4)

                # Hover transitions
                btn.bind("<Enter>", lambda e, b=btn, h=hover: b.configure(bg=h))
                btn.bind("<Leave>", lambda e, b=btn, normal=bg: b.configure(bg=normal))

    def _build_history_view(self):
        """Construct the calculation history drawer."""
        top_bar = tk.Frame(self.history_frame, bg=THEME["bg_card"], padx=10, pady=8)
        top_bar.pack(fill="x", pady=(0, 6))

        tk.Label(
            top_bar,
            text="Calculation History",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["fg_primary"],
        ).pack(side="left")

        tk.Button(
            top_bar,
            text="Clear",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["btn_clear_bg"],
            fg=THEME["fg_primary"],
            activebackground=THEME["btn_clear_hover"],
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.clear_history,
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            top_bar,
            text="Back to Calculator",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["btn_fn_bg"],
            fg=THEME["fg_primary"],
            activebackground=THEME["btn_fn_hover"],
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.toggle_history_drawer,
        ).pack(side="right")

        # History list with scrollbar
        list_container = tk.Frame(self.history_frame, bg=THEME["bg_display"])
        list_container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(
            list_container,
            bg=THEME["bg_display"],
            fg=THEME["fg_primary"],
            font=("Segoe UI", 11),
            selectbackground=THEME["btn_op_bg"],
            selectforeground=THEME["fg_primary"],
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self.history_listbox.pack(fill="both", expand=True, padx=6, pady=6)
        scrollbar.config(command=self.history_listbox.yview)

        self.history_listbox.bind("<Double-Button-1>", self.on_history_item_selected)

        hint_lbl = tk.Label(
            self.history_frame,
            text="💡 Double-click any record to load its result back into calculator",
            font=("Segoe UI", 8, "italic"),
            bg=THEME["bg_root"],
            fg=THEME["fg_secondary"],
            pady=6,
        )
        hint_lbl.pack()

    def _bind_keyboard_events(self):
        """Bind physical keyboard input for fast typing."""
        self.root.bind("<Key>", self.handle_key_event)
        self.root.bind("<Control-c>", lambda e: self.copy_to_clipboard())
        self.root.bind("<Control-C>", lambda e: self.copy_to_clipboard())

    def show_toast(self, message: str, duration_ms: int = 1500):
        """Flash a subtle status banner inside the display card."""
        self.lbl_toast.config(text=message)
        self.root.after(duration_ms, lambda: self.lbl_toast.config(text=""))

    def toggle_history_drawer(self):
        """Toggle between calculator keypad view and history list view."""
        if self.history_drawer_open:
            self.history_frame.pack_forget()
            self.calc_frame.pack(fill="both", expand=True)
            self.history_drawer_open = False
            self.btn_history.config(text="🕒 History", bg=THEME["bg_card"])
        else:
            self.calc_frame.pack_forget()
            self._refresh_history_listbox()
            self.history_frame.pack(fill="both", expand=True)
            self.history_drawer_open = True
            self.btn_history.config(text="✖ Close", bg=THEME["btn_del_bg"])

    def _refresh_history_listbox(self):
        """Populate listbox with current history records."""
        self.history_listbox.delete(0, tk.END)
        records = self.history_mgr.get_all()
        if not records:
            self.history_listbox.insert(tk.END, "  (No calculation history yet)")
            return

        for idx, rec in enumerate(reversed(records), 1):
            line = f"{rec['expression']}  =  {rec['result']}"
            self.history_listbox.insert(tk.END, f"{idx}. {line}")

    def on_history_item_selected(self, event):
        """Load selected history result into calculator display."""
        selection = self.history_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        records = list(reversed(self.history_mgr.get_all()))
        if index < len(records):
            chosen = records[index]
            self.expression = chosen["result"]
            self.lbl_display.config(text=self.expression)
            self.lbl_history.config(text=f"Loaded from history: {chosen['expression']}")
            self.just_calculated = True
            self.error_active = False
            self.toggle_history_drawer()
            self.show_toast("✓ Loaded from history")

    def clear_history(self):
        """Erase all history records."""
        self.history_mgr.clear()
        self._refresh_history_listbox()
        self.show_toast("History cleared")

    def copy_to_clipboard(self):
        """Copy current displayed value to system clipboard."""
        val = self.lbl_display.cget("text")
        if val and val != "Error":
            self.root.clipboard_clear()
            self.root.clipboard_append(val)
            self.show_toast("✓ Copied to clipboard!")

    def on_button_click(self, label: str):
        """Process click actions from UI buttons."""
        # 1. Clear (C)
        if label == "C":
            self.expression = ""
            self.just_calculated = False
            self.error_active = False
            self.lbl_display.config(text="0")
            self.lbl_history.config(text="Ready to calculate")
            return

        # 2. Backspace (DEL)
        if label == "DEL":
            if self.error_active or self.just_calculated:
                self.expression = ""
                self.error_active = False
                self.just_calculated = False
            else:
                self.expression = self.expression[:-1]

            display_val = self.expression if self.expression else "0"
            self.lbl_display.config(text=display_val)
            return

        # 3. Sign Toggle (±)
        if label == "±":
            if self.error_active:
                return
            if not self.expression or self.expression == "0":
                self.expression = "-"
            elif self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression
            self.lbl_display.config(text=self.expression or "0")
            return

        # 4. Square Root (√)
        if label == "√":
            if self.error_active:
                self.expression = ""
                self.error_active = False
            if self.just_calculated:
                self.expression = f"√({self.expression})"
                self.just_calculated = False
            else:
                self.expression += "√("
            self.lbl_display.config(text=self.expression)
            return

        # 5. Calculate (=)
        if label == "=":
            self.evaluate_current_expression()
            return

        # 6. Normal input characters
        char_map = {
            "×": "*",
            "÷": "/",
            "−": "-",
            "+": "+",
            "^": "^",
            "%": "%",
            ".": ".",
            "(": "(",
            ")": ")",
        }
        val_to_insert = char_map.get(label, label)

        if self.error_active:
            self.expression = ""
            self.error_active = False

        # If previous action was calculation:
        if self.just_calculated:
            # Continuing with an operator keeps previous answer
            if val_to_insert in "+-*/^%":
                self.just_calculated = False
            else:
                # Entering a new number starts a new expression
                self.expression = ""
                self.just_calculated = False

        if self.expression == "0" and val_to_insert not in ".+-*/^%()":
            self.expression = ""

        self.expression += val_to_insert
        self.lbl_display.config(text=self.expression)

    def evaluate_current_expression(self):
        """Execute calculation through the safe AST evaluator."""
        if not self.expression.strip() or self.error_active:
            return

        raw_input = self.expression

        try:
            numeric_ans = safe_evaluate(raw_input)
            formatted_ans = format_result(numeric_ans)

            # Record in history
            self.history_mgr.add_entry(raw_input, formatted_ans)

            # Update display
            self.lbl_history.config(text=f"{raw_input} =")
            self.lbl_display.config(text=formatted_ans)
            self.expression = formatted_ans
            self.just_calculated = True
            self.error_active = False

        except ZeroDivisionError as zde:
            self.lbl_history.config(text="Cannot divide by zero")
            self.lbl_display.config(text="Error")
            self.expression = ""
            self.error_active = True
            self.just_calculated = False

        except OverflowError:
            self.lbl_history.config(text="Number exceeded limits")
            self.lbl_display.config(text="Overflow")
            self.expression = ""
            self.error_active = True
            self.just_calculated = False

        except (InvalidExpressionError, Exception):
            self.lbl_history.config(text="Invalid expression syntax")
            self.lbl_display.config(text="Error")
            self.expression = ""
            self.error_active = True
            self.just_calculated = False

    def handle_key_event(self, event):
        """Map keyboard keys to calculator inputs."""
        char = event.char
        keysym = event.keysym

        # If history drawer is open, let Escape or Return toggle it
        if self.history_drawer_open:
            if keysym in ("Escape", "Return"):
                self.toggle_history_drawer()
            return

        if char in "0123456789.+-*/^%()":
            self.on_button_click(char)
        elif char.lower() == "r" or char.lower() == "s":
            self.on_button_click("√")
        elif keysym in ("Return", "KP_Enter"):
            self.on_button_click("=")
        elif keysym == "BackSpace":
            self.on_button_click("DEL")
        elif keysym == "Escape":
            self.on_button_click("C")


def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
