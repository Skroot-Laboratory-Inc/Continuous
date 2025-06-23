# PWQuality Windows

A Windows-compatible Python interface that replicates the functionality of Ubuntu's `python-pwquality` package. This package provides comprehensive password quality checking without requiring `libpwquality` or other system dependencies.

## Features

- **Complete API Compatibility**: Drop-in replacement for Ubuntu's python-pwquality
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **No Dependencies**: Pure Python implementation with no external requirements
- **Comprehensive Checking**: All standard password quality checks including:
  - Length validation
  - Character class requirements
  - Repeat character detection
  - Sequential pattern detection
  - Dictionary/common password checking
  - Username and personal information detection
  - Palindrome detection
  - Password similarity comparison

## Installation

Install from your local package:

```bash
pip install .