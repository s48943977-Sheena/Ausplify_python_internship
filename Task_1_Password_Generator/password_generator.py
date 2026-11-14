"""
password_generator.py
=====================
Core cryptographic password generation and entropy analysis engine.

Developed for: Auspify Technologies — Python Development Internship
Author: Python Development Intern
Security Standard: Python 'secrets' CSPRNG (PEP 506 / RFC 4086 compliant)
"""

from __future__ import annotations
import math
import secrets
import string
from typing import Dict, List, Set, Tuple, Union


# Standard character pools
UPPERCASE_CHARS: str = string.ascii_uppercase
LOWERCASE_CHARS: str = string.ascii_lowercase
DIGIT_CHARS: str = string.digits
SYMBOL_CHARS: str = "!@#$%^&*()_+-=[]{}|;:,.<>?/~"

# Ambiguous characters often confused in print or screen fonts
AMBIGUOUS_CHARS: Set[str] = {"O", "0", "o", "l", "1", "I", "|"}

# Validation bounds
MIN_PASSWORD_LENGTH: int = 4
MAX_PASSWORD_LENGTH: int = 128
MAX_BATCH_COUNT: int = 10


class PasswordGenerationError(ValueError):
    """Raised when password generation parameters are invalid."""
    pass


class PasswordGenerator:
    """
    Cryptographically secure password generator and strength evaluator.
    
    Uses Python's built-in `secrets` module, which interfaces with OS-level
    cryptographic random sources (BCryptGenRandom on Windows, /dev/urandom on POSIX).
    This prevents PRNG predictability attacks inherent to the standard `random` module.
    """

    @staticmethod
    def filter_ambiguous(chars: str) -> str:
        """Remove visually ambiguous characters (O, 0, l, 1, I, etc.)."""
        return "".join(c for c in chars if c not in AMBIGUOUS_CHARS)

    @classmethod
    def generate_password(
        cls,
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_ambiguous: bool = False,
    ) -> str:
        """
        Generates a cryptographically secure password meeting all specified constraints.

        Security guarantees:
        1. Uses secrets.choice() for selecting characters.
        2. Guarantees that EVERY selected character category is represented at least once.
        3. Cryptographically shuffles character positions using secrets.SystemRandom().shuffle()
           so guaranteed characters are not predictable in position.
        4. Memory only: no password is saved to disk or network.

        :param length: Total password length (between 4 and 128).
        :param use_upper: Include uppercase letters (A-Z).
        :param use_lower: Include lowercase letters (a-z).
        :param use_digits: Include numerical digits (0-9).
        :param use_symbols: Include special symbols (!@#$%^&*...).
        :param exclude_ambiguous: Exclude visually confusing characters (O, 0, l, 1, I, |).
        :return: Secure generated password string.
        :raises PasswordGenerationError: If parameters violate security constraints.
        """
        # Validate length
        if not isinstance(length, int):
            raise PasswordGenerationError("Password length must be an integer.")
        if length < MIN_PASSWORD_LENGTH or length > MAX_PASSWORD_LENGTH:
            raise PasswordGenerationError(
                f"Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters."
            )

        # Assemble character pools
        selected_pools: List[str] = []

        if use_upper:
            pool = cls.filter_ambiguous(UPPERCASE_CHARS) if exclude_ambiguous else UPPERCASE_CHARS
            if pool:
                selected_pools.append(pool)
        if use_lower:
            pool = cls.filter_ambiguous(LOWERCASE_CHARS) if exclude_ambiguous else LOWERCASE_CHARS
            if pool:
                selected_pools.append(pool)
        if use_digits:
            pool = cls.filter_ambiguous(DIGIT_CHARS) if exclude_ambiguous else DIGIT_CHARS
            if pool:
                selected_pools.append(pool)
        if use_symbols:
            pool = cls.filter_ambiguous(SYMBOL_CHARS) if exclude_ambiguous else SYMBOL_CHARS
            if pool:
                selected_pools.append(pool)

        # Validation: At least one character pool must be selected
        if not selected_pools:
            raise PasswordGenerationError(
                "At least one character type (Uppercase, Lowercase, Numbers, or Symbols) must be selected."
            )

        # Validation: Length must be at least the number of selected pools to satisfy guaranteed representation
        if length < len(selected_pools):
            raise PasswordGenerationError(
                f"Password length ({length}) is too short to include all {len(selected_pools)} selected character types."
            )

        # Step 1: Guarantee representation - Pick 1 character from each selected category
        password_chars: List[str] = [secrets.choice(pool) for pool in selected_pools]

        # Step 2: Combine all selected pools for the remaining characters
        combined_pool: str = "".join(selected_pools)

        # Step 3: Fill the remaining length with cryptographically chosen characters
        remaining_count: int = length - len(password_chars)
        for _ in range(remaining_count):
            password_chars.append(secrets.choice(combined_pool))

        # Step 4: Cryptographically shuffle the characters in-place
        # Using secrets.SystemRandom ensures CSPRNG randomness during shuffle
        crypto_rng = secrets.SystemRandom()
        crypto_rng.shuffle(password_chars)

        return "".join(password_chars)

    @classmethod
    def generate_multiple(
        cls,
        count: int = 1,
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_ambiguous: bool = False,
    ) -> List[str]:
        """
        Generates multiple distinct cryptographically secure passwords.

        :param count: Number of passwords to generate (1 to 10).
        :return: List of generated passwords.
        :raises PasswordGenerationError: If count is out of bounds or parameters invalid.
        """
        if not isinstance(count, int) or count < 1 or count > MAX_BATCH_COUNT:
            raise PasswordGenerationError(
                f"Batch count must be an integer between 1 and {MAX_BATCH_COUNT}."
            )

        return [
            cls.generate_password(
                length=length,
                use_upper=use_upper,
                use_lower=use_lower,
                use_digits=use_digits,
                use_symbols=use_symbols,
                exclude_ambiguous=exclude_ambiguous,
            )
            for _ in range(count)
        ]

    @staticmethod
    def calculate_entropy(password: str) -> float:
        """
        Calculates the theoretical Shannon entropy in bits for the password:
            Entropy (bits) = Length * log2(Pool Size)

        Pool size is deduced from the unique character categories present.
        """
        if not password:
            return 0.0

        pool_size = 0
        has_upper = any(c in UPPERCASE_CHARS for c in password)
        has_lower = any(c in LOWERCASE_CHARS for c in password)
        has_digit = any(c in DIGIT_CHARS for c in password)
        has_symbol = any(c in SYMBOL_CHARS or not c.isalnum() for c in password)

        if has_upper:
            pool_size += 26
        if has_lower:
            pool_size += 26
        if has_digit:
            pool_size += 10
        if has_symbol:
            pool_size += 33  # Standard printable symbols

        if pool_size == 0:
            return 0.0

        entropy = len(password) * math.log2(pool_size)
        return round(entropy, 1)

    @classmethod
    def evaluate_strength(cls, password: str) -> Dict[str, Union[str, float, int]]:
        """
        Evaluates password strength based on length, entropy, and character diversity.

        Returns a detailed dictionary containing:
        - score: float between 0.0 (weakest) and 1.0 (strongest)
        - label: 'Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong'
        - color: Hex color code appropriate for GUI progress meters
        - entropy_bits: calculated entropy in bits
        - crack_time_estimate: estimated time to brute force at 10^10 guesses/sec
        - feedback: actionable guidance for user
        """
        if not password:
            return {
                "score": 0.0,
                "label": "None",
                "color": "#64748B",  # Muted slate
                "entropy_bits": 0.0,
                "crack_time_estimate": "N/A",
                "feedback": "Generate a password to see strength analysis.",
            }

        length = len(password)
        entropy = cls.calculate_entropy(password)

        has_upper = any(c in UPPERCASE_CHARS for c in password)
        has_lower = any(c in LOWERCASE_CHARS for c in password)
        has_digit = any(c in DIGIT_CHARS for c in password)
        has_symbol = any(c in SYMBOL_CHARS or not c.isalnum() for c in password)

        variety_count = sum([has_upper, has_lower, has_digit, has_symbol])

        # Estimate crack time based on entropy combinations (2^entropy / 10^10 guesses/sec)
        # Note: 10 billion guesses/sec is a representative high-end GPU cluster benchmark
        guesses_per_sec = 1e10
        try:
            total_combinations = 2.0 ** entropy
            seconds_to_crack = total_combinations / guesses_per_sec
        except OverflowError:
            seconds_to_crack = float("inf")

        crack_time_estimate = cls._format_time_estimate(seconds_to_crack)

        # Strength scoring (0.0 to 1.0)
        # Based on NIST SP 800-63B and standard password entropy metrics
        if length < 6 or entropy < 30 or variety_count <= 1:
            score = 0.20
            label = "Very Weak"
            color = "#EF4444"  # Red
            feedback = "Dangerous: Vulnerable to immediate dictionary and brute-force attacks."
        elif length < 8 or entropy < 48 or variety_count <= 2:
            score = 0.45
            label = "Weak"
            color = "#F97316"  # Orange
            feedback = "Sub-optimal: Consider increasing length and adding symbols/numbers."
        elif length < 12 or entropy < 70 or variety_count <= 2:
            score = 0.70
            label = "Moderate"
            color = "#EAB308"  # Amber/Yellow
            feedback = "Acceptable for general web accounts; recommend 16+ characters for critical assets."
        elif length < 16 or entropy < 90 or variety_count < 3:
            score = 0.88
            label = "Strong"
            color = "#06B6D4"  # Cyan
            feedback = "Excellent: Highly resilient against modern offline dictionary & GPU brute-force."
        else:
            score = 1.00
            label = "Very Strong"
            color = "#10B981"  # Emerald Green
            feedback = "Enterprise Grade: Cryptographically robust against all known attack vectors."

        return {
            "score": score,
            "label": label,
            "color": color,
            "entropy_bits": entropy,
            "crack_time_estimate": crack_time_estimate,
            "feedback": feedback,
        }

    @staticmethod
    def _format_time_estimate(seconds: float) -> str:
        """Formats cracking duration into human-readable intervals."""
        if seconds <= 0.01:
            return "Instantaneous (< 1 millisecond)"
        if seconds < 1:
            return "Less than 1 second"
        if seconds < 60:
            return f"{round(seconds, 1)} seconds"
        minutes = seconds / 60
        if minutes < 60:
            return f"~{int(minutes)} minutes"
        hours = minutes / 60
        if hours < 24:
            return f"~{int(hours)} hours"
        days = hours / 24
        if days < 365:
            return f"~{int(days)} days"
        years = days / 365.25
        if years < 1000:
            return f"~{int(years):,} years"
        if years < 1_000_000:
            return f"~{int(years / 1000):,} thousand years"
        if years < 1_000_000_000:
            return f"~{int(years / 1_000_000):,} million years"
        return "Centuries (Billions of years)"
