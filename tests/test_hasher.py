# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""Tests for SentinelBlade file hashing."""

import hashlib
import tempfile
import unittest
from pathlib import Path

from sentinelblade.hasher import hash_file


class HashFileTests(unittest.TestCase):
    def test_hashes_file_with_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.bin"
            file_path.write_bytes(b"sentinel")
            result = hash_file(file_path)

        self.assertEqual(result["algorithm"], "sha256")
        self.assertEqual(result["digest"], hashlib.sha256(b"sentinel").hexdigest())

    def test_verifies_digest_case_insensitively(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.txt"
            file_path.write_text("data", encoding="utf-8")
            expected = hashlib.sha512(b"data").hexdigest().upper()
            result = hash_file(file_path, "sha512", expected)

        self.assertTrue(result["verified"])

    def test_rejects_unsupported_algorithm(self) -> None:
        with self.assertRaises(ValueError):
            hash_file("missing", "sha1")


if __name__ == "__main__":
    unittest.main()
