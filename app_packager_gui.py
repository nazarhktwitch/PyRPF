import os
import shutil
import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QWidget
)

def create_exe_with_dependencies(folder_path, output_name):
    try:
        # Create temporary folder for the build
        temp_build_dir = os.path.join(os.getcwd(), "build_temp")
        if os.path.exists(temp_build_dir):
            shutil.rmtree(temp_build_dir)
        os.makedirs(temp_build_dir)

        # Copy all files from the source folder to the temporary build folder
        for item in os.listdir(folder_path):
            src_path = os.path.join(folder_path, item)
            dest_path = os.path.join(temp_build_dir, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)

        # Create loader script
        loader_script = os.path.join(temp_build_dir, "loader.py")
        with open(loader_script, "w") as loader:
            loader.write("""
import os
import sys
import shutil
import subprocess
import tempfile

def main():
    temp_dir = tempfile.mkdtemp()
    exe_path = os.path.join(temp_dir, 'app.exe')

    # Extract the data
    current_dir = os.path.dirname(sys.argv[0])
    for item in os.listdir(current_dir):
        src_path = os.path.join(current_dir, item)
        dest_path = os.path.join(temp_dir, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)

    # Run the main app
    subprocess.run([exe_path], cwd=temp_dir)
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
""")

        # Use PyInstaller to bundle everything
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--add-data", f"{temp_build_dir}{os.pathsep}.",
            "--name", output_name,
            loader_script
        ], check=True)

        # Remove temporary files
        shutil.rmtree(temp_build_dir)
        dist_path = os.path.join(os.getcwd(), "dist", f"{output_name}.exe")
        final_path = os.path.join(os.getcwd(), f"{output_name}.exe")
        shutil.move(dist_path, final_path)
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

class AppPackager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyRPF - Application Packager")
        self.setGeometry(100, 100, 400, 250)

        layout = QVBoxLayout()

        self.folder_label = QLabel("Select the folder containing your application:")
        layout.addWidget(self.folder_label)

        self.folder_input = QLineEdit()
        layout.addWidget(self.folder_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)

        self.output_label = QLabel("Enter the output file name:")
        layout.addWidget(self.output_label)

        self.output_input = QLineEdit()
        layout.addWidget(self.output_input)

        self.package_button = QPushButton("Package Application")
        self.package_button.clicked.connect(self.package_app)
        layout.addWidget(self.package_button)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select the folder containing your application")
        if folder:
            self.folder_input.setText(folder)

    def package_app(self):
        folder_path = self.folder_input.text()
        output_name = self.output_input.text()

        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.critical(self, "Error", "Please provide an existing folder with your application!")
            return

        if not output_name:
            QMessageBox.critical(self, "Error", "Please provide an output file name!")
            return

        success = create_exe_with_dependencies(folder_path, output_name)
        if success:
            QMessageBox.information(self, "Success", f"Application '{output_name}.exe' has been successfully created!")
        else:
            QMessageBox.critical(self, "Error", "Failed to create the application.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    packager = AppPackager()
    packager.show()
    sys.exit(app.exec())