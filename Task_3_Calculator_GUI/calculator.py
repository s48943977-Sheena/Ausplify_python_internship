"""
calculator.py
=============
Task 3: Calculator (Command-Line & Desktop Interface)
Auspify Technologies -- Python Development Internship

An interactive mathematical calculator for the terminal with full arithmetic,
power, modulo, square root, parentheses, and history logging capabilities.
Includes support for launching the desktop GUI version via '--gui'.
"""

import argparse
import sys
from typing import Optional

try:
    from calculator_core import (
        CalculationHistory,
        CalculationError,
        InvalidExpressionError,
        format_result,
        safe_evaluate,
    )
except ImportError:
    from .calculator_core import (
        CalculationHistory,
        CalculationError,
        InvalidExpressionError,
        format_result,
        safe_evaluate,
    )


def print_banner():
    """Print styled terminal banner."""
    print("=" * 50)
    print("      AUSPIFY TECHNOLOGIES -- PYTHON INTERNSHIP    ")
    print("          Task 3: Modern Calculator (CLI)         ")
    print("=" * 50)
    print("Supported operations:")
    print("  * Basic:    + (Add), - (Sub), * (Mult), / (Div)")
    print("  * Advanced: ^ (Power), % (Modulo), sqrt(x)")
    print("  * Grouping: ( ... ) Parentheses with PEMDAS")
    print("Special Commands:")
    print("  * 'history'  -- View recent calculations")
    print("  * 'clear'    -- Clear calculation history")
    print("  * 'gui'      -- Launch Tkinter Desktop GUI")
    print("  * 'quit'/'q' -- Exit application")
    print("-" * 50)


def launch_gui():
    """Launch the Tkinter Desktop GUI interface."""
    try:
        import calculator_gui
        print("\n[INFO] Launching Desktop GUI Calculator...")
        calculator_gui.main()
    except Exception as e:
        print(f"\n[ERROR] Failed to start GUI: {e}")


def run_cli():
    """Run interactive CLI calculator loop."""
    print_banner()
    history = CalculationHistory(max_items=50)

    last_result: Optional[str] = None

    while True:
        try:
            prompt = "\nEnter expression (or command): "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            cmd_lower = user_input.lower()

            # Exit command
            if cmd_lower in ("quit", "exit", "q"):
                print("\nThank you for using Auspify Python Calculator! Goodbye.\n")
                break

            # Launch GUI command
            if cmd_lower in ("gui", "start-gui"):
                launch_gui()
                continue

            # View History
            if cmd_lower == "history":
                records = history.get_all()
                print("\n" + "-" * 40)
                print("         CALCULATION HISTORY")
                print("-" * 40)
                if not records:
                    print("  (No calculation history yet)")
                else:
                    for i, r in enumerate(records, 1):
                        print(f"  [{i:02d}] {r['expression']} = {r['result']}  ({r['timestamp']})")
                print("-" * 40)
                continue

            # Clear History
            if cmd_lower in ("clear", "cls"):
                history.clear()
                print("\n[SUCCESS] Calculation history cleared.")
                continue

            # Support using 'ans' to reference last calculated result
            expr_to_eval = user_input
            if last_result is not None:
                expr_to_eval = expr_to_eval.replace("ans", last_result).replace("ANS", last_result)

            # Evaluate Expression
            numeric_res = safe_evaluate(expr_to_eval)
            formatted = format_result(numeric_res)
            last_result = formatted

            # Record in history
            history.add_entry(user_input, formatted)

            # Display formatted output
            print("-" * 40)
            print(f"Expression : {user_input}")
            print(f"Result     : {formatted}")
            print("-" * 40)

        except ZeroDivisionError:
            print("\n[ERROR] Division by zero is undefined.")
        except OverflowError:
            print("\n[ERROR] Numeric overflow -- result is too large.")
        except InvalidExpressionError as ie:
            print(f"\n[ERROR] Invalid Syntax: {ie}")
        except KeyboardInterrupt:
            print("\n\nOperation interrupted by user. Exiting...")
            break
        except Exception as ex:
            print(f"\n[ERROR] Unexpected error: {ex}")


def main():
    """Main entry point with CLI argument support."""
    parser = argparse.ArgumentParser(
        description="Auspify Technologies -- Task 3: Calculator (CLI & GUI)"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the desktop Tkinter GUI calculator directly.",
    )
    args = parser.parse_args()

    if args.gui:
        launch_gui()
    else:
        run_cli()


if __name__ == "__main__":
    main()
