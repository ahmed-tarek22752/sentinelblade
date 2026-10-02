<p align="center">
  <img src="assets/logo.svg" alt="SentinelBlade logo" width="700"/>
</p>
# SentinelBlade

**Forge your defense.** SentinelBlade is a small, defensive command-line toolkit for file verification, integrity monitoring, authorized TCP port checks, and password-strength feedback. It is written for Python 3.10+ and uses only the Python standard library at runtime.

## Features

- SHA-256, SHA-512, and MD5 file digests with optional verification.
- SHA-256 file integrity baselines with NEW, MODIFIED, and DELETED detection.
- Concurrent TCP checks with a timeout, common service names, and an authorization guard for non-local targets.
- Hidden-input password analysis with a built-in common-password list, an entropy estimate, a score, and improvement tips.
- Timestamped JSON and TXT exports.
- Cross-platform terminal colors with a plain-text fallback.

## Installation

Use Python 3.10 or newer. No runtime dependencies need to be installed.

```bash
python -m sentinelblade --help
```

To install the `sentinelblade` console command in editable mode:

```bash
python -m pip install -e .
sentinelblade --help
```

## Usage

```bash
# Hash a file; SHA-256 is the default
python -m sentinelblade hash myfile.txt

# Select an algorithm and verify an expected digest
python -m sentinelblade hash myfile.txt --algorithm sha512 --verify EXPECTED_DIGEST

# Create or check a baseline (baseline.json is stored in the monitored folder)
python -m sentinelblade monitor baseline ./myfolder
python -m sentinelblade monitor check ./myfolder

# Check localhost; ranges are inclusive
python -m sentinelblade ports 127.0.0.1 --range 1-1024

# A non-local target requires an explicit authorization acknowledgment
python -m sentinelblade ports 192.0.2.10 --range 80-443 --authorized

# Enter the password at a hidden prompt; the password is not printed or included in output
python -m sentinelblade passcheck

# Export the result of any command as timestamped JSON or TXT
python -m sentinelblade hash myfile.txt --output report.json
python -m sentinelblade monitor check ./myfolder --output integrity.txt
python -m sentinelblade ports 127.0.0.1 --range 1-128 --output ports.json
python -m sentinelblade passcheck --output password.txt

# Convert a saved JSON result into another timestamped report
python -m sentinelblade report --input report.json --output report.txt

# Show version and author attribution
python -m sentinelblade --version
```

The port scanner prints: “Only scan systems you own or have written permission to test.” The `--authorized` option records your explicit acknowledgment; it cannot verify ownership or permission on your behalf.

## Ethical Use

Use SentinelBlade only on systems and files you own or are explicitly authorized to assess. Port scanning without permission may violate laws, policies, or service terms. The user is responsible for obtaining authorization and complying with applicable requirements. SentinelBlade is provided for defensive and educational use.

## License

SentinelBlade is distributed under the MIT License. See [LICENSE](LICENSE).
