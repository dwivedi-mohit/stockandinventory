# 🚀 Publishing Guide

## Quick Start: Build Standalone Executable

### Step 1: Install Build Tools
```bash
pip install -r requirements.txt
```

### Step 2: Build Executable
```bash
# Make build script executable (macOS/Linux)
chmod +x build.sh
./build.sh

# Or manually:
pyinstaller --onefile --windowed --name="InventoryManagementSystem" inventory_ui.py
```

### Step 3: Distribute
The executable is in `dist/InventoryManagementSystem`
- Users can run it directly
- No Python installation needed
- All dependencies included

---

## Publishing to GitHub Releases

```bash
# Create a release tag
git tag v1.0.0
git push origin v1.0.0

# Go to GitHub → Releases → Create Release
# Upload dist/InventoryManagementSystem file
```

---

## Publishing to PyPI

```bash
# Install publishing tools
pip install wheel twine

# Build distribution packages
python setup.py sdist bdist_wheel

# Create PyPI account at https://pypi.org

# Upload to PyPI
twine upload dist/*

# Users can then install with:
# pip install inventory-management-system
```

---

## Supported Platforms

✅ Windows (.exe)
✅ macOS (.app)
✅ Linux (binary)

---

## Build Options

### Windows Installer (MSI)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="InventorySystem" inventory_ui.py
```

### macOS DMG
```bash
# Create signed app
pyinstaller --onefile --windowed --osx-bundle-identifier="com.example.inventory" inventory_ui.py
```

### Linux AppImage
```bash
# Requires linux-appimage
appimage-builder --recipe=AppImageBuilder.yml
```

---

## Requirements

- Python 3.7+
- MySQL Server (for database functionality)
- mysql-connector-python
- tkinter (usually included with Python)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | `rm -rf build dist *.spec` then rebuild |
| Database won't connect | Verify MySQL is running and credentials are correct |
| Missing dependencies | Run `pip install -r requirements.txt` |
| GUI doesn't launch | Check Python version >= 3.7 |

---

## Version Numbers

Follow semantic versioning:
- `1.0.0` - Initial release
- `1.1.0` - New features
- `1.0.1` - Bug fixes
- `2.0.0` - Major breaking changes

---

## Distribution Checklist

- [ ] Code tested and working
- [ ] README updated
- [ ] Version number incremented
- [ ] CHANGELOG updated
- [ ] Tests pass
- [ ] Executable built and tested
- [ ] GitHub Release created
- [ ] PyPI package updated (optional)
- [ ] Users notified

---

## Questions?

Check the main README.md for more information!
