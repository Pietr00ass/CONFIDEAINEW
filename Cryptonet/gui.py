from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
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
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)

        display_font_family = "Playfair Display"
        text_font_family = "Inter"

        central_widget = QWidget()
        central_widget.setLayout(layout)
        central_widget.setStyleSheet(
            """
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #f9fbff,
                stop: 1 #eef3f8
            );
            font-family: '%s', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6em;
            color: #0d1b2a;
            """
            % text_font_family
        )
        self.setCentralWidget(central_widget)

        accent_color = "#0d1b2a"  # granat
        highlight_color = "#2de2e6"  # neonowy turkus

        # Nagłówek
        header_label = QLabel("🔒 Cryptonet - Bezpieczne szyfrowanie plików")
        header_label.setFont(QFont(display_font_family, 26, QFont.Weight.Black))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(
            f"color: {accent_color}; text-transform: uppercase; letter-spacing: 1.2px;"
        )
        layout.addWidget(header_label)

        # Podtytuł (H2)
        subheader_label = QLabel("Twoja bezpieczna przestrzeń do szyfrowania plików")
        subheader_label.setFont(QFont(display_font_family, 18, QFont.Weight.DemiBold))
        subheader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subheader_label.setStyleSheet(
            f"color: {accent_color}; letter-spacing: 0.6px; margin-bottom: 6px;"
        )
        layout.addWidget(subheader_label)

        # Opis sekcji (H3)
        section_hint = QLabel(
            "Korzystaj z panelu poniżej, aby przeglądać pliki i uruchamiać bezpieczne operacje."
        )
        hint_font = QFont(text_font_family, 11)
        hint_font.setWeight(QFont.Weight.Medium)
        section_hint.setFont(hint_font)
        section_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        section_hint.setStyleSheet(
            "color: #1f2f46; letter-spacing: 0.3px; margin-bottom: 14px;"
        )
        layout.addWidget(section_hint)

        cards_layout = QVBoxLayout()
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(18)
        layout.addLayout(cards_layout)

        file_card, file_card_body = self.create_card(
            title="Przegląd plików",
            icon="📂",
            accent_color=accent_color,
            highlight_color=highlight_color,
            heading_font=QFont(display_font_family, 16, QFont.Weight.Bold),
        )
        cards_layout.addWidget(file_card)

        # Lista plików
        self.file_browser = QTreeWidget(self)
        self.file_browser.setHeaderLabels(["Nazwa pliku"])
        self.file_browser.setStyleSheet(
            f"""
            QTreeWidget {{
                border: 1px solid rgba(13, 27, 42, 0.22);
                background-color: rgba(255, 255, 255, 0.92);
                border-radius: 8px;
                padding: 6px;
                font-family: '{text_font_family}', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10.5pt;
                line-height: 1.5em;
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
        file_card_body.addWidget(self.file_browser)

        actions_card, actions_card_body = self.create_card(
            title="Akcje szyfrowania",
            icon="⚙️",
            accent_color=accent_color,
            highlight_color=highlight_color,
            heading_font=QFont(display_font_family, 14, QFont.Weight.DemiBold),
        )
        cards_layout.addWidget(actions_card)

        # Przycisk odświeżania
        self.refresh_button = QPushButton("🔄 Odśwież listę plików")
        self.refresh_button.clicked.connect(self.refresh_file_list)
        actions_card_body.addWidget(self.refresh_button)

        # Przycisk szyfrowania
        self.encrypt_button = QPushButton("🔐 Szyfruj plik")
        self.encrypt_button.clicked.connect(self.encrypt_file)
        actions_card_body.addWidget(self.encrypt_button)

        # Przycisk odszyfrowywania
        self.decrypt_button = QPushButton("🔓 Odszyfruj plik")
        self.decrypt_button.clicked.connect(self.decrypt_file)
        actions_card_body.addWidget(self.decrypt_button)

        # Opcja usuwania pliku
        self.delete_original_checkbox = QCheckBox("🗑️ Usuń oryginalny plik po szyfrowaniu")
        actions_card_body.addWidget(self.delete_original_checkbox)

        button_style = (
            f"""
            QPushButton {{
                background: {accent_color};
                color: white;
                padding: 10px 14px;
                border-radius: 10px;
                font-weight: 600;
                border: 2px solid transparent;
                font-family: '{text_font_family}', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                font-size: 11pt;
                letter-spacing: 0.3px;
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

    def create_card(self, title, icon, accent_color, highlight_color, heading_font):
        card = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        card.setLayout(card_layout)

        title_bar = QWidget()
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(14, 12, 14, 12)
        title_bar_layout.setSpacing(8)
        title_bar.setLayout(title_bar_layout)
        title_bar.setStyleSheet(
            f"background-color: {accent_color}; border-top-left-radius: 14px; border-top-right-radius: 14px;"
        )

        title_label = QLabel(f"{icon} {title}")
        title_label.setFont(heading_font)
        title_label.setStyleSheet("color: white; letter-spacing: 0.8px;")
        title_bar_layout.addWidget(title_label)
        card_layout.addWidget(title_bar)

        body = QWidget()
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(16, 16, 16, 18)
        body_layout.setSpacing(12)
        body.setLayout(body_layout)
        body.setStyleSheet(
            f"""
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(13, 27, 42, 0.12);
            border-bottom-left-radius: 14px;
            border-bottom-right-radius: 14px;
            """
        )
        card_layout.addWidget(body)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(Qt.GlobalColor.black)
        card.setGraphicsEffect(shadow)

        return card, body_layout

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

