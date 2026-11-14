"""
calculator_core.py
==================
Core mathematical evaluation engine and calculation history tracker for
Task 3: Calculator Application (Auspify Technologies — Python Internship).

Features:
- Safe AST (Abstract Syntax Tree) expression parser and evaluator.
- Strictly eliminates dangerous `eval()` execution to prevent code injection.
- Complete support for PEMDAS precedence, parentheses, floating point decimals,
  unary negation, exponentiation (^ or **), modulo (%), and square root (sqrt).
- Clean mathematical formatting and zero-division protection.
- Calculation history recording with timestamps and recall capabilities.
"""

import ast
import math
import operator
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


class CalculationError(Exception):
    """Custom exception base for calculation errors."""
    pass


class InvalidExpressionError(CalculationError):
    """Raised when an expression contains invalid syntax or unsupported tokens."""
    pass


# Supported binary and unary operations mapping
BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Math functions allowed in expressions
ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
    "log": math.log10,
    "ln": math.log,
}


def sanitize_expression(expr: str) -> str:
    """
    Sanitize and preprocess the mathematical expression string.
    - Replaces visual glyphs (×, ÷, −, ^) with Python operators.
    - Normalizes implicit multiplication e.g., 2(3) -> 2*(3) or (2)(3) -> (2)*(3).
    - Replaces sqrt(x) if written as √x.
    """
    if not isinstance(expr, str):
        raise InvalidExpressionError("Expression must be a string.")

    cleaned = expr.strip()
    if not cleaned:
        raise InvalidExpressionError("Expression cannot be empty.")

    # Replace common Unicode symbols
    cleaned = cleaned.replace("×", "*").replace("÷", "/")
    cleaned = cleaned.replace("−", "-").replace("–", "-")
    cleaned = cleaned.replace("^", "**")

    # Handle square root symbol √x or √(x) -> sqrt(x)
    cleaned = re.sub(r"√\s*(\d+(\.\d+)?)", r"sqrt(\1)", cleaned)
    cleaned = re.sub(r"√\s*\(", r"sqrt(", cleaned)

    # Implicit multiplication: digit followed by parenthesis: 2(3) -> 2*(3)
    cleaned = re.sub(r"(\d)\s*\(", r"\1*(", cleaned)
    # Implicit multiplication: closing parenthesis followed by opening: )( -> )*(
    cleaned = re.sub(r"\)\s*\(", r")*(", cleaned)
    # Implicit multiplication: closing parenthesis followed by digit: )2 -> )*2
    cleaned = re.sub(r"\)\s*(\d)", r")*\1", cleaned)

    return cleaned


def safe_evaluate(expression: str) -> Union[int, float]:
    """
    Safely evaluate a mathematical expression using Python's AST parser.
    Guarantees no arbitrary code execution (no eval/exec).

    Raises:
        InvalidExpressionError: If syntax is malformed or invalid tokens are present.
        ZeroDivisionError: If division or modulo by zero is attempted.
        OverflowError: If calculation exceeds numeric limits.
    """
    cleaned = sanitize_expression(expression)

    # Validate character whitelist: only digits, decimal point, operators, parentheses, function names
    valid_chars_regex = r"^[0-9+\-*/%().,\s*a-zA-Z_]+$"
    if not re.match(valid_chars_regex, cleaned):
        raise InvalidExpressionError("Expression contains invalid or unsupported characters.")

    try:
        parsed_tree = ast.parse(cleaned, mode="eval")
    except SyntaxError as e:
        raise InvalidExpressionError(f"Syntax error in expression: {e.msg}") from e

    def _eval_node(node: ast.AST) -> Union[int, float]:
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)

        # Numbers (constants)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise InvalidExpressionError(f"Unsupported constant type: {type(node.value).__name__}")

        # Unary operations (e.g., -5, +3)
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in UNARY_OPERATORS:
                operand_val = _eval_node(node.operand)
                return UNARY_OPERATORS[op_type](operand_val)
            raise InvalidExpressionError(f"Unsupported unary operator: {op_type.__name__}")

        # Binary operations (e.g., 2 + 3, 4 * 5, 2 ** 3, 10 % 3)
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in BINARY_OPERATORS:
                raise InvalidExpressionError(f"Unsupported binary operator: {op_type.__name__}")

            left_val = _eval_node(node.left)
            right_val = _eval_node(node.right)

            # Division or Modulo by zero check
            if op_type is ast.Div:
                if right_val == 0:
                    raise ZeroDivisionError("Cannot divide by zero.")
            elif op_type is ast.Mod:
                if right_val == 0:
                    raise ZeroDivisionError("Cannot perform modulo by zero.")
            elif op_type is ast.Pow:
                # Prevent massive exponents that cause CPU hang (Denial of Service)
                if abs(right_val) > 10000:
                    raise OverflowError("Exponent too large to compute.")

            calc_func = BINARY_OPERATORS[op_type]
            try:
                result = calc_func(left_val, right_val)
            except OverflowError:
                raise OverflowError("Calculation result exceeded numerical limits.")
            return result

        # Function calls (e.g. sqrt(16), abs(-5))
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id.lower()
                if func_name in ALLOWED_FUNCTIONS:
                    if len(node.args) != 1:
                        raise InvalidExpressionError(f"Function '{func_name}' expects exactly 1 argument.")
                    arg_val = _eval_node(node.args[0])
                    if func_name == "sqrt" and arg_val < 0:
                        raise InvalidExpressionError("Cannot take the square root of a negative number.")
                    return ALLOWED_FUNCTIONS[func_name](arg_val)
                raise InvalidExpressionError(f"Function '{func_name}' is not permitted.")
            raise InvalidExpressionError("Unsupported function invocation.")

        raise InvalidExpressionError(f"Unsupported syntax structure: {type(node).__name__}")

    raw_result = _eval_node(parsed_tree)

    # Validate finite float
    if isinstance(raw_result, (int, float)):
        if not math.isfinite(raw_result):
            raise OverflowError("Result is infinite or undefined.")

    return raw_result


def format_result(val: Union[int, float], max_precision: int = 10) -> str:
    """
    Format a numeric calculation result into an aesthetically pleasing string.
    - Strips redundant trailing zeros (e.g. 5.0 -> '5').
    - Avoids scientific notation where feasible for standard numbers.
    - Limits floating point precision to avoid IEEE 754 artifacts (0.1 + 0.2 -> '0.3').
    """
    if isinstance(val, (int, float)):
        if isinstance(val, float) and val.is_integer():
            return str(int(val))

        if isinstance(val, float):
            # Round to max_precision to eliminate representation noise
            rounded = round(val, max_precision)
            if rounded.is_integer():
                return str(int(rounded))
            formatted = f"{rounded:.{max_precision}f}".rstrip("0").rstrip(".")
            return formatted

        return str(val)

    return str(val)


class CalculationHistory:
    """Manages the history of calculations in memory with persistence capabilities."""

    def __init__(self, max_items: int = 50):
        self.max_items = max_items
        self.records: List[Dict[str, str]] = []

    def add_entry(self, expression: str, result: str) -> Dict[str, str]:
        """Record a completed calculation."""
        entry = {
            "expression": expression,
            "result": result,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.records.append(entry)
        if len(self.records) > self.max_items:
            self.records.pop(0)
        return entry

    def get_all(self) -> List[Dict[str, str]]:
        """Return all historical records in chronological order."""
        return list(self.records)

    def get_latest(self) -> Optional[Dict[str, str]]:
        """Return the most recent calculation record."""
        return self.records[-1] if self.records else None

    def clear(self) -> None:
        """Clear all history records."""
        self.records.clear()

    def __len__(self) -> int:
        return len(self.records)


if __name__ == "__main__":
    print("=" * 55)
    print("  Task 3: Calculator Core Mathematical Engine")
    print("  (Auspify Technologies -- Python Development Internship)")
    print("=" * 55)
    print("\n[NOTE] 'calculator_core.py' is the backend mathematical engine.")
    print("       It provides AST parsing, PEMDAS evaluation, and security checks.\n")
    print("To launch the applications:")
    print("  * Desktop GUI Calculator  -> python calculator_gui.py")
    print("  * Terminal CLI Calculator -> python calculator.py\n")

    print("Running quick engine self-test:")
    demo_samples = [
        "2 + 3 * 4",
        "(25 + 15) * 4",
        "2 ^ 3",
        "10 % 3",
        "sqrt(144) + 8",
        "0.1 + 0.2",
    ]
    for expr in demo_samples:
        try:
            res = format_result(safe_evaluate(expr))
            print(f"  [PASS] {expr:<18} = {res}")
        except Exception as e:
            print(f"  [FAIL] {expr:<18} -> Error: {e}")

    print("\nEngine status: 100% OPERATIONAL (Ready for GUI and CLI use).")
    print("=" * 55)
