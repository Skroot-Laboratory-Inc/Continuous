# Skroot Desktop Application

Python 3.11 Tkinter GUI application for Skroot SIB (Sample Incubation Bioreactor) hardware. Takes scans, analyzes data, and plots results for visualization.

## Architecture

The app supports 5 product variants through a shared codebase:

| UseCase | Theme |
|---------|-------|
| Manufacturing (Continuous) | Wilson-Wolf |
| FlowCell | IBI |
| SkrootFlowCell | Skroot |
| Tunair | IBI |
| RollerBottle | Skroot |

- **`src/app/use_case/`** — Product-specific implementations (SIB, KPI forms, algorithms)
- **`src/app/common_modules/`** — Shared functionality (auth, AWS, threading, WiFi)
- **`src/app/ui_manager/`** — Tkinter UI framework and theme system
- **`src/app/widget/`** — Reusable UI components
- **`src/app/reader/`** — Hardware reading, analysis, and algorithms
- **`src/app/helper_methods/`** — Utilities, models, custom exceptions
- **`src/app/properties/`** — Configuration constants
- **`src/resources/`** — Static assets, scripts, version management, bundled packages

Product selection is stored in `/etc/skroot/device_config.json` and the `UseCase` enum in `src/resources/version/version.py` drives theme mapping and product behavior.

## Code Style

- **Methods/functions:** camelCase (e.g., `takeScan`, `uploadFile`, `checkAndSendConfiguration`)
- **Files/modules:** snake_case (e.g., `session_manager.py`, `generic_button.py`)
- **Classes:** PascalCase (e.g., `CommonModules`, `BaseSib`, `RootManager`)
- **Constants:** SCREAMING_SNAKE_CASE in Enum classes
- **Indentation:** 4 spaces
- **Type hints:** Used selectively — prioritize parameter annotations over return types

## Error Handling & Logging

**Never let exceptions propagate and crash the UI.** All exception-prone code must be wrapped in try/except with proper logging.

All logging calls **must** include `extra={"id": "<category>"}`. The `id` field is part of the log format (`%(id)s` in `src/app/widget/logger.py`) and omitting it will crash the logger.

```python
# Correct
try:
    result = someOperation()
except Exception:
    logging.exception("Failed to perform operation", extra={"id": "Reader"})

# WRONG - missing extra id, will crash
logging.exception("Failed to perform operation")
```

Common `id` categories: `"global"`, `"Sib"`, `"Reader"`, `"System failure"`, `"UI failure"`, `"User Management"`, `"Authentication"`. Use a descriptive category name matching the module or subsystem.

## Dependencies

- Prefer standard library solutions over new third-party packages
- **Ask before adding any new dependency** — new packages must be installable via `apt` and added to `src/resources/scripts/apt_requirements.txt`
- Bundled local packages: `src/resources/sibcontrol/` (SIB hardware control), `src/resources/pwquality_windows/` (Windows password policy)

## Guardrails

- **Do NOT modify `src/resources/sibcontrol/`** (SIB communication package) without explicit approval
- Always wrap UI-facing code in try/except to prevent crashes
- Platform-specific code must handle both Linux and Windows (`platform.system()` checks)

## Threading

Tkinter is single-threaded. All UI updates **must** happen on the main thread.

- Use **daemon threads** for background work: `threading.Thread(target=fn, daemon=True)`
- Marshal UI updates back to main thread via `widget.after(0, lambda: ...)` — never update widgets directly from a background thread
- Use `threading.Event()` for graceful shutdown of long-running loops (check `shutdown_flag.is_set()`)
- Use `widget.after(interval, callback)` for periodic polling (e.g., connectivity checks)
- RxPY `BehaviorSubject` is used for reactive state management across components

```python
# Background work pattern
def _doWork(self):
    result = expensiveOperation()
    self.root.after(0, lambda: self.label.configure(text=result))

thread = threading.Thread(target=self._doWork, daemon=True)
thread.start()
```

## Platform-Specific Code

The app runs on Linux (Raspberry Pi, deployed) and Windows (development). Use `platform.system()` to branch:

```python
if platform.system() == "Windows":
    # Dev/mock implementation
else:
    # Linux/production implementation
```

Key platform differences:
- **Config paths:** Linux uses `/etc/skroot/`, Windows uses `%PROGRAMDATA%\Skroot\`
- **Hardware:** SIB serial ports, GPIO pump control, CPU temp — Linux only; Windows uses mocks
- **WiFi:** `nmcli` on Linux, different approach on Windows
- **USB drives:** Linux mounts via `subprocess`; Windows defaults to `D:\`
- **Date formatting:** Linux uses `%-d` (no padding), Windows uses `%#d`

## File Organization

When adding new code, follow existing directory conventions:

- **New widgets** → `src/app/widget/`
- **New use-case-specific code** → `src/app/use_case/<product>/`
- **New shared utilities** → `src/app/helper_methods/`
- **New data models** → `src/app/helper_methods/model/`
- **New custom exceptions** → `src/app/helper_methods/custom_exceptions/`
- **New shared services** → `src/app/common_modules/`
- **New configuration/properties** → `src/app/properties/`

New use cases require changes in multiple places — see "Adding a New Use Case" below.

## Adding a New Use Case

1. **Add to `UseCase` enum** in `src/resources/version/version.py` and update `use_case_themes`
2. **Create use case directory** under `src/app/use_case/<name>/` with:
   - `<name>_sib.py` — extends `BaseSib` from `src/app/reader/sib/base_sib.py`
   - `<name>_kpi_form.py` — extends `KpiForm` from `src/app/widget/kpi_form/kpi_form_base.py`
3. **Add setup form config** — static method in `src/app/use_case/configuration/setup_form_config.py`
4. **Add SIB properties** — static method in `src/app/use_case/configuration/sib_properties.py`
5. **Wire into factory** — update all methods in `src/app/use_case/use_case_factory.py`
6. **Add release notes file** — `src/resources/version/release_notes/<Name>.json`
7. **Add product selection entry** — update `src/app/widget/product_selection.py`

## Environment Setup

**Linux (deployed):**
```bash
# Install system dependencies
sudo apt install $(cat src/resources/scripts/apt_requirements.txt)
sudo pip3 install reactivex --break-system-packages
# Run full install
bash src/resources/scripts/install-script.sh
```

**Windows (development):**
```bash
pip install -r src/resources/scripts/win-requirements.txt
```

`device_config.json` only exists on deployed devices. On dev machines without it, the app shows a product selection dialog on first launch.

## Running & Testing

```bash
# Run unit tests
python -m pytest src/test/unit_tests/

# Launch the GUI (verify no import errors)
python src/app/main.py
```

Entry point: `src/app/main.py`

## Jira Workflow

Project key: **WW** (Jira). All feature work is tied to Jira tickets (e.g., WW-431). Use the ticket number in branch names and commit messages.

## Branch Naming Convention

Branches should follow this format:
```
feature/WW-{ticket_number}-{short-description}
bugfix/WW-{ticket_number}-{short-description}
```
- Use `feature/` for new features and enhancements
- Use `bugfix/` for bug fixes
- Use kebab-case for the description
- Always include the Jira ticket number

Examples:
- `feature/WW-420-add-product-dropdown`
- `bugfix/WW-403-fix-refresh-buttons`
- `feature/WW-411-412-clear-hardware-ids`

## Commit Convention

Commits follow a Jira ticket-based format:
```
WW-{ticket_number} {Description}
```
Examples from the repo history:
- `WW-420 add SkrootFlowCell option to dropdown for product types.`
- `WW-411-412 Add functionality to clear existing hardware IDs and removed hardware ID manual entry.`
- `WW-403 Add refresh buttons to DeviceManagement, ExperimentView, and UserManagement tables`

If no Jira ticket is associated, use a plain descriptive message.

## Commit Squashing

Before pushing, squash all commits from the current session into a single commit. This keeps the git history clean and makes code review easier.

- Use `git rebase -r HEAD~N` (where N is the number of commits in the session) to squash down to one commit, or `git reset --soft` to the base commit and re-commit.
- The final squashed commit message should follow the Commit Convention above and summarize all changes made during the session.
- If the session involved multiple logical changes, list them as bullet points in the commit body.

## PR Workflow

- Push to feature/bugfix branches, then open a PR against `master`
- PRs require review before merging
- CI/CD (GitHub Actions) handles deployment to S3 on release publication
