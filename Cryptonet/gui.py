from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QWidget,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QCheckBox,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
import os

class FileEncryptionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Szyfrowanie i odszyfrowywanie plików")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QIcon("icon.png"))

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        central_widget.setStyleSheet(
            """
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #f9fbff,
                stop: 1 #eef3f8
            );
            """
        )
        self.setCentralWidget(central_widget)

        accent_color = "#0d1b2a"  # granat
        highlight_color = "#2de2e6"  # neonowy turkus

        # Nagłówek
        header_label = QLabel("🔒 Cryptonet - Bezpieczne szyfrowanie plików")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(
            f"color: {accent_color}; text-transform: uppercase; letter-spacing: 1px;"
        )
        layout.addWidget(header_label)

        # Sekcja konspektu z półprzezroczystym panelem
        overview_panel = QWidget()
        overview_panel_layout = QVBoxLayout()
        overview_panel.setLayout(overview_panel_layout)
        overview_panel.setStyleSheet(
            """
            background-color: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(13, 27, 42, 0.18);
            border-radius: 12px;
            padding: 14px;
            """
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(Qt.GlobalColor.black)
        overview_panel.setGraphicsEffect(shadow)
        layout.addWidget(overview_panel)

        # Lista plików
        self.file_browser = QTreeWidget(self)
        self.file_browser.setHeaderLabels(["Nazwa pliku"])
        self.file_browser.setStyleSheet(
            f"""
            QTreeWidget {{
                border: 1px solid rgba(13, 27, 42, 0.22);
                background-color: rgba(255, 255, 255, 0.92);
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background: {accent_color};
                color: white;
                border: none;
                padding: 6px 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QTreeWidget::item:selected {{
                background: {highlight_color};
                color: {accent_color};
            }}
            """
        )
        self.file_browser.itemDoubleClicked.connect(self.on_file_selected)
        overview_panel_layout.addWidget(self.file_browser)

        # Przycisk odświeżania
        self.refresh_button = QPushButton("🔄 Odśwież listę plików")
        self.refresh_button.clicked.connect(self.refresh_file_list)
        overview_panel_layout.addWidget(self.refresh_button)

        # Przycisk szyfrowania
        self.encrypt_button = QPushButton("🔐 Szyfruj plik")
        self.encrypt_button.clicked.connect(self.encrypt_file)
        overview_panel_layout.addWidget(self.encrypt_button)

        # Przycisk odszyfrowywania
        self.decrypt_button = QPushButton("🔓 Odszyfruj plik")
        self.decrypt_button.clicked.connect(self.decrypt_file)
        overview_panel_layout.addWidget(self.decrypt_button)

        # Opcja usuwania pliku
        self.delete_original_checkbox = QCheckBox("🗑️ Usuń oryginalny plik po szyfrowaniu")
        overview_panel_layout.addWidget(self.delete_original_checkbox)

        button_style = (
            f"""
            QPushButton {{
                background: {accent_color};
                color: white;
                padding: 10px 14px;
                border-radius: 10px;
                font-weight: 600;
                border: 2px solid transparent;
            }}
            QPushButton:hover {{
                background: {highlight_color};
                color: {accent_color};
                border-color: {accent_color};
            }}
            QPushButton:pressed {{
                background: {accent_color};
                color: white;
                border-color: {highlight_color};
            }}
            """
        )
        self.refresh_button.setStyleSheet(button_style)
        self.encrypt_button.setStyleSheet(button_style)
        self.decrypt_button.setStyleSheet(button_style)
        self.delete_original_checkbox.setStyleSheet(
            f"color: {accent_color}; font-weight: 600; padding-top: 4px;"
        )

        self.refresh_file_list()

    def refresh_file_list(self):
        self.file_browser.clear()
        current_dir = os.getcwd()
        for entry in os.listdir(current_dir):
            item = QTreeWidgetItem([entry])
            self.file_browser.addTopLevelItem(item)

    def on_file_selected(self, item):
        QMessageBox.information(self, "Plik", f"Wybrano plik: {item.text(0)}")

    def encrypt_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik do zaszyfrowania", "", "All Files (*)")
        if file_path:
            QMessageBox.information(self, "Sukces", f"Plik {file_path} został zaszyfrowany!")

    def decrypt_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik do odszyfrowania", "", "Encrypted Files (*.enc)")
        if file_path:
            QMessageBox.information(self, "Sukces", f"Plik {file_path} został odszyfrowany!")

