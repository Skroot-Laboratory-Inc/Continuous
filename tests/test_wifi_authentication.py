#!/usr/bin/env python3
"""
WiFi Authentication Test Harness
Tests captive portal detection and authentication functions.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import the wifi helpers
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.common_modules.wifi.helpers.wifi_helpers import (
    detectCaptivePortal,
    authenticateCaptivePortal,
    checkAndAuthenticateCaptivePortal
)


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_test(name, status, message=""):
    """Print test result"""
    symbol = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"  # Green or Red
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} {name}")
    if message:
        print(f"  └─ {message}")


def test_captive_portal_detection():
    """Test 1: Captive Portal Detection"""
    print_header("TEST 1: Captive Portal Detection")

    print("\nNOTE: Make sure the captive portal simulator is running!")
    print("Run: python tests/captive_portal_simulator.py\n")

    input("Press Enter when simulator is ready...")

    print("\n🔍 Testing captive portal detection...\n")

    # Test with localhost portal
    is_captive, portal_url = detectCaptivePortal(timeout=5)

    if is_captive:
        print_test("Captive portal detected", True, f"URL: {portal_url}")
        return True, portal_url
    else:
        print_test("Captive portal detected", False, "No portal found - ensure simulator is running")
        return False, None


def test_captive_portal_authentication(portal_url):
    """Test 2: Captive Portal Authentication"""
    print_header("TEST 2: Captive Portal Authentication")

    if not portal_url:
        portal_url = "http://localhost:8080/login"
        print(f"\n⚠ Using default portal URL: {portal_url}\n")

    # Test cases
    test_cases = [
        ("testuser", "testpass", True, "Valid standard credentials"),
        ("netid@iastate.edu", "password123", True, "Valid university credentials"),
        ("wronguser", "wrongpass", False, "Invalid credentials"),
    ]

    results = []
    for username, password, should_succeed, description in test_cases:
        print(f"\n🧪 Testing: {description}")
        print(f"   Username: {username}, Password: {'*' * len(password)}")

        success, message = authenticateCaptivePortal(portal_url, username, password)

        expected_result = success == should_succeed
        print_test(f"Authentication {description}", expected_result, message)
        results.append(expected_result)

    return all(results)


def test_form_parsing():
    """Test 3: HTML Form Parsing"""
    print_header("TEST 3: HTML Form Parser")

    from src.app.common_modules.wifi.helpers.wifi_helpers import CaptivePortalFormParser

    # Sample HTML with login form
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <form method="POST" action="/login">
            <input type="hidden" name="csrf_token" value="abc123">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <input type="submit" value="Login">
        </form>
    </body>
    </html>
    """

    parser = CaptivePortalFormParser()
    parser.feed(html)

    print("\n🔍 Parsing sample login form...\n")

    if len(parser.forms) > 0:
        form = parser.forms[0]
        print_test("Form found", True, f"Action: {form['action']}, Method: {form['method']}")

        has_username = 'username' in form['inputs']
        print_test("Username field detected", has_username)

        has_password = 'password' in form['inputs']
        print_test("Password field detected", has_password)

        has_csrf = 'csrf_token' in form['inputs']
        print_test("Hidden CSRF token detected", has_csrf)

        return has_username and has_password
    else:
        print_test("Form found", False, "No forms parsed")
        return False


def test_network_type_detection():
    """Test 4: Network Type Detection"""
    print_header("TEST 4: Network Type Detection")

    from src.app.common_modules.wifi.helpers.wifi_helpers import is_enterprise_network

    test_cases = [
        ("WPA2-PSK", False, "Standard WPA2"),
        ("WPA2-Enterprise", True, "WPA2-Enterprise"),
        ("802.1X", True, "802.1X explicit"),
        ("WPA-EAP", True, "WPA-EAP"),
        ("Open", False, "Open network"),
        ("", False, "Empty security"),
    ]

    print("\n🔍 Testing enterprise network detection...\n")

    results = []
    for security, expected, description in test_cases:
        is_enterprise = is_enterprise_network(security)
        matches = is_enterprise == expected
        print_test(f"{description} ('{security}')", matches,
                   f"Detected as: {'Enterprise' if is_enterprise else 'Simple'}")
        results.append(matches)

    return all(results)


def interactive_test():
    """Interactive test with live simulator"""
    print_header("INTERACTIVE TEST MODE")

    print("\n📝 This will test authentication against the running simulator.")
    print("You can enter custom credentials to test.\n")

    portal_url = input("Portal URL [http://localhost:8080/login]: ").strip()
    if not portal_url:
        portal_url = "http://localhost:8080/login"

    username = input("Username [testuser]: ").strip()
    if not username:
        username = "testuser"

    password = input("Password [testpass]: ").strip()
    if not password:
        password = "testpass"

    print(f"\n🔐 Attempting authentication...")
    print(f"   Portal: {portal_url}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}\n")

    success, message = authenticateCaptivePortal(portal_url, username, password)

    print_test("Authentication", success, message)


def run_all_tests():
    """Run all automated tests"""
    print("\n" + "🧪 " * 20)
    print("  WIFI AUTHENTICATION TEST SUITE")
    print("🧪 " * 20)

    print("\n⚠️  PREREQUISITES:")
    print("  1. Run the captive portal simulator in another terminal:")
    print("     python tests/captive_portal_simulator.py")
    print("  2. Keep it running during the tests\n")

    input("Press Enter to start tests...")

    # Test 4: Network Type Detection (doesn't need simulator)
    test4_result = test_network_type_detection()

    # Test 3: Form Parsing (doesn't need simulator)
    test3_result = test_form_parsing()

    # Test 1: Detection (needs simulator)
    test1_result, portal_url = test_captive_portal_detection()

    # Test 2: Authentication (needs simulator)
    test2_result = False
    if test1_result:
        test2_result = test_captive_portal_authentication(portal_url)
    else:
        print_header("TEST 2: Captive Portal Authentication")
        print("\n⚠️  Skipped - simulator not detected\n")

    # Summary
    print_header("TEST SUMMARY")
    results = [
        ("Network Type Detection", test4_result),
        ("HTML Form Parsing", test3_result),
        ("Captive Portal Detection", test1_result),
        ("Captive Portal Authentication", test2_result),
    ]

    print()
    for name, result in results:
        print_test(name, result)

    total = len(results)
    passed = sum(1 for _, r in results if r)

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        run_all_tests()
        print("\n💡 Tip: Run 'python tests/test_wifi_authentication.py interactive'")
        print("   for interactive testing mode.\n")


if __name__ == "__main__":
    main()
