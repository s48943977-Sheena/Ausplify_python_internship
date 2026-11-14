"""
test_password_generator.py
==========================
Unit test suite for the SecurePass password generation logic.

Verifies:
- Minimum (4) and maximum (128) lengths
- Invalid inputs and boundary validation
- Character pool selection (individual and combined)
- Strict guarantee of category representation
- Cryptographic shuffle uniformity
- Ambiguous character exclusion
- Batch password generation (1-10)
- Entropy and strength analysis
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import unittest
from password_generator import (
    PasswordGenerator,
    PasswordGenerationError,
    UPPERCASE_CHARS,
    LOWERCASE_CHARS,
    DIGIT_CHARS,
    SYMBOL_CHARS,
    AMBIGUOUS_CHARS,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_BATCH_COUNT,
)


class TestPasswordGenerator(unittest.TestCase):

    def test_minimum_length(self):
        """Verify generation at exact minimum length boundary (4)."""
        pw = PasswordGenerator.generate_password(
            length=MIN_PASSWORD_LENGTH,
            use_upper=True,
            use_lower=True,
            use_digits=True,
            use_symbols=True,
        )
        self.assertEqual(len(pw), MIN_PASSWORD_LENGTH)
        # All 4 categories must be present
        self.assertTrue(any(c in UPPERCASE_CHARS for c in pw))
        self.assertTrue(any(c in LOWERCASE_CHARS for c in pw))
        self.assertTrue(any(c in DIGIT_CHARS for c in pw))
        self.assertTrue(any(c in SYMBOL_CHARS for c in pw))

    def test_maximum_length(self):
        """Verify generation at exact maximum length boundary (128)."""
        pw = PasswordGenerator.generate_password(length=MAX_PASSWORD_LENGTH)
        self.assertEqual(len(pw), MAX_PASSWORD_LENGTH)

    def test_invalid_lengths(self):
        """Ensure boundary violation errors are raised."""
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator.generate_password(length=3)

        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator.generate_password(length=129)

        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator.generate_password(length="invalid")  # type: ignore

    def test_no_character_categories_selected(self):
        """Ensure selecting zero character categories raises an error."""
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator.generate_password(
                length=16,
                use_upper=False,
                use_lower=False,
                use_digits=False,
                use_symbols=False,
            )

    def test_single_category_generation(self):
        """Verify generating passwords with only one category enabled."""
        # Only digits
        pw_digits = PasswordGenerator.generate_password(
            length=12,
            use_upper=False,
            use_lower=False,
            use_digits=True,
            use_symbols=False,
        )
        self.assertEqual(len(pw_digits), 12)
        self.assertTrue(all(c in DIGIT_CHARS for c in pw_digits))

        # Only uppercase
        pw_upper = PasswordGenerator.generate_password(
            length=10,
            use_upper=True,
            use_lower=False,
            use_digits=False,
            use_symbols=False,
        )
        self.assertEqual(len(pw_upper), 10)
        self.assertTrue(all(c in UPPERCASE_CHARS for c in pw_upper))

        # Only lowercase
        pw_lower = PasswordGenerator.generate_password(
            length=10,
            use_upper=False,
            use_lower=True,
            use_digits=False,
            use_symbols=False,
        )
        self.assertEqual(len(pw_lower), 10)
        self.assertTrue(all(c in LOWERCASE_CHARS for c in pw_lower))

        # Only symbols
        pw_symbols = PasswordGenerator.generate_password(
            length=10,
            use_upper=False,
            use_lower=False,
            use_digits=False,
            use_symbols=True,
        )
        self.assertEqual(len(pw_symbols), 10)
        self.assertTrue(all(c in SYMBOL_CHARS for c in pw_symbols))

    def test_guaranteed_category_representation(self):
        """
        Critical security test:
        Generate 1,000 passwords with all 4 categories enabled.
        Assert that 100% of them have at least one character from EACH selected category.
        """
        for _ in range(1000):
            pw = PasswordGenerator.generate_password(
                length=16,
                use_upper=True,
                use_lower=True,
                use_digits=True,
                use_symbols=True,
            )
            has_upper = any(c in UPPERCASE_CHARS for c in pw)
            has_lower = any(c in LOWERCASE_CHARS for c in pw)
            has_digit = any(c in DIGIT_CHARS for c in pw)
            has_symbol = any(c in SYMBOL_CHARS for c in pw)

            self.assertTrue(has_upper, f"Missing uppercase in: {pw}")
            self.assertTrue(has_lower, f"Missing lowercase in: {pw}")
            self.assertTrue(has_digit, f"Missing digit in: {pw}")
            self.assertTrue(has_symbol, f"Missing symbol in: {pw}")

    def test_cryptographic_shuffle(self):
        """
        Verify that guaranteed characters aren't just placed at indices 0, 1, 2, 3.
        The first character should vary across different categories.
        """
        first_chars = [
            PasswordGenerator.generate_password(length=16)[0]
            for _ in range(100)
        ]
        # Should see multiple different character sets at index 0
        has_upper_first = any(c in UPPERCASE_CHARS for c in first_chars)
        has_lower_first = any(c in LOWERCASE_CHARS for c in first_chars)
        has_digit_first = any(c in DIGIT_CHARS for c in first_chars)
        has_symbol_first = any(c in SYMBOL_CHARS for c in first_chars)

        self.assertTrue(has_upper_first and has_lower_first and has_digit_first and has_symbol_first)

    def test_exclude_ambiguous_characters(self):
        """Verify that ambiguous characters (0, O, 1, l, I, |) are never included when excluded."""
        for _ in range(200):
            pw = PasswordGenerator.generate_password(
                length=32,
                use_upper=True,
                use_lower=True,
                use_digits=True,
                use_symbols=True,
                exclude_ambiguous=True,
            )
            for amb in AMBIGUOUS_CHARS:
                self.assertNotIn(amb, pw, f"Found ambiguous character '{amb}' in {pw}")

    def test_batch_generation(self):
        """Verify generating multiple passwords at once."""
        count = 5
        passwords = PasswordGenerator.generate_multiple(count=count, length=16)
        self.assertEqual(len(passwords), count)
        # Verify all are valid length
        for p in passwords:
            self.assertEqual(len(p), 16)
        # Verify uniqueness (due to high entropy, collisions are negligible)
        self.assertEqual(len(set(passwords)), count)

    def test_batch_count_bounds(self):
        """Verify batch generation count limits."""
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator.generate_multiple(count=0)

        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator.generate_multiple(count=MAX_BATCH_COUNT + 1)

    def test_strength_evaluation(self):
        """Test entropy and strength calculations."""
        # Very weak
        eval_weak = PasswordGenerator.evaluate_strength("abc")
        self.assertEqual(eval_weak["label"], "Very Weak")
        self.assertLess(eval_weak["score"], 0.4)

        # Weak
        eval_simple = PasswordGenerator.evaluate_strength("password")
        self.assertIn(eval_simple["label"], ["Very Weak", "Weak"])

        # Moderate
        eval_mod = PasswordGenerator.evaluate_strength("Secret123")
        self.assertIn(eval_mod["label"], ["Weak", "Moderate"])

        # Strong
        eval_strong = PasswordGenerator.evaluate_strength("K9#vP2$xL7!m")
        self.assertIn(eval_strong["label"], ["Strong", "Very Strong"])

        # Very strong
        eval_vstrong = PasswordGenerator.evaluate_strength("V#8m!K9$xL7@pQ2&wZ1*rT5^yU4~")
        self.assertEqual(eval_vstrong["label"], "Very Strong")
        self.assertEqual(eval_vstrong["score"], 1.0)
        self.assertGreater(eval_vstrong["entropy_bits"], 80.0)


if __name__ == "__main__":
    unittest.main()
