# **PyRPF - Application Packager**

**PyRPF** (Python Resource Packing Framework) is a simple Python tool that allows you to create a standalone executable (`.exe`) from your Python application. The program bundles your application files and dependencies into a single executable file using **PyInstaller**. It provides an easy-to-use graphical interface to help you select the folder containing your Python application and specify the output file name.

## **Features**:
- **Browse for Folder**: Select the folder containing your Python application.
- **Name Your Output File**: Provide the name for the `.exe` file that will be created.
- **Automatic Packing**: The tool automatically packages your application, including all its files and dependencies, into a standalone `.exe` file.
- **Cross-Platform GUI**: Built using **PySide6** for creating modern, platform-independent graphical user interfaces.

## **Requirements**:
Before you can use **PyRPF**, make sure you have the following dependencies installed:

- **PySide6**: The Qt6 bindings for Python used to create the GUI.
- **requests**: A Python library for handling HTTP requests (though it's not directly used in the current version, it might be useful in future versions for handling file downloads or web-based services).
- **pyinstaller**: A tool for packaging Python programs into standalone executables.

### **Installation**:
To install the required dependencies, run the following command in your terminal or command prompt:

```bash
pip install PySide6 requests pyinstaller
```

## How to Use:

### 1. Clone or Download the Repository:

You can clone the repository using Git, or download the files as a ZIP and extract them to your local machine.

### 2. Install the Required Dependencies:

After downloading the code, navigate to the directory containing the script and install the necessary dependencies:

pip install PySide6 requests pyinstaller

Or by using:

```bash
pip install -r requirements.txt
```

### 3. Run the Program:

Run the script by executing the following:

```bash
python app_packager_gui.py
```

This will launch the GUI application.

### 4. Using the GUI:

The graphical interface will appear, and you can perform the following actions:

    Browse for Folder: Click on the "Browse" button to select the folder containing your Python application.
    Enter Output File Name: In the "Enter the output file name" field, type the name you want for the output .exe file (for example: my_application.exe).
    Click "Package Application": Once everything is set, click the "Package Application" button to start the packaging process.

The program will package your Python application into a .exe file, which will be placed in the same folder as the script.
Example:

If you have a Python project located in the folder C:/projects/my_app/ and want to create an executable named my_app.exe, you will:

    Select the folder C:/projects/my_app/.
    Enter the output file name as my_app.exe.
    Click the Package Application button.

The program will generate the my_app.exe file in the same folder.

## About PyRPF:

PyRPF stands for Python Resource Packing Framework. It is a tool for packaging Python applications along with their resources (such as dependencies, data files, etc.) into a single, standalone executable. This allows your Python application to run on systems without requiring a Python installation.

## License

This project is under the MIT License. See LICENSE file for more.
