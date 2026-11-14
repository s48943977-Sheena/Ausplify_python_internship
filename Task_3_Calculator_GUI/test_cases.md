# Test Cases — Task 3: Modern Desktop & CLI Calculator

## Testing Environment

- **Operating System:** Windows 10 / 11
- **Programming Language:** Python 3.10+ (Verified on Python 3.14)
- **IDE / Environment:** Visual Studio Code / Windows PowerShell
- **GUI Framework:** Python Tkinter (Standard Library, zero external dependencies)
- **Parser Architecture:** Safe AST (Abstract Syntax Tree) with strict operator whitelisting (no `eval()`)
- **Automated Test Runner:** Python `unittest` framework (`test_calculator.py`)

---

## Test Results Summary

| ID | Test Case | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC01** | Basic Arithmetic (+, -, *, /) | Evaluates standard addition, subtraction, multiplication, and division accurately | Correct numerical results; integers formatted without `.0` | **Pass** |
| **TC02** | PEMDAS Operator Precedence | Multiplications and divisions evaluate before additions and subtractions without parentheses | `2 + 3 * 4` evaluates to `14`; `20 - 10 / 2` evaluates to `15` | **Pass** |
| **TC03** | Parentheses & Implicit Multiplication | Parentheses override standard precedence; expressions like `2(3+4)` parse properly | `(2 + 3) * 4` evaluates to `20`; `2(3+4)` evaluates to `14` | **Pass** |
| **TC04** | Exponentiation, Modulo & Roots | Computes powers (`^`, `**`), remainder (`%`), and square roots (`√`, `sqrt`) | `2 ^ 3 = 8`, `10 % 3 = 1`, `√16 = 4`, `sqrt(25) = 5` | **Pass** |
| **TC05** | Unary Operators & Sign Toggle (±) | Supports negative numbers and toggles positive/negative states on demand | `-5 + 10 = 5`; pressing `±` toggles active number sign | **Pass** |
| **TC06** | Floating Point Precision Handling | Mitigates IEEE 754 precision artifacts (`0.1 + 0.2`) and strips trailing float zeros | `0.1 + 0.2` formats cleanly as `0.3`; `4.0` displays as `4` | **Pass** |
| **TC07** | Zero Division Protection | Gracefully traps division and modulo by zero without crashing terminal or GUI | Raises `ZeroDivisionError`; UI shows "Cannot divide by zero" | **Pass** |
| **TC08** | Malformed Syntax & Unbalanced Parentheses | Rejects dangling operators (`5 + * 2`) and unclosed brackets (`(2+3`) | Cleanly caught as `InvalidExpressionError`; UI displays "Error" | **Pass** |
| **TC09** | Security & Code Injection Prevention | Strictly blocks arbitrary code execution (`eval`, `exec`, `__import__`, `open`) | AST rejects non-mathematical nodes; prevents arbitrary execution | **Pass** |
| **TC10** | Calculation History Management | Logs timestamped expressions and results; supports 1-click re-insertion and clearing | History drawer logs calculations; double-click loads result into display | **Pass** |
| **TC11** | Desktop GUI Interactivity & Theme | High-contrast modern dark layout with responsive hover transitions and active states | Rendered at 420x680; smooth button hover states and crisp typography | **Pass** |
| **TC12** | Keyboard Navigation & Clipboard Sync | Full keyboard support (Enter, Backspace, Esc, digits) and 1-click clipboard copy | Keyboard enters numbers/operators seamlessly; clipboard copies result | **Pass** |

---

## Detailed Test Logs

### TC01: Basic Arithmetic Operations
- **Input Expressions:**
  - `12 + 34`
  - `100 - 45`
  - `6 * 7`
  - `84 / 4`
- **Output:** `46`, `55`, `42`, `21`
- **Verification:** Computed accurately using safe AST traversal; results match standard mathematical expectations.

### TC02: PEMDAS Operator Precedence
- **Input Expressions:**
  - `2 + 3 * 4`
  - `20 - 10 / 2`
  - `2 * 3 ^ 2`
- **Expected Results:** `14`, `15`, `18`
- **Actual Results:** `14`, `15`, `18`
- **Verification:** Operator precedence follows standard algebraic rules (Powers first, then Multiplication/Division left-to-right, then Addition/Subtraction).

### TC03: Parentheses Grouping & Implicit Multiplication
- **Input Expressions:**
  - `(2 + 3) * 4`
  - `((2 + 3) * (5 - 1)) / 4`
  - `2(3 + 4)`
  - `(2 + 1)(3 + 1)`
- **Expected Results:** `20`, `5`, `14`, `12`
- **Actual Results:** `20`, `5`, `14`, `12`
- **Verification:** Preprocessing successfully expands implicit multiplication tokens into explicit AST `Mult` nodes and honors parenthesis nesting depths.

### TC04: Exponentiation, Modulo & Roots
- **Input Expressions:**
  - `2 ^ 3`
  - `10 % 3`
  - `√49`
  - `sqrt(100) + 5`
- **Expected Results:** `8`, `1`, `7`, `15`
- **Actual Results:** `8`, `1`, `7`, `15`
- **Verification:** Functions and power operators map directly to Python `math` library calls within safe boundaries.

### TC05: Unary Operators & Sign Toggle (±)
- **Input Expressions:**
  - `-5 + 10`
  - `-(4 + 6)`
  - Toggle `±` on `25` -> `-25`
- **Expected Results:** `5`, `-10`, `-25`
- **Actual Results:** `5`, `-10`, `-25`
- **Verification:** Unary plus/minus operations parse correctly via `ast.UAdd` and `ast.USub`.

### TC06: Floating Point Precision Handling
- **Input Expressions:**
  - `0.1 + 0.2`
  - `7 / 2`
  - `4.0`
- **Expected Results:** `0.3` (not `0.30000000000000004`), `3.5`, `4`
- **Actual Results:** `0.3`, `3.5`, `4`
- **Verification:** `format_result()` eliminates IEEE 754 float representation noise and strips superfluous trailing decimals for integers.

### TC07: Zero Division Error Handling
- **Input Expressions:**
  - `10 / 0`
  - `15 % 0`
- **Expected Behavior:** Trapped before evaluation; clean `ZeroDivisionError` raised.
- **Actual GUI Output:** History shows "Cannot divide by zero"; display shows "Error".
- **Actual CLI Output:** Displays `[ERROR] Division by zero is undefined.` without halting runtime loop.

### TC08: Malformed Syntax & Unbalanced Parentheses
- **Input Expressions:**
  - `5 + * 2`
  - `(3 + 2`
  - `10 /`
  - `""` (empty)
- **Expected Behavior:** AST parser raises `InvalidExpressionError`.
- **Actual GUI Output:** Display shows "Error"; secondary history label highlights "Invalid expression syntax".
- **Verification:** Application catches syntax errors cleanly and resets state on subsequent input.

### TC09: Security & Code Injection Prevention
- **Input Expressions:**
  - `__import__('os').system('dir')`
  - `eval('2+2')`
  - `open('passwords.txt', 'w')`
- **Expected Behavior:** Strictly rejected at both character whitelist and AST inspection stages.
- **Verification:** The AST evaluator only permits approved arithmetic nodes (`Constant`, `UnaryOp`, `BinOp`, whitelisted `Call`). Arbitrary method lookups, attribute accesses (`ast.Attribute`), and imports are completely unreachable.

### TC10: Calculation History Management
- **Workflow:**
  1. Calculate `12 + 18 = 30`
  2. Calculate `30 * 4 = 120`
  3. Open History drawer via Top Bar button
  4. Double-click record #2 (`120`)
- **Verification:** The history drawer displays numbered entries with timestamps. Double-clicking re-loads `120` into the active calculator display for chaining calculations. Clear history purges all stored items.

### TC11: Desktop GUI Interactivity & Theme
- **Actions:** Launch `python calculator_gui.py`.
- **Observations:**
  - Window opens centered on screen at 420x680 resolution.
  - Dark modern aesthetic with distinct visual hierarchy:
    - Number keys in dark slate (`#1E293B`)
    - Basic operators in indigo (`#6366F1`)
    - Function keys in sky blue (`#0284C7`)
    - Clear key in coral red (`#EF4444`)
    - Backspace key in amber (`#F59E0B`)
    - Equals key in emerald green (`#10B981`)
  - Mouse hover dynamically alters button background colors.

### TC12: Keyboard Navigation & Clipboard Sync
- **Actions:**
  - Type `2 * 5` on physical keyboard, press `Enter`. Display shows `10`.
  - Press `Ctrl+C` or click `📋 Copy`.
- **Verification:**
  - Keyboard mappings fire appropriate button actions.
  - Status toast "✓ Copied to clipboard!" appears in the display card.
  - Pasting into external editors yields `10`.
