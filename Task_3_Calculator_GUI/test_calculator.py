"""
test_calculator.py
==================
Unit Test Suite for Task 3: Calculator Application
Auspify Technologies — Python Development Internship

Comprehensive verification of:
- Basic and advanced arithmetic (+, -, *, /, %, ^, sqrt)
- PEMDAS operator precedence & parentheses nesting
- Unary operators and sign toggling
- ZeroDivisionError, OverflowError, and syntax error handling
- Security validation: AST verification preventing code injection
- History logging and capacity constraints
- Precision rounding and float formatting
"""

import math
import unittest
from calculator_core import (
    CalculationHistory,
    InvalidExpressionError,
    format_result,
    safe_evaluate,
    sanitize_expression,
)


class TestBasicArithmetic(unittest.TestCase):
    """Test primary arithmetic calculations."""

    def test_addition(self):
        self.assertEqual(safe_evaluate("12 + 34"), 46)
        self.assertEqual(safe_evaluate("0 + 0"), 0)
        self.assertEqual(safe_evaluate("-15 + 25"), 10)

    def test_subtraction(self):
        self.assertEqual(safe_evaluate("100 - 45"), 55)
        self.assertEqual(safe_evaluate("0 - 15"), -15)
        self.assertEqual(safe_evaluate("50 - (-20)"), 70)

    def test_multiplication(self):
        self.assertEqual(safe_evaluate("6 * 7"), 42)
        self.assertEqual(safe_evaluate("12 * 0"), 0)
        self.assertEqual(safe_evaluate("-4 * 8"), -32)
        # Unicode multiplication symbol
        self.assertEqual(safe_evaluate("6 × 7"), 42)

    def test_division(self):
        self.assertEqual(safe_evaluate("84 / 4"), 21)
        self.assertEqual(safe_evaluate("7 / 2"), 3.5)
        # Unicode division symbol
        self.assertEqual(safe_evaluate("84 ÷ 4"), 21)


class TestAdvancedOperations(unittest.TestCase):
    """Test exponentiation, modulo, square root, and functions."""

    def test_exponentiation(self):
        self.assertEqual(safe_evaluate("2 ^ 3"), 8)
        self.assertEqual(safe_evaluate("5 ** 2"), 25)
        self.assertEqual(safe_evaluate("2 ^ 0"), 1)
        self.assertEqual(safe_evaluate("4 ^ 0.5"), 2.0)

    def test_modulo(self):
        self.assertEqual(safe_evaluate("10 % 3"), 1)
        self.assertEqual(safe_evaluate("25 % 5"), 0)
        self.assertEqual(safe_evaluate("14 % 4"), 2)

    def test_square_root(self):
        self.assertEqual(safe_evaluate("sqrt(16)"), 4.0)
        self.assertEqual(safe_evaluate("sqrt(100)"), 10.0)
        # Radical symbol √
        self.assertEqual(safe_evaluate("√49"), 7.0)
        self.assertEqual(safe_evaluate("√(64)"), 8.0)

    def test_unary_operations(self):
        self.assertEqual(safe_evaluate("-5 + 10"), 5)
        self.assertEqual(safe_evaluate("+8 - 3"), 5)
        self.assertEqual(safe_evaluate("-(4 + 6)"), -10)
        self.assertEqual(safe_evaluate("-(-12)"), 12)


class TestPrecedenceAndParentheses(unittest.TestCase):
    """Verify standard order of operations (PEMDAS)."""

    def test_pemdas_order(self):
        # Multiplication before addition
        self.assertEqual(safe_evaluate("2 + 3 * 4"), 14)
        # Division before subtraction
        self.assertEqual(safe_evaluate("20 - 10 / 2"), 15)
        # Power before multiplication
        self.assertEqual(safe_evaluate("2 * 3 ^ 2"), 18)

    def test_parentheses_overrides(self):
        self.assertEqual(safe_evaluate("(2 + 3) * 4"), 20)
        self.assertEqual(safe_evaluate("(20 - 10) / 2"), 5)
        self.assertEqual(safe_evaluate("(2 * 3) ^ 2"), 36)

    def test_nested_parentheses(self):
        self.assertEqual(safe_evaluate("((2 + 3) * (5 - 1)) / 4"), 5)
        self.assertEqual(safe_evaluate("10 * (5 + (3 - 1))"), 70)

    def test_implicit_multiplication(self):
        self.assertEqual(safe_evaluate("2(3 + 4)"), 14)
        self.assertEqual(safe_evaluate("(2 + 1)(3 + 1)"), 12)
        self.assertEqual(safe_evaluate("(5)3"), 15)


class TestPrecisionAndFormatting(unittest.TestCase):
    """Verify floating point handling and format_result."""

    def test_floating_point_addition(self):
        # Standard IEEE 754 precision artifact (0.1 + 0.2 = 0.30000000000000004)
        res = safe_evaluate("0.1 + 0.2")
        formatted = format_result(res)
        self.assertEqual(formatted, "0.3")

    def test_integer_float_stripping(self):
        self.assertEqual(format_result(4.0), "4")
        self.assertEqual(format_result(100.0000), "100")
        self.assertEqual(format_result(-15.0), "-15")

    def test_precision_limiting(self):
        res = safe_evaluate("1 / 3")
        formatted = format_result(res, max_precision=6)
        self.assertEqual(formatted, "0.333333")


class TestErrorHandlingAndSecurity(unittest.TestCase):
    """Test exceptions on division by zero, invalid syntax, and security boundaries."""

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            safe_evaluate("10 / 0")

    def test_modulo_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            safe_evaluate("10 % 0")

    def test_negative_square_root(self):
        with self.assertRaises(InvalidExpressionError):
            safe_evaluate("sqrt(-16)")

    def test_syntax_errors(self):
        invalid_expressions = [
            "5 + * 2",
            "(3 + 2",
            ")3 + 2(",
            "++",
            "10 /",
            "...",
            "",
            "   ",
        ]
        for expr in invalid_expressions:
            with self.assertRaises(InvalidExpressionError):
                safe_evaluate(expr)

    def test_security_disallowed_code_injection(self):
        """Ensure malicious code / arbitrary functions are strictly rejected."""
        malicious_inputs = [
            "__import__('os').system('dir')",
            "open('test.txt', 'w')",
            "eval('2+2')",
            "exec('x=1')",
            "lambda: 42",
        ]
        for mal in malicious_inputs:
            with self.assertRaises(InvalidExpressionError):
                safe_evaluate(mal)


class TestCalculationHistory(unittest.TestCase):
    """Test calculation history management."""

    def setUp(self):
        self.history = CalculationHistory(max_items=3)

    def test_add_and_retrieve_history(self):
        self.history.add_entry("2 + 2", "4")
        self.history.add_entry("10 * 5", "50")
        records = self.history.get_all()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["expression"], "2 + 2")
        self.assertEqual(records[0]["result"], "4")
        self.assertEqual(records[1]["expression"], "10 * 5")
        self.assertEqual(records[1]["result"], "50")

    def test_history_capacity_limit(self):
        self.history.add_entry("1 + 1", "2")
        self.history.add_entry("2 + 2", "4")
        self.history.add_entry("3 + 3", "6")
        self.history.add_entry("4 + 4", "8")  # Exceeds max 3, pushes out 1+1
        records = self.history.get_all()
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["expression"], "2 + 2")
        self.assertEqual(records[-1]["expression"], "4 + 4")

    def test_history_clear(self):
        self.history.add_entry("5 + 5", "10")
        self.history.clear()
        self.assertEqual(len(self.history.get_all()), 0)


if __name__ == "__main__":
    unittest.main()
