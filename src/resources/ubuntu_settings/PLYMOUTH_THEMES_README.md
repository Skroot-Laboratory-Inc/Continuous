# Plymouth Boot Splash Themes

This directory contains Plymouth boot splash themes for different use cases.

## Theme Structure

Each theme directory should contain:
- `<theme-name>.plymouth` - Plymouth theme configuration file
- `<theme-name>.script` - Plymouth script that displays the logo
- `<theme-name>-logo.png` - The logo image file (720x1280 recommended for portrait displays)

## Available Themes

### IBI Theme
- Directory: `ibi/`
- Logo file required: `ibi-logo.png`
- Used when `Version().theme == Theme.IBI`

### Skroot Theme
- Directory: `skroot/`
- Logo file required: `skroot-logo.png`
- Used when `Version().theme == Theme.Skroot`

### Wilson-Wolf Theme
- Directory: `wilson-wolf/`
- Logo file required: `wilson-wolf-logo.png`
- Used when `Version().theme == Theme.WW`

## Installation

The install-script.sh automatically detects the theme from the Version class and installs the appropriate Plymouth theme.

## Adding Logo Images

To add or update logo images:
1. Place your logo PNG file in the appropriate theme directory
2. Name it according to the pattern: `<theme-name>-logo.png`
3. Recommended size: 720x1280 pixels (portrait orientation)
4. The logo will be scaled to fill the screen during boot

## Theme Selection

The theme is determined by the `Version().theme` property in `src/resources/version/version.py`.
