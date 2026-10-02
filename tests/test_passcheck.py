# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""Tests for SentinelBlade password analysis."""

import unittest

from sentinelblade.passcheck import check_password


class PasswordCheckTests(unittest.TestCase):
    def test_common_password_is_flagged_and_capped(self) -> None:
        result = check_password("Password1")

        self.assertTrue(result["checks"]["common_password"])
        self.assertLessEqual(result["score"], 10)

    def test_strong_password_has_positive_entropy_and_no_secret_in_result(self) -> None:
        secret = "Violet!River7-Window"
        result = check_password(secret)

        self.assertGreater(result["entropy_bits_estimate"], 80)
        self.assertEqual(result["score"], 100)
        self.assertNotIn(secret, str(result))

    def test_empty_password_gets_improvement_tips(self) -> None:
        result = check_password("")

        self.assertEqual(result["length"], 0)
        self.assertTrue(result["tips"])


if __name__ == "__main__":
    unittest.main()
