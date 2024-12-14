import os
import shutil
import sys
import subprocess
from tqdm import tqdm
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QWidget, QCheckBox, QProgressBar
)

def create_exe_with_dependencies(folder_path, main_exe, output_name, unpack_folder_name, delete_temp_files, save_location, additional_params, icon_path, update_progress):
    try:
        # Убедимся, что целевая папка существует
        output_folder = save_location
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Временная папка для сборки
        temp_build_dir = os.path.join(os.getcwd(), "build_temp")
        if os.path.exists(temp_build_dir):
            shutil.rmtree(temp_build_dir)
        os.makedirs(temp_build_dir)

        # Копируем саму папку (например, betterjoy) в временную директорию
        folder_name = os.path.basename(folder_path)  # Берем имя папки
        files_to_copy = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                files_to_copy.append(os.path.join(root, file))

        # Прогресс-бар для копирования файлов
        for file in tqdm(files_to_copy, desc="Copying files", unit="file"):
            dest_path = os.path.join(temp_build_dir, os.path.relpath(file, folder_path))
            dest_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            shutil.copy2(file, dest_path)

        # Создаем loader скрипт
        loader_script = os.path.join(temp_build_dir, "loader.py")
        with open(loader_script, "w") as loader:
            loader.write(f"""
import os
import sys
import shutil
import subprocess

def unpack_data():
    # Папка, в которую будут распаковываться файлы
    unpack_dir = os.path.join(os.getcwd(), '{unpack_folder_name}')

    # Если папка уже существует, выводим предупреждение
    if os.path.exists(unpack_dir):
        print(f"Warning: Folder '{{unpack_folder_name}}' already exists!")
        input("Press Enter to continue or close this window to abort...")
    else:
        os.makedirs(unpack_dir)

    # Извлекаем данные из текущего исполнимого файла
    current_dir = os.path.dirname(sys.argv[0])

    if hasattr(sys, '_MEIPASS'):
        # Если исполнимый файл был упакован с PyInstaller, данные находятся в временной директории
        data_dir = sys._MEIPASS
    else:
        # Если это обычный запуск из исходных файлов
        data_dir = current_dir

    target_dir = os.path.join(data_dir, '{folder_name}')  # Папка с вашими данными

    # Копируем все файлы из папки в целевую папку
    for item in os.listdir(target_dir):
        src_path = os.path.join(target_dir, item)
        dest_path = os.path.join(unpack_dir, item)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dest_path)

def main():
    # Распаковываем данные
    unpack_data()

    # Запускаем основной исполнимый файл
    exe_path = os.path.join(os.getcwd(), '{unpack_folder_name}', '{main_exe}')
    subprocess.run([exe_path], cwd=os.path.join(os.getcwd(), '{unpack_folder_name}'))

if __name__ == "__main__":
    main()
""")

        # Создаем команду для PyInstaller
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",  # Собираем один файл .exe
            "--add-data", f"{temp_build_dir}{os.pathsep}{folder_name}",  # Указываем путь папки для встраивания в .exe
            "--name", output_name,
            loader_script
        ]
        
        # Добавляем дополнительные параметры, если есть
        if additional_params:
            pyinstaller_cmd.extend(additional_params.split(";"))

        # Добавляем иконку, если указан путь
        if icon_path and os.path.exists(icon_path):
            pyinstaller_cmd.extend(["--icon", icon_path])

        # Обновляем прогресс-бар для сборки с PyInstaller
        process = subprocess.Popen(pyinstaller_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Correct the use of update_progress, which was passed as an argument
        for line in tqdm(process.stdout, desc="Building executable", unit="line"):
            if update_progress:
                update_progress(line.decode())

        process.wait()  # Ждем завершения процесса сборки

        # Перемещаем EXE в выбранную папку
        dist_path = os.path.join(os.getcwd(), "dist", f"{output_name}.exe")
        if os.path.exists(dist_path):
            shutil.move(dist_path, output_folder)

        # Удаляем временные файлы, если указано
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
        self.setGeometry(100, 100, 400, 450)

        layout = QVBoxLayout()

        self.folder_label = QLabel("Select the folder containing your application:")
        layout.addWidget(self.folder_label)

        self.folder_input = QLineEdit()
        layout.addWidget(self.folder_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)

        self.unpack_folder_label = QLabel("Enter the name of the unpack folder:")
        layout.addWidget(self.unpack_folder_label)

        self.unpack_folder_input = QLineEdit()
        layout.addWidget(self.unpack_folder_input)

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

        self.delete_temp_files_checkbox = QCheckBox("Delete temporary files after packaging (.spec, build, dist)")
        layout.addWidget(self.delete_temp_files_checkbox)

        self.package_button = QPushButton("Package Application")
        self.package_button.clicked.connect(self.package_app)
        layout.addWidget(self.package_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select the folder containing your application")
        if folder:
            self.folder_input.setText(folder)
            self.check_exes(folder)

    def check_exes(self, folder_path):
        # Ищем все исполнимые файлы (.exe, .bat, .py) в папке
        exe_files = [f for f in os.listdir(folder_path) if f.endswith(('.exe', '.bat', '.py'))]

        # Если найден один файл, устанавливаем его как основной
        if len(exe_files) == 1:
            self.main_exe_input.setText(exe_files[0])
        elif len(exe_files) > 1:
            self.main_exe_input.clear()  # Если найдено несколько файлов, очищаем поле для ввода

    def browse_save_location(self):
        save_location = QFileDialog.getExistingDirectory(self, "Select save location for the executable")
        if save_location:
            self.save_location_input.setText(save_location)

    def package_app(self):
        folder_path = self.folder_input.text()
        main_exe = self.main_exe_input.text()
        output_name = self.output_input.text()
        unpack_folder_name = self.unpack_folder_input.text()
        save_location = self.save_location_input.text()
        additional_params = self.additional_params_input.text()
        delete_temp_files = self.delete_temp_files_checkbox.isChecked()

        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.critical(self, "Error", "Please provide an existing folder with your application!")
            return

        if not unpack_folder_name:
            QMessageBox.critical(self, "Error", "Please provide a name for the unpack folder!")
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

        # Запуск упаковки с прогрессом
        success = create_exe_with_dependencies(folder_path, main_exe, output_name, unpack_folder_name, delete_temp_files, save_location, additional_params, icon_path=None, update_progress=self.update_progress)
        if success:
            QMessageBox.information(self, "Success", f"Application '{output_name}.exe' has been successfully created!")
        else:
            QMessageBox.critical(self, "Error", "Failed to create the application.")

    def update_progress(self, message):
        # Пример обновления прогресс-бара с помощью сообщений
        if 'Copying' in message:
            self.progress_bar.setValue(50)
        elif 'Building' in message:
            self.progress_bar.setValue(100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    packager = AppPackager()
    packager.show()
    sys.exit(app.exec())
