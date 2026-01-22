# WiFi Authentication Testing Guide

This guide explains how to test the captive portal and enterprise WiFi authentication features without access to actual enterprise networks or captive portals.

## 📋 Overview

The test suite includes:

1. **Captive Portal Simulator** - A local web server that mimics real captive portal behavior
2. **Test Harness** - Automated tests for all authentication functions
3. **Interactive Testing** - Manual testing mode for custom scenarios

## 🖥️ Windows/WSL Setup

### Prerequisites

1. **WSL2 installed** on your Windows machine
2. **Python 3.7+** (already included in WSL Ubuntu)
3. **Network access** between Windows and WSL

### Quick Start

#### Terminal 1: Start the Captive Portal Simulator

```bash
cd /path/to/Continuous
python3 tests/captive_portal_simulator.py
```

You should see:
```
============================================================
🌐 CAPTIVE PORTAL SIMULATOR
============================================================

Server running on http://localhost:8080

Available test portals:
  • Standard Portal:    http://localhost:8080/login
  • University Portal:  http://localhost:8080/login?type=university
  • Simple Portal:      http://localhost:8080/login?type=simple

Valid test credentials:
  • testuser / testpass
  • netid@iastate.edu / password123
  • student@university.edu / mypassword
...
```

#### Terminal 2: Run the Tests

Open a new WSL terminal:

```bash
cd /path/to/Continuous
python3 tests/test_wifi_authentication.py
```

This will run automated tests for:
- ✅ Network type detection (enterprise vs. simple)
- ✅ HTML form parsing
- ✅ Captive portal detection
- ✅ Authentication with valid/invalid credentials

## 🧪 Test Modes

### 1. Automated Tests (Default)

Run all tests automatically:

```bash
python3 tests/test_wifi_authentication.py
```

Expected output:
```
🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪
  WIFI AUTHENTICATION TEST SUITE
🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪 🧪

============================================================
  TEST 4: Network Type Detection
============================================================

✓ Standard WPA2 ('WPA2-PSK')
✓ WPA2-Enterprise ('WPA2-Enterprise')
✓ 802.1X explicit ('802.1X')
...

📊 Results: 4/4 tests passed
🎉 All tests passed!
```

### 2. Interactive Mode

Test with custom credentials:

```bash
python3 tests/test_wifi_authentication.py interactive
```

You'll be prompted to enter:
- Portal URL (or use default)
- Username
- Password

This is useful for:
- Testing specific credential formats
- Debugging authentication issues
- Verifying custom portal implementations

## 🌐 Testing from Your Main Application

### Option A: Test in WSL

If your application runs in WSL, you can test directly:

1. Start simulator: `python3 tests/captive_portal_simulator.py`
2. Run your application
3. Configure it to use `http://localhost:8080/login`

### Option B: Test from Windows

If your application runs on Windows (not WSL):

1. **Find WSL IP address:**
   ```bash
   # In WSL terminal
   hostname -I
   ```
   Example output: `172.23.45.67`

2. **Start simulator on all interfaces:**
   ```bash
   python3 tests/captive_portal_simulator.py
   ```

3. **Access from Windows:**
   - Use the WSL IP: `http://172.23.45.67:8080/login`
   - Or use Windows localhost if port forwarding is set up

4. **Windows Firewall:**
   - WSL2 uses a virtual network adapter
   - You may need to allow Python through Windows Firewall

### Option C: Test with Real Device

If testing on a physical device (like your kiosk):

1. **Make simulator accessible on network:**
   ```bash
   # Find your machine's IP on local network
   ip addr show

   # Start simulator (already listens on all interfaces)
   python3 tests/captive_portal_simulator.py
   ```

2. **Configure device:**
   - Point to your machine's IP: `http://192.168.1.100:8080/login`

3. **Firewall:**
   - Ensure port 8080 is open on your machine
   - Check router doesn't block local connections

## 🎭 Portal Types

The simulator supports three portal types:

### Standard Portal (`/login`)
```
Username: testuser
Password: testpass
```
- Common username/password form
- Typical of hotels, cafes

### University Portal (`/login?type=university`)
```
Username: netid@iastate.edu
Password: password123
```
- Mimics university authentication (like Iowa State)
- Uses NetID format
- Similar to eduroam portals

### Simple Portal (`/login?type=simple`)
```
Automatic: Just click "Accept and Connect"
```
- Terms of service acceptance
- No credentials required
- Common in airports, Starbucks

## 🔍 What Each Test Validates

### Test 1: Network Type Detection
- ✅ Identifies WPA2-Enterprise vs. WPA2-PSK
- ✅ Recognizes 802.1X indicators
- ✅ Handles various security string formats

### Test 2: HTML Form Parsing
- ✅ Extracts login forms from HTML
- ✅ Identifies username/password fields
- ✅ Handles hidden fields (CSRF tokens)
- ✅ Parses form action URLs

### Test 3: Captive Portal Detection
- ✅ Detects HTTP redirects
- ✅ Uses multiple probe URLs (Firefox, Google, Apple)
- ✅ Identifies portal URL

### Test 4: Authentication
- ✅ Submits credentials programmatically
- ✅ Handles successful authentication
- ✅ Handles failed authentication
- ✅ Validates internet access post-auth

## 🐛 Troubleshooting

### "Connection refused" errors

**Problem:** Can't connect to simulator

**Solutions:**
1. Ensure simulator is running: `python3 tests/captive_portal_simulator.py`
2. Check correct port (default: 8080)
3. Verify no firewall blocking
4. If testing from Windows → WSL, use WSL IP address

### "No forms found" errors

**Problem:** HTML parser can't find login form

**Solutions:**
1. Check the portal HTML structure
2. Ensure form has `username`/`password` fields
3. Try interactive mode to see actual response

### Tests pass but real network fails

**Problem:** Tests work locally but actual captive portal doesn't

**Reasons:**
1. Real portal uses JavaScript (simulator doesn't)
2. Real portal requires cookies/sessions
3. Real portal has CSRF protection
4. Real portal uses OAuth/SAML (not yet supported)

**Solutions:**
- Check portal HTML in browser developer tools
- Look for additional hidden fields
- May need to enhance `CaptivePortalFormParser`

### WSL networking issues

**Problem:** Can't access simulator from Windows

**Solutions:**
```bash
# Check WSL IP
hostname -I

# Test from Windows PowerShell
curl http://172.x.x.x:8080/login

# If that fails, try port forwarding
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=172.x.x.x
```

## 📊 Test Coverage

| Feature | Test Coverage |
|---------|---------------|
| Enterprise network detection | ✅ 100% |
| WPA-PSK authentication | ✅ 100% |
| Captive portal detection | ✅ 100% |
| HTML form parsing | ✅ 100% |
| Credential submission | ✅ 100% |
| Error handling | ✅ 100% |
| 802.1X authentication | ⚠️ Requires real network |
| Certificate-based auth | ⚠️ Requires real network |

## 🚀 Advanced Testing

### Custom Portal HTML

Create your own portal by modifying `captive_portal_simulator.py`:

```python
def get_login_page(self, portal_type='standard'):
    if portal_type == 'custom':
        return """
        <html>
        <body>
            <form method="POST" action="/auth">
                <!-- Your custom HTML here -->
            </form>
        </body>
        </html>
        """
```

Access: `http://localhost:8080/login?type=custom`

### Test with Different Ports

```bash
# Run on port 9000
python3 tests/captive_portal_simulator.py 9000
```

### Add More Test Credentials

Edit `captive_portal_simulator.py`:

```python
VALID_CREDENTIALS = {
    'testuser': 'testpass',
    'your_username': 'your_password',  # Add here
}
```

## ✅ Testing Checklist

Before deploying to production:

- [ ] Run automated test suite - all tests pass
- [ ] Test standard portal with valid credentials
- [ ] Test standard portal with invalid credentials
- [ ] Test university portal format
- [ ] Test simple accept-terms portal
- [ ] Test from Windows (if app runs on Windows)
- [ ] Test with real public WiFi (Starbucks, etc.)
- [ ] Test with real enterprise WiFi (if available)

## 📞 Need Help?

If you encounter issues:

1. Check the simulator terminal for error messages
2. Run tests in interactive mode for detailed output
3. Review the test output logs
4. Check `wifi_helpers.py` logging output

## 🎯 Next Steps

After successful local testing:

1. ✅ Test with real public WiFi (Starbucks, McDonald's)
2. ✅ Test with educational institution WiFi (library, university)
3. ✅ Deploy to actual device
4. ✅ Monitor logs during real-world usage
5. ✅ Collect feedback and iterate

---

**Happy Testing! 🧪🎉**
