# 📦 Inventory Management System

A Python-based desktop application for managing products, suppliers, purchases, and sales with a modern GUI built using Tkinter.

## Features

✨ **Features Included:**
- ✅ Add, view, and manage products
- ✅ Supplier management
- ✅ Purchase tracking
- ✅ Sales management
- ✅ Low stock alerts
- ✅ Sales summary reports
- ✅ MySQL database integration
- ✅ User-friendly GUI interface

## Screenshots

```
📦 Inventory Management System
├── ➕ Add Product
├── 📋 View Products
├── 👥 Add Supplier
├── 🛒 Purchase Product
├── 💳 Sell Product
├── ⚠️ Low Stock Report
└── 📊 Sales Summary
```

## Installation

### Prerequisites
- Python 3.7+
- MySQL Server running locally
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/dwivedi-mohit/stockandinventory.git
cd stockandinventory
```

### Step 2: Setup Database
```bash
# Create the database and tables
mysql -u root -p < database_setup.sql
```

### Step 3: Install Dependencies
```bash
# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

## Running the Application

### Development Mode
```bash
python inventory_ui.py
```

### Create Standalone Executable (Windows/macOS/Linux)
```bash
# Make build script executable (macOS/Linux)
chmod +x build.sh

# Run build script
./build.sh

# The executable will be created in the 'dist' folder
# Run it directly without Python installation!
```

## Building for Distribution

### Option 1: Using PyInstaller (Recommended)
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name="InventorySystem" inventory_ui.py

# Find executable in dist/ folder
```

### Option 2: Create Windows Installer
```bash
# Install pyinstaller and setuptools
pip install pyinstaller setuptools

# Create installer
pyinstaller --onefile --windowed --icon=icon.ico inventory_ui.py
```

## Publishing Steps

### 1. **Create Releases on GitHub**
```bash
# Tag your release
git tag v1.0.0
git push origin v1.0.0

# Go to GitHub → Releases → Create Release
# Upload the executable from dist/ folder
```

### 2. **Create installer with PyInstaller**
```bash
pyinstaller --onefile --windowed \
  --name="InventoryManagementSystem" \
  --icon=icon.ico \
  inventory_ui.py
```

### 3. **Distribute to Users**
- Share the standalone executable
- Users can run without installing Python
- All dependencies are bundled

### 4. **Package for PyPI (Python Package Index)**
```bash
# Create setup.py
pip install wheel twine

# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

## Project Structure

```
stockandinventory/
├── inventory_ui.py              # Main GUI application
├── inventory_management.py       # Database operations
├── connection_test.py            # Database connection test
├── requirements.txt              # Python dependencies
├── build.sh                      # Build script for executable
├── README.md                     # Documentation
└── setup.sh                      # Environment setup script
```

## Configuration

Edit the database connection settings in `inventory_ui.py`:
```python
self.conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="inventory_db"
)
```

## Database Schema

The application requires these tables:
- `Products` - product_id, product_name, price, stock_quantity
- `Suppliers` - supplier_id, supplier_name, contact_info, email

## Troubleshooting

### Database Connection Error
- Ensure MySQL Server is running
- Verify username and password
- Check database name exists

### GUI Not Launching
- Ensure tkinter is installed: `python -m tkinter`
- Check Python version (3.7+)

### Build Fails
- Clear previous builds: `rm -rf build dist *.spec`
- Reinstall PyInstaller: `pip install --upgrade pyinstaller`

## Version History

- **v1.0.0** - Initial release with GUI
- Features: Product management, Sales tracking, Reports

## License

This project is open source and available under the MIT License.

## Author

**Mohit Dwivedi**
- GitHub: [@dwivedi-mohit](https://github.com/dwivedi-mohit)

## Support

For issues, questions, or contributions, please create an issue on GitHub.