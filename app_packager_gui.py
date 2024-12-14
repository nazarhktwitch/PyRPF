import os
import shutil
import sys
import subprocess
import tempfile
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QWidget, QCheckBox, QProgressBar
)
from tqdm import tqdm

def create_exe_with_dependencies(folder_path, main_exe, output_name, delete_temp_files, save_location, additional_params, icon_path):
    try:
        # Create a folder named after the output folder name
        output_folder = os.path.join(save_location, output_name)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Create temporary folder for the build
        temp_build_dir = os.path.join(os.getcwd(), "build_temp")
        if os.path.exists(temp_build_dir):
            shutil.rmtree(temp_build_dir)
        os.makedirs(temp_build_dir)

        # Copy all files from the source folder to the temporary build folder with progress
        files = []
        for item in os.listdir(folder_path):
            src_path = os.path.join(folder_path, item)
            if os.path.isdir(src_path):
                files.append((src_path, True))  # Add directories
            else:
                files.append((src_path, False))  # Add files

        # Create a progress bar to display the copying process
        progress_bar = QProgressBar()
        progress_bar.setMaximum(len(files))
        progress_bar.setMinimum(0)
        progress_bar.setValue(0)

        for file, is_dir in tqdm(files, desc="Copying Files", ncols=100):
            dest_path = os.path.join(temp_build_dir, os.path.basename(file))
            if is_dir:
                shutil.copytree(file, dest_path)
            else:
                shutil.copy2(file, dest_path)
            progress_bar.setValue(progress_bar.value() + 1)

        # Create loader script that unpacks the app when executed
        loader_script = os.path.join(temp_build_dir, "loader.py")
        with open(loader_script, "w") as loader:
            loader.write(f"""
import os
import sys
import shutil
import subprocess
import tempfile

def main():
    temp_dir = tempfile.mkdtemp()
    exe_path = os.path.join(temp_dir, '{main_exe}')

    # Create a folder with the name of the output file
    output_dir = os.path.join(os.getcwd(), '{output_name}')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract the data
    current_dir = os.path.dirname(sys.argv[0])
    for item in os.listdir(current_dir):
        src_path = os.path.join(current_dir, item)
        dest_path = os.path.join(output_dir, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)

    # Run the main app
    subprocess.run([exe_path], cwd=output_dir)
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
""")

        # Build command to run PyInstaller
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",  # Create a single executable file
            "--add-data", f"{temp_build_dir}{os.pathsep}.",  # Add all data from the temp build dir
            "--name", output_name,
            loader_script
        ]
        
        # Add icon if provided
        if icon_path:
            pyinstaller_cmd.append(f"--icon={icon_path}")
        
        # Add additional parameters if any
        if additional_params:
            pyinstaller_cmd.extend(additional_params.split(";"))

        # Use PyInstaller to bundle everything
        subprocess.run(pyinstaller_cmd, check=True)

        # Move the EXE to the selected location
        dist_path = os.path.join(os.getcwd(), "dist", f"{output_name}.exe")
        if os.path.exists(dist_path):
            shutil.move(dist_path, output_folder)

        # Remove temporary files if checkbox is selected
        if delete_temp_files:
            shutil.rmtree(temp_build_dir)
            spec_file = os.path.join(os.getcwd(), f"{output_name}.spec")
            if os.path.exists(spec_file):
                os.remove(spec_file)
            shutil.rmtree(os.path.join(os.getcwd(), "build"))
            shutil.rmtree(os.path.join(os.getcwd(), "dist"))

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
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.folder_label = QLabel("Select the folder containing your application:")
        layout.addWidget(self.folder_label)

        self.folder_input = QLineEdit()
        layout.addWidget(self.folder_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)

        self.main_exe_label = QLabel("Select the main executable (if more than one .exe exists):")
        layout.addWidget(self.main_exe_label)

        self.main_exe_input = QLineEdit()
        layout.addWidget(self.main_exe_input)

        self.output_label = QLabel("Enter the output file name:")
        layout.addWidget(self.output_label)

        self.output_input = QLineEdit()
        layout.addWidget(self.output_input)

        self.save_location_label = QLabel("Select where to save the final executable:")
        layout.addWidget(self.save_location_label)

        self.save_location_input = QLineEdit()
        layout.addWidget(self.save_location_input)

        self.browse_save_button = QPushButton("Browse to save location")
        self.browse_save_button.clicked.connect(self.browse_save_location)
        layout.addWidget(self.browse_save_button)

        self.additional_params_label = QLabel("Enter additional PyInstaller parameters (separate with semicolon `;`):")
        layout.addWidget(self.additional_params_label)

        self.additional_params_input = QLineEdit()
        layout.addWidget(self.additional_params_input)

        self.icon_label = QLabel("Select an icon for the executable (Leave empty for default):")
        layout.addWidget(self.icon_label)

        self.icon_input = QLineEdit()
        layout.addWidget(self.icon_input)

        self.browse_icon_button = QPushButton("Browse for Icon")
        self.browse_icon_button.clicked.connect(self.browse_icon)
        layout.addWidget(self.browse_icon_button)

        self.delete_temp_files_checkbox = QCheckBox("Delete temporary files after packaging (.spec, build, dist)")
        layout.addWidget(self.delete_temp_files_checkbox)

        self.package_button = QPushButton("Package Application")
        self.package_button.clicked.connect(self.package_app)
        layout.addWidget(self.package_button)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select the folder containing your application")
        if folder:
            self.folder_input.setText(folder)
            self.check_exes(folder)

    def check_exes(self, folder_path):
        # Check for .exe files in the folder
        exe_files = [f for f in os.listdir(folder_path) if f.endswith('.exe')]
        if len(exe_files) == 1:
            self.main_exe_input.setText(exe_files[0])
        elif len(exe_files) > 1:
            self.main_exe_input.clear()

    def browse_save_location(self):
        save_location = QFileDialog.getExistingDirectory(self, "Select save location for the executable")
        if save_location:
            self.save_location_input.setText(save_location)

    def browse_icon(self):
        icon_file, _ = QFileDialog.getOpenFileName(self, "Select an Icon", "", "Icon Files (*.ico);;All Files (*)")
        if icon_file:
            self.icon_input.setText(icon_file)

    def package_app(self):
        folder_path = self.folder_input.text()
        main_exe = self.main_exe_input.text()
        output_name = self.output_input.text()
        save_location = self.save_location_input.text()
        additional_params = self.additional_params_input.text()
        icon_path = self.icon_input.text()
        delete_temp_files = self.delete_temp_files_checkbox.isChecked()

        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.critical(self, "Error", "Please provide an existing folder with your application!")
            return

        if not output_name:
            QMessageBox.critical(self, "Error", "Please provide an output file name!")
            return

        if not main_exe:
            QMessageBox.critical(self, "Error", "Please select the main executable!")
            return

        if not save_location:
            QMessageBox.critical(self, "Error", "Please provide a save location!")
            return

        success = create_exe_with_dependencies(folder_path, main_exe, output_name, delete_temp_files, save_location, additional_params, icon_path)
        if success:
            QMessageBox.information(self, "Success", f"Application '{output_name}.exe' has been successfully created!")
        else:
            QMessageBox.critical(self, "Error", "Failed to create the application.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    packager = AppPackager()
    packager.show()
    sys.exit(app.exec())
