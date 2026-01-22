#!/usr/bin/env python3
"""
Quick portal field debugger - shows what fields a captive portal has.
"""

import sys
import urllib.request
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.common_modules.wifi.helpers.wifi_helpers import CaptivePortalFormParser


def debug_portal(url):
    """Debug a captive portal to see what fields it has"""

    print(f"\n{'='*60}")
    print(f"  CAPTIVE PORTAL DEBUGGER")
    print(f"{'='*60}\n")
    print(f"Fetching: {url}\n")

    try:
        # Fetch the page
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request, timeout=10)
        html_content = response.read().decode('utf-8', errors='ignore')

        # Parse forms
        parser = CaptivePortalFormParser()
        parser.feed(html_content)

        if not parser.forms:
            print("❌ No forms found on this page!\n")
            return

        print(f"✅ Found {len(parser.forms)} form(s)\n")

        # Show each form
        for i, form in enumerate(parser.forms, 1):
            print(f"{'─'*60}")
            print(f"FORM #{i}")
            print(f"{'─'*60}")
            print(f"  Action: {form['action']}")
            print(f"  Method: {form['method']}")
            print(f"\n  Fields found:")

            for field_name, field_info in form['inputs'].items():
                field_type = field_info['type']
                field_value = field_info['value']

                # Highlight likely username/password fields
                highlight = ""
                if any(x in field_name.lower() for x in ['user', 'login', 'email', 'netid']):
                    highlight = " 👤 (likely USERNAME)"
                elif any(x in field_name.lower() for x in ['pass', 'pwd']):
                    highlight = " 🔑 (likely PASSWORD)"
                elif field_type == 'hidden':
                    highlight = " 🔒 (hidden)"

                value_display = f"= '{field_value}'" if field_value else ""
                print(f"    • {field_name} ({field_type}) {value_display}{highlight}")

            print()

        # Check pattern matching
        print(f"{'─'*60}")
        print("PATTERN MATCHING TEST")
        print(f"{'─'*60}")

        username_fields = ['username', 'user', 'userid', 'login', 'email', 'netid']
        password_fields = ['password', 'pass', 'pwd']

        form = parser.forms[0]  # Test first form

        # Find username field
        username_match = None
        for field_name in form['inputs'].keys():
            if any(uf in field_name.lower() for uf in username_fields):
                username_match = field_name
                break

        # Find password field
        password_match = None
        for field_name in form['inputs'].keys():
            if any(pf in field_name.lower() for pf in password_fields):
                password_match = field_name
                break

        if username_match:
            print(f"✅ Username field matched: '{username_match}'")
        else:
            print(f"❌ No username field matched!")
            print(f"   Current patterns: {username_fields}")
            print(f"   You may need to add a new pattern.")

        if password_match:
            print(f"✅ Password field matched: '{password_match}'")
        else:
            print(f"❌ No password field matched!")
            print(f"   Current patterns: {password_fields}")
            print(f"   You may need to add a new pattern.")

        print()

    except Exception as e:
        print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_portal.py <portal_url>")
        print("\nExamples:")
        print("  python debug_portal.py http://localhost:8080/login")
        print("  python debug_portal.py http://localhost:8080/login?type=university")
        print("  python debug_portal.py https://captiveportal.example.com/login")
        sys.exit(1)

    url = sys.argv[1]
    debug_portal(url)
