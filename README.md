# The Maze Project Save Viewer

A PyQt5-based GUI application for viewing and editing encrypted save files from "The Maze Project" game. This tool provides a user-friendly interface to decrypt, inspect, modify, and re-encrypt game save files.

## Features

- **Decrypt and View Save Files**: Open encrypted `.save` files and view their contents in a structured tree format
- **Edit Save Data**: Modify save file values directly in the GUI with automatic type preservation
- **Save Changes**: Save modifications back to the original file or export to a new file
- **Raw View**: View the raw JSON content with options to:
  - Hide graph data for cleaner viewing
  - Toggle JSON prettification
- **Type-Safe Editing**: Automatically preserves data types (int, float, bool, string) when editing values

## Requirements

- Python 3.12 or higher
- PyQt5
- pycryptodome

## Installation

1. **Clone or download** this repository to your local machine

2. **Create a virtual environment** (recommended):

   ```powershell
   python -m venv env
   ```

3. **Activate the virtual environment**:

   ```powershell
   .\env\Scripts\Activate.ps1
   ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```powershell
python save-viewer.py
```

### Opening a Save File

1. Launch the application
2. Go to **File > Open** (or press `Ctrl+O`)
3. Select a `.save` file from "The Maze Project" game
4. The decrypted content will appear in the tree view

### Editing Save Data

1. Open a save file
2. Navigate through the tree structure to find the value you want to modify
3. Double-click on the value in the "value" column
4. Edit the value (the application will preserve the original data type)
5. Press Enter to confirm the change

### Saving Changes

- **Save to current file**: Go to **File > Save** (or press `Ctrl+S`)
- **Save to new file**: Go to **File > Save As**

### Viewing Raw Data

1. Open a save file
2. Go to **File > View Raw** (or press `Ctrl+R`)
3. Use the checkboxes to:
   - **Hide graph data**: Filters out graph-related data for cleaner viewing
   - **Prettify JSON**: Formats the JSON with proper indentation

## Technical Details

### Encryption

The tool uses AES encryption in CBC mode with:

- **Key**: `hE0+JOzhYLBPOqXmb43vj5+DUigTMjmUu4j3zWNb3LI=` (Base64 encoded)
- **IV**: `fvaCYFNydvipQUqTlD9yXg==` (Base64 encoded)

### File Format

Save files are:

1. JSON data structures containing game state
2. Encrypted using AES-256-CBC
3. Stored with `.save` extension

### Data Types

The viewer preserves the following data types when editing:

- `bool`: Accepts true/false, 1/0, yes/no, on/off (case-insensitive)
- `int`: Integer numbers
- `float`: Decimal numbers
- `str`: Text strings

## File Structure

```
themazeproject-save-viewer/
├── save-viewer.py          # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── env/                   # Virtual environment (created after setup)
```

## Dependencies

- **PyQt5**: GUI framework
- **pycryptodome**: Cryptographic operations for AES encryption/decryption
- **json**: Built-in JSON parsing (standard library)
- **base64**: Base64 encoding/decoding (standard library)

## Keyboard Shortcuts

- `Ctrl+O`: Open save file
- `Ctrl+S`: Save current file
- `Ctrl+R`: View raw JSON data
- `Ctrl+Q`: Exit application

## Troubleshooting

### Common Issues

1. **"Permission denied" when saving**:

   - Ensure the save file isn't being used by the game
   - Check file permissions

2. **Decryption errors**:

   - Verify the file is a valid save file from "The Maze Project"
   - Check if the file is corrupted

3. **Import errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Verify you're using the correct virtual environment

### Data Safety

- **Always backup your save files** before editing
- The application creates encrypted saves, but data corruption is possible if invalid values are entered
- Test modified saves in a safe environment first

## Contributing

This tool was created for "The Maze Project" save file management. If you encounter bugs or have feature requests, please:

1. Ensure you can reproduce the issue
2. Check that your Python environment meets the requirements
3. Provide detailed information about the problem

## License

This tool is provided as-is for educational and personal use with "The Maze Project" game save files.

## Disclaimer

This tool is not officially associated with "The Maze Project" game. Use at your own risk and always backup your save files before making any modifications.

**Maintenance Notice**: This tool is provided as-is with no guarantee of future updates, bug fixes, or ongoing maintenance. The tool may become incompatible with future game updates or operating system changes.
