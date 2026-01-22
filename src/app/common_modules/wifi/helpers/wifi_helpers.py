import logging
import platform
import re
import socket
import subprocess
import time
import urllib.request
import urllib.parse
import urllib.error
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple


def getWifiNetworks() -> List[Dict]:
    """
    Public function returning list of { 'ssid', 'in_use', 'security' } sorted by signal.
    """
    try:
        system = platform.system()
        if system == "Linux":
            return get_linux_networks()
        elif system == "Windows":
            return get_windows_networks()
        else:
            return []
    except Exception:
        logging.exception("Unexpected error getting WiFi networks", extra={"id": "Network"})
        return []


def checkInternetConnection(timeout=3) -> bool:
    """
    Check if the device has an active internet connection.
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except (OSError, socket.timeout):
        return False


def connectToWifi(ssid: str, password: str = None, username: str = None, auth_method: str = None) -> tuple[bool, str]:
    """
    Connect to a WiFi network using nmcli (Linux-only).
    Supports both simple WPA-PSK and enterprise 802.1X authentication.

    Args:
        ssid: Network SSID
        password: Password for WPA-PSK or enterprise authentication
        username: Username for enterprise authentication (optional)
        auth_method: Authentication method for enterprise networks (e.g., 'peap', 'ttls', 'tls')
    """
    if platform.system() != "Linux":
        return False, "WiFi connection only supported on Linux"

    try:
        check_result = subprocess.run(
            ['nmcli', '-t', '-f', 'NAME', 'connection', 'show'],
            capture_output=True, text=True, check=True, timeout=5
        )
        saved_connections = check_result.stdout.strip().split('\n')
        connection_exists = ssid in saved_connections

        if connection_exists:
            result = subprocess.run(
                ['sudo', 'nmcli', 'connection', 'up', ssid],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return True, f"Connected to {ssid}"
            elif password or username:
                subprocess.run(['sudo', 'nmcli', 'connection', 'delete', ssid],
                               capture_output=True, timeout=5, check=False)
                connection_exists = False

        if not connection_exists:
            # If username is provided, it's an enterprise network
            if username and auth_method:
                return connectToEnterpriseWifi(ssid, username, password, auth_method)
            elif password:
                result = subprocess.run(
                    ['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid, 'password', password],
                    capture_output=True, text=True, timeout=30
                )
            else:
                result = subprocess.run(
                    ['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid],
                    capture_output=True, text=True, timeout=30
                )

            if result.returncode == 0:
                # Check for captive portal after successful connection
                time.sleep(2)  # Wait for network to stabilize
                is_captive, portal_url = detectCaptivePortal(timeout=5)

                if is_captive and portal_url and username and password:
                    # Attempt to authenticate with captive portal
                    portal_success, portal_msg = authenticateCaptivePortal(portal_url, username, password)
                    if portal_success:
                        return True, f"Connected to {ssid} and authenticated with captive portal"
                    else:
                        return True, f"Connected to {ssid} but captive portal auth failed: {portal_msg}"
                elif is_captive:
                    return True, f"Connected to {ssid} but captive portal detected (credentials needed)"

                return True, f"Successfully connected to {ssid}"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Connection failed"
                return False, error_msg

    except subprocess.TimeoutExpired:
        return False, "Connection timeout - please try again"
    except subprocess.CalledProcessError as e:
        return False, f"Error connecting to network: {str(e)}"
    except Exception:
        logging.exception("Unexpected error connecting to WiFi", extra={"id": "Network"})
        return False, "Unexpected error"


def connectToEnterpriseWifi(ssid: str, username: str, password: str, auth_method: str = 'peap') -> tuple[bool, str]:
    """
    Connect to an enterprise WiFi network with 802.1X authentication.

    Args:
        ssid: Network SSID
        username: Username for authentication
        password: Password for authentication
        auth_method: Authentication method ('peap', 'ttls', 'tls', 'pwd', 'fast')

    Returns:
        Tuple of (success: bool, message: str)
    """
    if platform.system() != "Linux":
        return False, "WiFi connection only supported on Linux"

    # Map friendly names to nmcli auth methods
    auth_map = {
        'peap': 'peap',
        'ttls': 'ttls',
        'tls': 'tls',
        'pwd': 'pwd',
        'fast': 'fast',
        'leap': 'leap'
    }

    eap_method = auth_map.get(auth_method.lower(), 'peap')

    # For PEAP and TTLS, we typically use MSCHAPv2 as phase2 auth
    phase2_map = {
        'peap': 'mschapv2',
        'ttls': 'mschapv2',
        'fast': 'mschapv2'
    }

    try:
        # Delete existing connection if it exists
        subprocess.run(
            ['sudo', 'nmcli', 'connection', 'delete', ssid],
            capture_output=True, timeout=5, check=False
        )

        # Build the nmcli command for enterprise WiFi
        cmd = [
            'sudo', 'nmcli', 'connection', 'add',
            'type', 'wifi',
            'con-name', ssid,
            'ssid', ssid,
            'wifi-sec.key-mgmt', 'wpa-eap',
            '802-1x.eap', eap_method,
            '802-1x.identity', username,
            '802-1x.password', password
        ]

        # Add phase2 authentication for methods that need it
        if eap_method in phase2_map:
            cmd.extend(['802-1x.phase2-auth', phase2_map[eap_method]])

        # Create the connection
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Failed to create connection profile"
            logging.error(f"Failed to create enterprise connection: {error_msg}")
            return False, f"Failed to create connection: {error_msg}"

        # Activate the connection
        activate_result = subprocess.run(
            ['sudo', 'nmcli', 'connection', 'up', ssid],
            capture_output=True, text=True, timeout=30
        )

        if activate_result.returncode == 0:
            # Check for captive portal after successful 802.1X connection
            time.sleep(2)  # Wait for network to stabilize
            is_captive, portal_url = detectCaptivePortal(timeout=5)

            if is_captive and portal_url:
                # Attempt to authenticate with captive portal using the same credentials
                portal_success, portal_msg = authenticateCaptivePortal(portal_url, username, password)
                if portal_success:
                    return True, f"Connected to {ssid} and authenticated with captive portal"
                else:
                    return True, f"Connected to {ssid} but captive portal auth failed: {portal_msg}"

            return True, f"Successfully connected to {ssid}"
        else:
            error_msg = activate_result.stderr.strip() if activate_result.stderr else "Connection failed"
            # Try to extract more useful error message
            if "802-1x" in error_msg.lower() or "authentication" in error_msg.lower():
                return False, "Authentication failed - check username and password"
            return False, error_msg

    except subprocess.TimeoutExpired:
        return False, "Connection timeout - please try again"
    except Exception:
        logging.exception("Unexpected error connecting to enterprise WiFi", extra={"id": "Network"})
        return False, "Unexpected error"


def disconnectWifi() -> tuple[bool, str]:
    """
    Disconnect from current WiFi network (Linux-only).
    """
    if platform.system() != "Linux":
        return False, "WiFi disconnection only supported on Linux"

    try:
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
            capture_output=True, text=True, check=True, timeout=5
        )

        for line in result.stdout.strip().split('\n'):
            parts = line.split(':')
            if len(parts) >= 2 and '802-11-wireless' in parts[1]:
                connection_name = parts[0]
                disconnect_result = subprocess.run(
                    ['sudo', 'nmcli', 'connection', 'down', connection_name],
                    capture_output=True, text=True, timeout=10
                )
                if disconnect_result.returncode == 0:
                    return True, f"Disconnected from {connection_name}"
                else:
                    return False, "Failed to disconnect"

        return False, "No active WiFi connection found"
    except Exception:
        logging.exception("Error disconnecting from WiFi", extra={"id": "Network"})
        return False, "Error"


class CaptivePortalFormParser(HTMLParser):
    """
    HTML parser to extract login form details from captive portal pages.
    """
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current_form = None
        self.current_input = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'form':
            self.current_form = {
                'action': attrs_dict.get('action', ''),
                'method': attrs_dict.get('method', 'post').lower(),
                'inputs': {}
            }
        elif tag == 'input' and self.current_form is not None:
            input_name = attrs_dict.get('name', '')
            input_type = attrs_dict.get('type', 'text').lower()
            input_value = attrs_dict.get('value', '')

            if input_name:
                self.current_form['inputs'][input_name] = {
                    'type': input_type,
                    'value': input_value
                }

    def handle_endtag(self, tag):
        if tag == 'form' and self.current_form is not None:
            self.forms.append(self.current_form)
            self.current_form = None


def detectCaptivePortal(timeout: int = 5) -> Tuple[bool, Optional[str]]:
    """
    Detect if there's a captive portal by checking for HTTP redirects.

    Returns:
        Tuple of (is_captive_portal: bool, portal_url: Optional[str])
    """
    # Common URLs used for captive portal detection
    test_urls = [
        'http://detectportal.firefox.com/success.txt',
        'http://www.gstatic.com/generate_204',
        'http://captive.apple.com/hotspot-detect.html',
        'http://connectivitycheck.gstatic.com/generate_204'
    ]

    for test_url in test_urls:
        try:
            request = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(request, timeout=timeout)

            # Check if we got redirected
            final_url = response.geturl()
            status_code = response.getcode()

            # If redirected to a different domain, it's likely a captive portal
            if final_url != test_url and status_code in [200, 302, 303, 307]:
                logging.info(f"Captive portal detected: {final_url}")
                return True, final_url

            # Some portals return 200 but with different content
            if test_url.endswith('generate_204') and status_code != 204:
                return True, final_url

        except urllib.error.HTTPError as e:
            # 302/303 redirects might throw HTTPError
            if e.code in [302, 303, 307]:
                redirect_url = e.headers.get('Location', '')
                if redirect_url:
                    logging.info(f"Captive portal detected via redirect: {redirect_url}")
                    return True, redirect_url
        except (urllib.error.URLError, socket.timeout):
            continue
        except Exception as e:
            logging.debug(f"Error checking captive portal with {test_url}: {e}")
            continue

    return False, None


def authenticateCaptivePortal(portal_url: str, username: str, password: str) -> Tuple[bool, str]:
    """
    Attempt to authenticate with a captive portal programmatically.

    Args:
        portal_url: The captive portal login page URL
        username: Username for authentication
        password: Password for authentication

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Fetch the login page
        request = urllib.request.Request(portal_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request, timeout=10)
        html_content = response.read().decode('utf-8', errors='ignore')

        # Parse the HTML to find login forms
        parser = CaptivePortalFormParser()
        parser.feed(html_content)

        if not parser.forms:
            return False, "No login form found on captive portal page"

        # Use the first form found (usually the login form)
        form = parser.forms[0]

        # Debug: Log form fields found
        field_names = list(form['inputs'].keys())
        logging.info(f"Captive portal form fields found: {field_names}", extra={"id": "Network"})
        logging.debug(f"Form details - Action: {form['action']}, Method: {form['method']}, Fields: {form['inputs']}", extra={"id": "Network"})

        # Build the form action URL
        if form['action'].startswith('http'):
            action_url = form['action']
        elif form['action'].startswith('/'):
            parsed = urllib.parse.urlparse(portal_url)
            action_url = f"{parsed.scheme}://{parsed.netloc}{form['action']}"
        else:
            action_url = urllib.parse.urljoin(portal_url, form['action'])

        # Prepare form data - try common field names for username/password
        form_data = {}
        username_fields = ['username', 'user', 'userid', 'login', 'email', 'netid']
        password_fields = ['password', 'pass', 'pwd']

        # Copy existing hidden fields and values
        for field_name, field_info in form['inputs'].items():
            if field_info['type'] in ['hidden', 'submit']:
                form_data[field_name] = field_info['value']

        # Find and set username field
        username_set = False
        matched_username_field = None
        for field_name in form['inputs'].keys():
            if any(uf in field_name.lower() for uf in username_fields):
                form_data[field_name] = username
                username_set = True
                matched_username_field = field_name
                break

        # Find and set password field
        password_set = False
        matched_password_field = None
        for field_name in form['inputs'].keys():
            if any(pf in field_name.lower() for pf in password_fields):
                form_data[field_name] = password
                password_set = True
                matched_password_field = field_name
                break

        # Debug: Log field matching results
        if username_set and password_set:
            logging.info(f"Matched fields - Username: '{matched_username_field}', Password: '{matched_password_field}'", extra={"id": "Network"})
        else:
            logging.warning(f"Field matching failed - Username set: {username_set}, Password set: {password_set}", extra={"id": "Network"})
            logging.warning(f"Available fields: {field_names}", extra={"id": "Network"})

        if not username_set or not password_set:
            return False, "Could not identify username/password fields in login form"

        # Submit the form
        encoded_data = urllib.parse.urlencode(form_data).encode('utf-8')
        submit_request = urllib.request.Request(
            action_url,
            data=encoded_data,
            headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
        )

        submit_response = urllib.request.urlopen(submit_request, timeout=10)

        # Wait a moment for authentication to complete
        time.sleep(2)

        # Check if we now have internet access
        has_internet = checkInternetConnection(timeout=3)

        if has_internet:
            return True, "Successfully authenticated with captive portal"
        else:
            return False, "Captive portal form submitted but internet access not confirmed"

    except urllib.error.HTTPError as e:
        logging.error(f"HTTP error during captive portal auth: {e.code} - {e.reason}")
        return False, f"Authentication failed: HTTP {e.code}"
    except urllib.error.URLError as e:
        logging.error(f"URL error during captive portal auth: {e.reason}")
        return False, "Could not connect to captive portal"
    except Exception as e:
        logging.exception("Unexpected error during captive portal authentication", extra={"id": "Network"})
        return False, f"Authentication error: {str(e)}"


def checkAndAuthenticateCaptivePortal(username: str = None, password: str = None) -> Tuple[bool, str]:
    """
    Check if connected to a captive portal and attempt authentication if credentials provided.

    Args:
        username: Username for authentication (optional)
        password: Password for authentication (optional)

    Returns:
        Tuple of (needs_auth: bool, message: str)
    """
    # First check if we already have internet
    if checkInternetConnection(timeout=3):
        return False, "Already have internet access"

    # Check for captive portal
    is_captive, portal_url = detectCaptivePortal(timeout=5)

    if not is_captive:
        return False, "No captive portal detected but no internet access"

    if not username or not password:
        return True, f"Captive portal detected at {portal_url} - credentials required"

    # Attempt authentication
    success, message = authenticateCaptivePortal(portal_url, username, password)
    return success, message


def sortNetworks(networks_map: Dict[str, Dict]) -> List[Dict]:
    sorted_entries = sorted(
        networks_map.values(),
        key=lambda x: int(x['signal']) if isinstance(x['signal'], int) or str(x['signal']).isdigit() else 0,
        reverse=True
    )
    sorted_entries = sorted(
        sorted_entries,
        key=lambda x: not x.get('in_use', False)
    )
    return [{
        'ssid': e['ssid'],
        'in_use': bool(e.get('in_use', False)),
        'security': e.get('security', 'Open'),
        'is_enterprise': e.get('is_enterprise', False)
    } for e in sorted_entries]


def run_cmd(cmd: List[str], timeout: int = 10, check: bool = True) -> Optional[str]:
    """
    Run a subprocess command and return stdout, or None on error.
    """
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=check)
        return res.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logging.debug("Command failed: %s -> %s", cmd, e)
        return None
    except Exception:
        logging.exception("Unexpected error running command", extra={"cmd": cmd})
        return None


def is_enterprise_network(security: str) -> bool:
    """
    Determine if a network uses enterprise authentication (802.1X).
    """
    if not security or security == 'Open':
        return False
    security_lower = security.lower()
    # Check for 802.1X indicators
    enterprise_indicators = ['802.1x', '802-1x', 'enterprise', 'eap', 'wpa2-eap', 'wpa-eap']
    return any(indicator in security_lower for indicator in enterprise_indicators)


def parse_nmcli_lines(lines: List[str]) -> Dict[str, Dict]:
    """
    Parse nmcli -t -f SSID,SIGNAL,SECURITY,IN-USE lines.
    Aggregate by SSID, keep highest signal, prefer non-Open security, preserve in-use.
    """
    networks: Dict[str, Dict] = {}
    for line in lines:
        if not line:
            continue
        parts = line.rsplit(':', 3)
        if len(parts) < 4:
            continue

        ssid = parts[0].strip()
        signal_str = parts[1].strip()
        security = parts[2].strip() or 'Open'
        in_use_token = parts[3].strip()

        try:
            sig_val = int(signal_str)
        except ValueError:
            sig_val = 0

        if not ssid:
            continue

        is_enterprise = is_enterprise_network(security)

        entry = networks.get(ssid)
        if entry is None:
            networks[ssid] = {
                'ssid': ssid,
                'signal': sig_val,
                'security': security,
                'in_use': (in_use_token == '*'),
                'is_enterprise': is_enterprise
            }
        else:
            if sig_val > entry['signal']:
                entry['signal'] = sig_val
            if (entry.get('security') == 'Open' or not entry.get('security')) and security != 'Open':
                entry['security'] = security
                entry['is_enterprise'] = is_enterprise
            if in_use_token == '*':
                entry['in_use'] = True
    return networks


def get_linux_networks() -> List[Dict]:
    """
    Run nmcli, parse output and return sorted list of { 'ssid', 'in_use', 'security' }.
    """
    subprocess.run(['sudo', 'nmcli', 'device', 'wifi', 'rescan'],
                   capture_output=True, timeout=5, check=False)
    time.sleep(1)

    out = run_cmd(['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,IN-USE', 'device', 'wifi', 'list'], timeout=10, check=True)
    if not out:
        return []

    networks_map = parse_nmcli_lines(out.strip().splitlines())
    return sortNetworks(networks_map)


def parse_netsh_lines(lines: List[str]) -> Dict[str, Dict]:
    """
    Parse `netsh wlan show networks mode=bssid` output into a mapping per SSID.
    """
    networks: Dict[str, Dict] = {}
    current_ssid: Optional[str] = None

    ssid_re = re.compile(r'^\s*SSID\s*\d*\s*:\s*(.*)$', re.I)
    signal_re = re.compile(r'^\s*Signal\s*:\s*(\d+)\s*%?', re.I)
    auth_enc_re = re.compile(r'^\s*(Authentication|Encryption|Auth)\s*:\s*(.+)$', re.I)

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        m = ssid_re.match(line)
        if m:
            ssid = m.group(1).strip()
            if ssid:
                current_ssid = ssid
                networks.setdefault(ssid, {'ssid': ssid, 'signal': 0, 'security': 'Open', 'in_use': False, 'is_enterprise': False})
            else:
                current_ssid = None
            continue

        if not current_ssid:
            continue

        m = signal_re.match(line)
        if m:
            try:
                sig_val = int(m.group(1))
            except ValueError:
                sig_val = 0
            networks[current_ssid]['signal'] = max(networks[current_ssid]['signal'], sig_val)
            continue

        m = auth_enc_re.match(line)
        if m:
            val = m.group(2).strip()
            if 'open' in val.lower():
                networks[current_ssid]['security'] = 'Open'
                networks[current_ssid]['is_enterprise'] = False
            else:
                existing = networks[current_ssid].get('security', '')
                if not existing or existing == 'Open':
                    networks[current_ssid]['security'] = val
                elif val and val not in existing:
                    networks[current_ssid]['security'] = f"{existing}/{val}"
                # Check if it's an enterprise network
                networks[current_ssid]['is_enterprise'] = is_enterprise_network(val)
            continue

    return networks


def get_windows_networks() -> List[Dict]:
    """
    Run netsh commands, parse networks and interfaces, return sorted list of { 'ssid', 'in_use', 'security' }.
    """
    out = run_cmd(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], timeout=10, check=True)
    if not out:
        return []

    networks_map = parse_netsh_lines(out.splitlines())

    # determine currently connected SSID
    iface_out = run_cmd(['netsh', 'wlan', 'show', 'interfaces'], timeout=5, check=True)
    if iface_out:
        iface_ssid_re = re.compile(r'^\s*SSID\s*:\s*(.*)$', re.I)
        for raw in iface_out.splitlines():
            if not raw:
                continue
            if raw.strip().lower().startswith('bssid'):
                continue
            m = iface_ssid_re.match(raw)
            if m:
                connected = m.group(1).strip()
                if connected and connected in networks_map:
                    networks_map[connected]['in_use'] = True
                break
    return sortNetworks(networks_map)