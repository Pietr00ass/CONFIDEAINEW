import os
import hashlib
import secrets
import logging
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog,
    QWidget, QMessageBox, QDialog, QTreeWidget, QTreeWidgetItem, QCheckBox, QLineEdit, QGroupBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QIcon, QFont, QPixmap
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# Konfiguracja logowania
logging.basicConfig(filename='operations.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Funkcja generowania identyfikatora pliku (hash)
def generate_file_id(file_path):
    hash_func = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_func.update(chunk)
    file_id = hash_func.digest()
    logging.info(f"Wygenerowano identyfikator pliku: {file_id.hex()}")
    return file_id

# Funkcja usuwania pliku
def delete_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            logging.info(f"Usunięto plik: {file_path}")
        else:
            logging.warning(f"Plik do usunięcia nie istnieje: {file_path}")
    except Exception as e:
        logging.error(f"Błąd podczas usuwania pliku {file_path}: {e}")

# Funkcja szyfrowania pliku
def encrypt_file(file_path, compress=False, password=None, use_rsa=False, delete_original=False):
    try:
        logging.info(f"Rozpoczęto szyfrowanie pliku: {file_path}")
        
        # Generowanie klucza AES (256-bitowy)
        key = secrets.token_bytes(32)  # 256-bitowy klucz AES
        iv = secrets.token_bytes(16)   # 128-bitowy IV
        logging.info(f"Wygenerowano klucz AES: {key.hex()}")
        logging.info(f"Wygenerowano IV: {iv.hex()}")

        # Otwarcie pliku do odczytu
        with open(file_path, "rb") as f:
            plaintext = f.read()
        logging.info(f"Odczytano plik do zaszyfrowania: {len(plaintext)} bajtów")

        # Szyfrowanie danych
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        logging.info(f"Zaszyfrowano dane: {len(ciphertext)} bajtów")

        # Zapis zaszyfrowanego pliku
        encrypted_path = file_path + ".enc"
        with open(encrypted_path, "wb") as f:
            f.write(iv + ciphertext)
        logging.info(f"Zapisano zaszyfrowany plik: {encrypted_path}")

        # Generowanie HMAC dla weryfikacji integralności
        hmac_key = secrets.token_bytes(32)  # Klucz HMAC
        hmac_generator = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
        hmac_generator.update(ciphertext)
        hmac_digest = hmac_generator.finalize()
        logging.info(f"Wygenerowano HMAC: {hmac_digest.hex()}")

        # Zapis HMAC do pliku
        with open(encrypted_path + ".hmac", "wb") as f:
            f.write(hmac_digest)
        logging.info(f"Zapisano HMAC do pliku: {encrypted_path}.hmac")

        # Generowanie identyfikatora pliku
        file_id = generate_file_id(file_path)
        logging.info(f"Wygenerowano identyfikator pliku: {file_id.hex()}")

        # Zapis klucza, identyfikatora pliku i klucza HMAC
        key_path = file_path + ".key"
        with open(key_path, "wb") as f:
            f.write(file_id + key + hmac_key)  # Dodaj hmac_key do pliku .key
        logging.info(f"Zapisano klucz AES i HMAC do pliku: {key_path}")

        # Usuń oryginalny plik, jeśli użytkownik zaznaczył opcję
        if delete_original:
            delete_file(file_path)

        return encrypted_path, key_path
    except Exception as e:
        logging.error(f"Błąd podczas szyfrowania pliku {file_path}: {e}")
        return None, None

# Funkcja odszyfrowywania pliku
def decrypt_file(file_path, key_path, password=None, use_rsa=False, delete_keys=False, delete_encrypted=False):
    try:
        logging.info(f"Rozpoczęto odszyfrowywanie pliku: {file_path}")
        
        # Sprawdź, czy plik i klucz istnieją
        if not os.path.isfile(file_path):
            logging.error(f"Plik do odszyfrowania nie istnieje: {file_path}")
            return "Plik do odszyfrowania nie istnieje."

        if not os.path.isfile(key_path):
            logging.error(f"Plik klucza nie istnieje: {key_path}")
            return "Plik klucza nie istnieje."

        # Odczyt klucza, identyfikatora i klucza HMAC z pliku .key
        with open(key_path, "rb") as f:
            file_id = f.read(32)  # Pierwsze 32 bajty to identyfikator pliku
            key = f.read(32)      # Kolejne 32 bajty to klucz AES
            hmac_key = f.read(32) # Kolejne 32 bajty to klucz HMAC
        logging.info(f"Odczytano identyfikator pliku: {file_id.hex()}")
        logging.info(f"Odczytano klucz AES: {key.hex()}")
        logging.info(f"Odczytano klucz HMAC: {hmac_key.hex()}")

        # Sprawdź, czy oryginalny plik istnieje
        original_file_path = file_path.replace(".enc", "")
        if os.path.isfile(original_file_path):
            # Generowanie identyfikatora z oryginalnego pliku
            actual_file_id = generate_file_id(original_file_path)
            logging.info(f"Wygenerowano aktualny identyfikator pliku: {actual_file_id.hex()}")

            # Weryfikacja identyfikatora
            if file_id != actual_file_id:
                logging.error("Klucz nie pasuje do tego pliku!")
                return "Klucz nie pasuje do tego pliku!"
        else:
            logging.warning("Oryginalny plik nie istnieje. Pominięto weryfikację identyfikatora.")

        # Sprawdź długość klucza AES
        if len(key) != 32:
            logging.error(f"Niewłaściwa długość klucza AES: {len(key)} bajtów")
            return "Niewłaściwa długość klucza AES."

        # Odczyt zaszyfrowanego pliku
        with open(file_path, "rb") as f:
            data = f.read()
        logging.info(f"Odczytano zaszyfrowany plik: {len(data)} bajtów")

        # Sprawdź, czy plik ma wystarczającą długość (co najmniej 16 bajtów IV)
        if len(data) < 16:
            logging.error(f"Plik zaszyfrowany jest zbyt krótki: {len(data)} bajtów")
            return "Plik zaszyfrowany jest zbyt krótki."

        # IV (pierwsze 16 bajtów)
        iv = data[:16]
        # Zaszyfrowane dane
        encrypted_data = data[16:]
        logging.info(f"Odczytano IV: {iv.hex()}")
        logging.info(f"Odczytano zaszyfrowane dane: {len(encrypted_data)} bajtów")

        # Weryfikacja integralności pliku
        if not os.path.isfile(file_path + ".hmac"):
            logging.error(f"Brak pliku HMAC dla pliku: {file_path}")
            return "Brak pliku HMAC."

        with open(file_path + ".hmac", "rb") as f:
            hmac_digest = f.read()
        logging.info(f"Odczytano HMAC: {hmac_digest.hex()}")

        hmac_verifier = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
        hmac_verifier.update(encrypted_data)
        try:
            hmac_verifier.verify(hmac_digest)
            logging.info("Weryfikacja HMAC zakończona sukcesem.")
        except Exception as e:
            logging.error(f"Błąd weryfikacji HMAC: {e}")
            return "Błąd weryfikacji HMAC."

        # Odszyfrowywanie
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        logging.info(f"Odszyfrowano dane: {len(decrypted_data)} bajtów")

        # Zapis odszyfrowanego pliku
        decrypted_path = file_path.replace(".enc", "")
        with open(decrypted_path, "wb") as f:
            f.write(decrypted_data)
        logging.info(f"Zapisano odszyfrowany plik: {decrypted_path}")

        # Usuń pliki klucza i HMAC, jeśli użytkownik zaznaczył opcję
        if delete_keys:
            delete_file(key_path)
            delete_file(file_path + ".hmac")
            logging.info(f"Usunięto pliki klucza i HMAC.")

        # Usuń zaszyfrowany plik, jeśli użytkownik zaznaczył opcję
        if delete_encrypted:
            delete_file(file_path)
            logging.info(f"Usunięto zaszyfrowany plik: {file_path}")

        return decrypted_path
    except Exception as e:
        logging.error(f"Błąd podczas odszyfrowywania pliku {file_path}: {e}")
        return str(e)

# Funkcja hashowania hasła
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Funkcja rejestracji użytkownika
def register_user(username, password):
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            data = json.load(f)
    else:
        data = {"users": []}

    for user in data["users"]:
        if user["username"] == username:
            return False  # Użytkownik już istnieje

    data["users"].append({
        "username": username,
        "password_hash": hash_password(password)
    })

    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

    return True

# Funkcja logowania użytkownika
def login_user(username, password):
    if not os.path.exists("users.json"):
        return False  # Brak zarejestrowanych użytkowników

    with open("users.json", "r") as f:
        data = json.load(f)

    for user in data["users"]:
        if user["username"] == username and user["password_hash"] == hash_password(password):
            return True  # Logowanie zakończone sukcesem

    return False  # Nieprawidłowa nazwa użytkownika lub hasło

# Klasa etykiety obsługującej przeciąganie i upuszczanie
class DragDropLabel(QLabel):
    def __init__(self, parent=None, on_drop=None):
        super().__init__(parent)
        self.on_drop = on_drop  # Funkcja wywoływana po upuszczeniu pliku
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls() and self.on_drop:
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            self.on_drop(files)
        else:
            event.ignore()

# Klasa okna logowania
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logowanie")
        self.setGeometry(200, 200, 300, 150)

        # Layout
        layout = QVBoxLayout()

        # Pole do wprowadzenia nazwy użytkownika
        self.username_label = QLabel("Nazwa użytkownika:")
        layout.addWidget(self.username_label)
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # Pole do wprowadzenia hasła
        self.password_label = QLabel("Hasło:")
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Przycisk logowania
        self.login_button = QPushButton("Zaloguj")
        self.login_button.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if login_user(username, password):
            self.accept()  # Zamyka okno logowania i zwraca QDialog.DialogCode.Accepted
        else:
            QMessageBox.warning(self, "Błąd", "Nieprawidłowa nazwa użytkownika lub hasło.")

# Klasa okna rejestracji
class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rejestracja")
        self.setGeometry(200, 200, 300, 200)

        # Layout
        layout = QVBoxLayout()

        # Pole do wprowadzenia nazwy użytkownika
        self.username_label = QLabel("Nazwa użytkownika:")
        layout.addWidget(self.username_label)
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # Pole do wprowadzenia hasła
        self.password_label = QLabel("Hasło:")
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Przycisk rejestracji
        self.register_button = QPushButton("Zarejestruj")
        self.register_button.clicked.connect(self.attempt_register)
        layout.addWidget(self.register_button)

        # Przycisk powrotu do logowania
        self.back_to_login_button = QPushButton("Powrót do logowania")
        self.back_to_login_button.clicked.connect(self.back_to_login)
        layout.addWidget(self.back_to_login_button)

        self.setLayout(layout)

    def attempt_register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Błąd", "Nazwa użytkownika i hasło nie mogą być puste.")
            return

        if register_user(username, password):
            QMessageBox.information(self, "Sukces", "Rejestracja zakończona sukcesem.")
            self.accept()  # Zamyka okno rejestracji i zwraca QDialog.DialogCode.Accepted
        else:
            QMessageBox.warning(self, "Błąd", "Użytkownik już istnieje.")

    def back_to_login(self):
        self.reject()  # Zamyka okno rejestracji i zwraca QDialog.DialogCode.Rejected

# Główne okno aplikacji
class FileEncryptionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Szyfrowanie i odszyfrowywanie plików - PyQt6")
        self.setGeometry(100, 100, 800, 600)

        # Ustawienie ikony aplikacji
        self.setWindowIcon(QIcon("icon.png"))

        # Layout
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Przeglądarka plików (QTreeWidget zamiast QFileSystemModel)
        self.file_browser = QTreeWidget(self)
        self.file_browser.setHeaderLabels(["Nazwa pliku"])
        self.file_browser.itemDoubleClicked.connect(self.on_file_selected)
        layout.addWidget(self.file_browser)

        # Przycisk do odświeżania listy plików
        self.refresh_button = QPushButton("Odśwież listę plików")
        self.refresh_button.clicked.connect(self.refresh_file_list)
        layout.addWidget(self.refresh_button)

        # Kafel szyfrowania
        self.encrypt_label = DragDropLabel(
            self,
            on_drop=self.handle_encrypt_drop
        )
        self.encrypt_label.setText("Przeciągnij pliki tutaj, aby je zaszyfrować")
        self.encrypt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.encrypt_label.setStyleSheet("background-color: lightgray; border: 2px dashed black;")
        self.encrypt_label.setFixedHeight(150)
        layout.addWidget(self.encrypt_label)

        # Przycisk odszyfrowywania
        self.decrypt_button = QPushButton("Odszyfruj plik")
        self.decrypt_button.clicked.connect(self.open_decrypt_dialog)
        layout.addWidget(self.decrypt_button)

        # Checkbox do usuwania oryginalnego pliku po zaszyfrowaniu
        self.delete_original_checkbox = QCheckBox("Usuń oryginalny plik po zaszyfrowaniu")
        layout.addWidget(self.delete_original_checkbox)

        # Odśwież listę plików przy starcie
        self.refresh_file_list()

    # Odśwież listę plików
    def refresh_file_list(self):
        self.file_browser.clear()
        current_dir = QDir.currentPath()
        for entry in QDir(current_dir).entryInfoList():
            item = QTreeWidgetItem([entry.fileName()])
            self.file_browser.addTopLevelItem(item)

    # Obsługa podwójnego kliknięcia na pliku
    def on_file_selected(self, item):
        file_name = item.text(0)  # Pobierz nazwę pliku
        file_path = os.path.join(QDir.currentPath(), file_name)  # Pełna ścieżka do pliku

        # Wyświetl okno dialogowe z pytaniem, co zrobić z plikiem
        reply = QMessageBox.question(
            self,
            "Wybór pliku",
            f"Czy chcesz zaszyfrować plik: {file_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Zaszyfruj plik
            encrypted_path, key_path = encrypt_file(
                file_path,
                compress=True,
                password="secure_password",
                use_rsa=False,
                delete_original=self.delete_original_checkbox.isChecked()
            )
            if encrypted_path and os.path.exists(encrypted_path):
                QMessageBox.information(self, "Sukces", f"Plik zaszyfrowano: {encrypted_path}\nKlucz zapisano: {key_path}")
            else:
                QMessageBox.warning(self, "Błąd", f"Nie udało się zaszyfrować pliku: {file_path}")

    # Obsługa przeciągania plików do szyfrowania
    def handle_encrypt_drop(self, files):
        for file_path in files:
            if os.path.isfile(file_path):
                encrypted_path, key_path = encrypt_file(
                    file_path,
                    compress=True,
                    password="secure_password",
                    use_rsa=False,
                    delete_original=self.delete_original_checkbox.isChecked()
                )
                if encrypted_path and os.path.exists(encrypted_path):
                    QMessageBox.information(self, "Sukces", f"Plik zaszyfrowano: {encrypted_path}\nKlucz zapisano: {key_path}")
                else:
                    QMessageBox.warning(self, "Błąd", f"Nie udało się zaszyfrować pliku: {file_path}")

    # Otwórz okno dialogowe odszyfrowywania
    def open_decrypt_dialog(self):
        dialog = DecryptDialog(self)
        dialog.exec()

# Klasa okna dialogowego do odszyfrowywania
class DecryptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Odszyfruj plik")
        self.setGeometry(200, 200, 400, 200)

        # Layout
        layout = QVBoxLayout()

        # Przyciski do załadowania pliku
        self.file_label = QLabel("Nie załadowano pliku do odszyfrowania")
        layout.addWidget(self.file_label)
        self.load_file_button = QPushButton("Załaduj plik do odszyfrowania")
        self.load_file_button.clicked.connect(self.load_file)
        layout.addWidget(self.load_file_button)

        # Przyciski do załadowania klucza
        self.key_label = QLabel("Nie załadowano klucza")
        layout.addWidget(self.key_label)
        self.load_key_button = QPushButton("Załaduj plik klucza")
        self.load_key_button.clicked.connect(self.load_key)
        layout.addWidget(self.load_key_button)

        # Checkbox do usuwania klucza po odszyfrowaniu
        self.delete_keys_checkbox = QCheckBox("Usuń klucz i HMAC po odszyfrowaniu")
        layout.addWidget(self.delete_keys_checkbox)

        # Checkbox do usuwania zaszyfrowanego pliku po odszyfrowaniu
        self.delete_encrypted_checkbox = QCheckBox("Usuń zaszyfrowany plik po odszyfrowaniu")
        layout.addWidget(self.delete_encrypted_checkbox)

        # Przycisk odszyfrowania
        self.decrypt_button = QPushButton("Odszyfruj")
        self.decrypt_button.clicked.connect(self.decrypt)
        self.decrypt_button.setEnabled(False)  # Zablokowane dopóki nie załadowano pliku i klucza
        layout.addWidget(self.decrypt_button)

        self.setLayout(layout)

        # Atrybuty pliku i klucza
        self.file_path = None
        self.key_path = None

    # Załaduj plik do odszyfrowania
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik do odszyfrowania", "", "Encrypted Files (*.enc);;All Files (*)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Załadowano plik: {os.path.basename(file_path)}")
            self.check_ready()

    # Załaduj plik klucza
    def load_key(self):
        key_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik klucza", "", "Key Files (*.key);;All Files (*)")
        if key_path:
            self.key_path = key_path
            self.key_label.setText(f"Załadowano klucz: {os.path.basename(key_path)}")
            self.check_ready()

    # Sprawdź, czy można odszyfrować
    def check_ready(self):
        if self.file_path and self.key_path:
            self.decrypt_button.setEnabled(True)

    # Odszyfruj plik
    def decrypt(self):
        if not self.file_path or not self.key_path:
            QMessageBox.warning(self, "Błąd", "Załaduj zarówno plik, jak i klucz.")
            return

        decrypted_path = decrypt_file(
            self.file_path,
            self.key_path,
            password="secure_password",
            use_rsa=False,
            delete_keys=self.delete_keys_checkbox.isChecked(),
            delete_encrypted=self.delete_encrypted_checkbox.isChecked()
        )
        if os.path.exists(decrypted_path):
            QMessageBox.information(self, "Sukces", f"Plik odszyfrowano: {decrypted_path}")
            self.close()
        else:
            QMessageBox.warning(self, "Błąd", "Nie udało się odszyfrować pliku.")

# Uruchamianie aplikacji
if __name__ == "__main__":
    app = QApplication([])

    # Styl CSS dla aplikacji
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            font-size: 16px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QLabel {
            font-size: 14px;
            color: #333;
        }
        QTreeWidget {
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QCheckBox {
            font-size: 14px;
            color: #333;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QGroupBox {
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 15px;
            font-size: 16px;
            font-weight: bold;
        }
    """)

    while True:
        # Wybór między logowaniem a rejestracją
        choice_dialog = QDialog()
        choice_dialog.setWindowTitle("Wybierz opcję")
        choice_dialog.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()

        login_button = QPushButton("Zaloguj")
        login_button.clicked.connect(lambda: choice_dialog.done(1))
        layout.addWidget(login_button)

        register_button = QPushButton("Zarejestruj")
        register_button.clicked.connect(lambda: choice_dialog.done(2))
        layout.addWidget(register_button)

        choice_dialog.setLayout(layout)

        result = choice_dialog.exec()

        if result == 1:
            # Logowanie
            login_dialog = LoginDialog()
            if login_dialog.exec() == QDialog.DialogCode.Accepted:
                window = FileEncryptionApp()
                window.show()
                app.exec()
                break  # Zakończ pętlę po zalogowaniu
        elif result == 2:
            # Rejestracja
            register_dialog = RegisterDialog()
            register_result = register_dialog.exec()
            if register_result == QDialog.DialogCode.Accepted:
                # Po rejestracji przejdź do logowania
                login_dialog = LoginDialog()
                if login_dialog.exec() == QDialog.DialogCode.Accepted:
                    window = FileEncryptionApp()
                    window.show()
                    app.exec()
                    break  # Zakończ pętlę po zalogowaniu
            elif register_result == QDialog.DialogCode.Rejected:
                # Powrót do logowania
                continue  # Wróć do wyboru między logowaniem a rejestracją
        else:
            break  # Zakończ pętlę, jeśli użytkownik zamknął okno wyboru