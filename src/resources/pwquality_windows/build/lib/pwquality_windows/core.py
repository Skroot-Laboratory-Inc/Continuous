"""
Windows-compatible interface replicating Ubuntu 24.04 python-pwquality package functionality.
This module provides password quality checking without requiring libpwquality.
"""

import re
import string
from typing import Dict, List, Optional, Union
from enum import IntEnum


class PWQError(Exception):
    """Exception raised for password quality errors."""

    # Error codes matching libpwquality
    GENERIC_ERROR = -1
    BAD_WORDS = -2
    TOO_SHORT = -3
    TOO_LONG = -4
    INSUFFICIENT_DIFFERENT_CLASSES = -5
    TOO_MANY_REPEATS = -6
    TOO_MANY_SAME_CLASS_CONSECUTIVE = -7
    TOO_MANY_SEQUENTIAL = -8
    PALINDROME = -9
    CASE_CHANGES_ONLY = -10
    TOO_SIMILAR = -11
    USER_CHECK = -12
    GECOS_CHECK = -13
    BAD_WORDS_IN_PASSWORD = -14

    def __init__(self, message: str, error_code: int = GENERIC_ERROR):
        super().__init__(message)
        self.error_code = error_code


class PWQSettings:
    """
    Python interface for password quality checking, compatible with Ubuntu's python-pwquality.
    """

    def __init__(self):
        """Initialize PWQSettings with default settings."""
        self.settings = {
            'minlen': 8,           # Minimum password length
            'maxlen': 0,           # Maximum password length (0 = no limit)
            'dcredit': 0,          # Digit character credit/requirement
            'ucredit': 0,          # Upper case character credit/requirement
            'lcredit': 0,          # Lower case character credit/requirement
            'ocredit': 0,          # Other character credit/requirement
            'minclass': 0,         # Minimum number of character classes
            'maxrepeat': 0,        # Maximum number of repeating characters
            'maxclassrepeat': 0,   # Maximum number of consecutive same class chars
            'maxsequence': 0,      # Maximum length of monotonic character sequence
            'gecoscheck': 0,       # Check against GECOS field
            'dictcheck': 1,        # Check against dictionary words
            'usercheck': 1,        # Check against username
            'enforcing': 1,        # Enforcing mode
            'badwords': [],        # Custom bad words list
            'retry': 3,            # Number of retries
        }

        # Common weak passwords and patterns
        self.common_passwords = {
            'password', 'admin', 'root', '123456', 'qwerty', 'abc123',
            'password123', 'admin123', 'welcome', 'letmein', 'monkey',
            'dragon', 'master', 'shadow', 'superman', 'michael', 'football'
        }

        # Sequential patterns
        self.sequences = [
            'abcdefghijklmnopqrstuvwxyz',
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            '01234567890',
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]

    def read_config(self, config_file: Optional[str] = None) -> int:
        """
        Read configuration from file (stub implementation).

        Args:
            config_file: Path to configuration file

        Returns:
            0 on success, negative on error
        """
        # In real implementation, would parse /etc/security/pwquality.conf
        return 0

    def set_option(self, option: str, value: Union[int, str, List[str]]) -> int:
        """
        Set a configuration option.

        Args:
            option: Option name
            value: Option value

        Returns:
            0 on success, negative on error
        """
        if option in self.settings:
            if option == 'badwords' and isinstance(value, str):
                self.settings[option] = [word.strip() for word in value.split(',')]
            else:
                self.settings[option] = value
            return 0
        return -1

    def get_option(self, option: str) -> Union[int, str, List[str], None]:
        """
        Get a configuration option value.

        Args:
            option: Option name

        Returns:
            Option value or None if not found
        """
        return self.settings.get(option)

    def check(self, password: str, oldpassword: Optional[str] = None,
              user: Optional[str] = None, gecos: Optional[str] = None) -> int:
        """
        Check password quality.

        Args:
            password: Password to check
            oldpassword: Previous password for similarity check
            user: Username for user check
            gecos: GECOS field for gecos check

        Returns:
            Password score (positive) or raises PWQError

        Raises:
            PWQError: If password fails quality checks
        """
        score = 0

        # Length checks
        if len(password) < self.settings['minlen']:
            raise PWQError(
                f"Password too short (minimum {self.settings['minlen']} characters)",
                PWQError.TOO_SHORT
            )

        if self.settings['maxlen'] > 0 and len(password) > self.settings['maxlen']:
            raise PWQError(
                f"Password too long (maximum {self.settings['maxlen']} characters)",
                PWQError.TOO_LONG
            )

        # Character class analysis
        char_classes = self._analyze_character_classes(password)

        # Check minimum character classes
        if self.settings['minclass'] > 0:
            active_classes = sum(1 for count in char_classes.values() if count > 0)
            if active_classes < self.settings['minclass']:
                raise PWQError(
                    f"Password must contain at least {self.settings['minclass']} different character types",
                    PWQError.INSUFFICIENT_DIFFERENT_CLASSES
                )

        # Credit/requirement checks
        self._check_character_requirements(password, char_classes)

        # Repeat character checks
        if self.settings['maxrepeat'] > 0:
            max_repeat = self._find_max_repeats(password)
            if max_repeat > self.settings['maxrepeat']:
                raise PWQError(
                    f"Password contains too many repeating characters (max {self.settings['maxrepeat']})",
                    PWQError.TOO_MANY_REPEATS
                )

        # Same class consecutive check
        if self.settings['maxclassrepeat'] > 0:
            max_class_repeat = self._find_max_class_repeats(password)
            if max_class_repeat > self.settings['maxclassrepeat']:
                raise PWQError(
                    f"Password contains too many consecutive characters of the same type",
                    PWQError.TOO_MANY_SAME_CLASS_CONSECUTIVE
                )

        # Sequential character check
        if self.settings['maxsequence'] > 0:
            max_sequence = self._find_max_sequence(password)
            if max_sequence > self.settings['maxsequence']:
                raise PWQError(
                    f"Password contains too long sequential characters",
                    PWQError.TOO_MANY_SEQUENTIAL
                )

        # Dictionary/common password check
        if self.settings['dictcheck']:
            if password.lower() in self.common_passwords:
                raise PWQError(
                    "Password is too common",
                    PWQError.BAD_WORDS
                )

        # Custom bad words check
        if self.settings['badwords']:
            password_lower = password.lower()
            for bad_word in self.settings['badwords']:
                if bad_word.lower() in password_lower:
                    raise PWQError(
                        "Password contains forbidden word",
                        PWQError.BAD_WORDS_IN_PASSWORD
                    )

        # Username check
        if self.settings['usercheck'] and user:
            if user.lower() in password.lower():
                raise PWQError(
                    "Password contains username",
                    PWQError.USER_CHECK
                )

        # GECOS check
        if self.settings['gecoscheck'] and gecos:
            gecos_words = re.findall(r'\w+', gecos.lower())
            password_lower = password.lower()
            for word in gecos_words:
                if len(word) > 2 and word in password_lower:
                    raise PWQError(
                        "Password contains personal information",
                        PWQError.GECOS_CHECK
                    )

        # Palindrome check
        if self._is_palindrome(password):
            raise PWQError(
                "Password is a palindrome",
                PWQError.PALINDROME
            )

        # Case changes only check
        if oldpassword and self._is_case_change_only(password, oldpassword):
            raise PWQError(
                "Password is only case changes of old password",
                PWQError.CASE_CHANGES_ONLY
            )

        # Similarity check
        if oldpassword and self._is_too_similar(password, oldpassword):
            raise PWQError(
                "Password is too similar to old password",
                PWQError.TOO_SIMILAR
            )

        # Calculate score based on complexity
        score = self._calculate_score(password, char_classes)

        return score

    def generate(self, entropy: int = 64) -> str:
        """
        Generate a random password.

        Args:
            entropy: Desired entropy in bits

        Returns:
            Generated password
        """
        import secrets

        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

        all_chars = lowercase + uppercase + digits + symbols

        # Calculate required length for desired entropy
        import math
        length = max(8, int(math.ceil(entropy / math.log2(len(all_chars)))))

        # Ensure at least one character from each class
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]

        # Fill remaining length
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)

        return ''.join(password)

    def _analyze_character_classes(self, password: str) -> Dict[str, int]:
        """Analyze character classes in password."""
        classes = {
            'lower': sum(1 for c in password if c.islower()),
            'upper': sum(1 for c in password if c.isupper()),
            'digit': sum(1 for c in password if c.isdigit()),
            'other': sum(1 for c in password if not c.isalnum())
        }
        return classes

    def _check_character_requirements(self, password: str, char_classes: Dict[str, int]):
        """Check character credit/requirement settings."""
        checks = [
            ('dcredit', 'digit', 'digit'),
            ('ucredit', 'upper', 'uppercase'),
            ('lcredit', 'lower', 'lowercase'),
            ('ocredit', 'other', 'special')
        ]

        for setting, class_key, name in checks:
            requirement = self.settings[setting]
            if requirement > 0:  # Minimum requirement
                if char_classes[class_key] < requirement:
                    raise PWQError(
                        f"Password must contain at least {requirement} {name} characters",
                        PWQError.INSUFFICIENT_DIFFERENT_CLASSES
                    )

    def _find_max_repeats(self, password: str) -> int:
        """Find maximum consecutive repeating characters."""
        if len(password) < 2:
            return 0

        max_repeat = 1
        current_repeat = 1

        for i in range(1, len(password)):
            if password[i] == password[i-1]:
                current_repeat += 1
                max_repeat = max(max_repeat, current_repeat)
            else:
                current_repeat = 1

        return max_repeat

    def _find_max_class_repeats(self, password: str) -> int:
        """Find maximum consecutive characters of same class."""
        if len(password) < 2:
            return 0

        def char_class(c):
            if c.islower():
                return 'lower'
            elif c.isupper():
                return 'upper'
            elif c.isdigit():
                return 'digit'
            else:
                return 'other'

        max_repeat = 1
        current_repeat = 1

        for i in range(1, len(password)):
            if char_class(password[i]) == char_class(password[i-1]):
                current_repeat += 1
                max_repeat = max(max_repeat, current_repeat)
            else:
                current_repeat = 1

        return max_repeat

    def _find_max_sequence(self, password: str) -> int:
        """Find maximum length of sequential characters."""
        max_seq = 0

        for sequence in self.sequences:
            # Check forward and reverse sequences
            for seq in [sequence, sequence[::-1]]:
                for i in range(len(seq) - 2):  # Minimum sequence length of 3
                    for length in range(3, len(seq) - i + 1):
                        subseq = seq[i:i+length]
                        if subseq.lower() in password.lower():
                            max_seq = max(max_seq, length)

        return max_seq

    def _is_palindrome(self, password: str) -> bool:
        """Check if password is a palindrome."""
        clean = re.sub(r'[^a-zA-Z0-9]', '', password.lower())
        return len(clean) > 3 and clean == clean[::-1]

    def _is_case_change_only(self, password: str, oldpassword: str) -> bool:
        """Check if password is only case changes of old password."""
        return password.lower() == oldpassword.lower()

    def _is_too_similar(self, password: str, oldpassword: str) -> bool:
        """Check if password is too similar to old password."""
        # Simple similarity check - more than 50% common characters
        if len(password) == 0 or len(oldpassword) == 0:
            return False

        common = sum(1 for a, b in zip(password.lower(), oldpassword.lower()) if a == b)
        similarity = common / max(len(password), len(oldpassword))

        return similarity > 0.7

    def _calculate_score(self, password: str, char_classes: Dict[str, int]) -> int:
        """Calculate password complexity score."""
        score = len(password) * 4  # Base score

        # Bonus for character variety
        if char_classes['lower'] > 0:
            score += (len(password) - char_classes['lower']) * 2
        if char_classes['upper'] > 0:
            score += (len(password) - char_classes['upper']) * 2
        if char_classes['digit'] > 0:
            score += char_classes['digit'] * 4
        if char_classes['other'] > 0:
            score += char_classes['other'] * 6

        # Penalty for common patterns
        if password.isdigit():
            score -= len(password)
        if password.isalpha():
            score -= len(password)

        return max(0, score)


# Convenience functions matching python-pwquality API
def check_password(password: str, oldpassword: Optional[str] = None,
                  user: Optional[str] = None, gecos: Optional[str] = None) -> int:
    """
    Convenience function to check password quality.

    Args:
        password: Password to check
        oldpassword: Previous password for similarity check
        user: Username for user check
        gecos: GECOS field for gecos check

    Returns:
        Password score or raises PWQError
    """
    pwq = PWQSettings()
    return pwq.check(password, oldpassword, user, gecos)


def generate_password(entropy: int = 64) -> str:
    """
    Convenience function to generate a password.

    Args:
        entropy: Desired entropy in bits

    Returns:
        Generated password
    """
    pwq = PWQSettings()
    return pwq.generate(entropy)


# Example usage
if __name__ == "__main__":
    # Create PWQSettings instance (matching real pwquality API)
    pwq = PWQSettings()

    # Configure settings
    pwq.set_option('minlen', 12)
    pwq.set_option('minclass', 3)
    pwq.set_option('maxrepeat', 2)

    # Test passwords
    test_passwords = [
        "weak",
        "password123",
        "StrongP@ssw0rd!",
        "MyS3cur3P@ssw0rd2024"
    ]

    for pwd in test_passwords:
        try:
            score = pwq.check(pwd, user="testuser")
            print(f"Password '{pwd}': Score = {score}")
        except PWQError as e:
            print(f"Password '{pwd}': FAILED - {e}")

    # Generate a strong password
    generated = pwq.generate(entropy=80)
    print(f"\nGenerated password: {generated}")

    try:
        score = pwq.check(generated)
        print(f"Generated password score: {score}")
    except PWQError as e:
        print(f"Generated password failed: {e}")