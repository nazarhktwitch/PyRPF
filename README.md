# PyRPF - Application Packager

## About
**PyRPF** stands for **Python Rapid Packager Framework**. It is a tool designed to package a ready-to-use executable application (`.exe`) along with all its necessary dependencies (e.g., DLL files, `lib` folders, `Plugins`, and other resources) into a single `.exe` file. Once packaged, the application works exactly as it did before, but everything is contained in one executable.

This project also serves as an **alternative to SFX archives**, written entirely in Python.

## Features
- Packages a `.exe` application with all its dependencies.
- Supports any types of files and folders required for the application.
- Automatically creates a self-extracting loader that unpacks dependencies and runs the main executable.

## Requirements
- Python 3.8+
- Installed dependencies from `requirements.txt`
- Installed `PyInstaller`
- Windows operating system

## Installing Dependencies

Before usage, install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Use
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PyRPF.git
   cd PyRPF
   ```

2. Ensure Python and dependencies are installed.

3. Launch the GUI interface:
   ```bash
   python app_packager_gui.py
   ```

4. Select the folder containing your application (must include the `.exe` file and all necessary folders/files).

5. Specify the name of the output file (`.exe`).

6. Click "Package Application". After completion, a single `.exe` file will be generated in the folder.

## Example Input Folder Structure
```
MyApp/
├── app.exe
├── lib/
│   ├── some_library.dll
│   └── another_library.dll
├── plugins/
│   ├── plugin1.dll
│   └── plugin2.dll
└── resources/
    ├── config.json
    └── image.png
```

After packaging, everything will be bundled into a single file `MyApp.exe`.

## Dependencies
- PyQt5
- PyInstaller

## `requirements.txt` File
```
PyQt5
pyinstaller
```

## License
[MIT License](https://github.com/nazarhktwitch/PyRPF/blob/main/LICENSE)