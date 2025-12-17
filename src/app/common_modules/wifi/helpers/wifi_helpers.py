import logging
import platform
import re
import socket
import subprocess
import time
from typing import Dict, List, Optional


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


def connectToWifi(ssid: str, password: str = None) -> tuple[bool, str]:
    """
    Connect to a WiFi network using nmcli (Linux-only).
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
            elif password:
                subprocess.run(['sudo', 'nmcli', 'connection', 'delete', ssid],
                               capture_output=True, timeout=5, check=False)
                connection_exists = False

        if not connection_exists:
            if password:
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
    return [{'ssid': e['ssid'], 'in_use': bool(e.get('in_use', False)), 'security': e.get('security', 'Open')} for e in sorted_entries]


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

        entry = networks.get(ssid)
        if entry is None:
            networks[ssid] = {
                'ssid': ssid,
                'signal': sig_val,
                'security': security,
                'in_use': (in_use_token == '*')
            }
        else:
            if sig_val > entry['signal']:
                entry['signal'] = sig_val
            if (entry.get('security') == 'Open' or not entry.get('security')) and security != 'Open':
                entry['security'] = security
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
                networks.setdefault(ssid, {'ssid': ssid, 'signal': 0, 'security': 'Open', 'in_use': False})
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
            else:
                existing = networks[current_ssid].get('security', '')
                if not existing or existing == 'Open':
                    networks[current_ssid]['security'] = val
                elif val and val not in existing:
                    networks[current_ssid]['security'] = f"{existing}/{val}"
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