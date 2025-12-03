from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QFileDialog,
    QWidget,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QCheckBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QPoint, QRect, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor
import os


class CardWidget(QWidget):
    def __init__(self, accent_color, highlight_color):
        super().__init__()
        self.accent_color = accent_color
        self.highlight_color = highlight_color
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self.card_layout = QVBoxLayout()
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(0)
        self.setLayout(self.card_layout)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(22)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(8)
        self.shadow.setColor(QColor(13, 27, 42, 90))
        self.setGraphicsEffect(self.shadow)

        self.body = QWidget()
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(16, 16, 16, 18)
        self.body_layout.setSpacing(12)
        self.body.setLayout(self.body_layout)

        self.body_base_style = f"""
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(13, 27, 42, 0.12);
            border-bottom-left-radius: 14px;
            border-bottom-right-radius: 14px;
            background-image:
                radial-gradient(circle at 16px 16px, rgba(45, 226, 230, 0.12), transparent 38px),
                radial-gradient(circle at calc(100% - 16px) 16px, rgba(13, 27, 42, 0.10), transparent 38px),
                radial-gradient(circle at 16px calc(100% - 16px), rgba(45, 226, 230, 0.10), transparent 38px),
                radial-gradient(circle at calc(100% - 16px) calc(100% - 16px), rgba(13, 27, 42, 0.08), transparent 38px);
            background-repeat: no-repeat;
        """

        self.body_hover_style = f"""
            background-color: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(13, 27, 42, 0.20);
            border-bottom-left-radius: 16px;
            border-bottom-right-radius: 16px;
            background-image:
                radial-gradient(circle at 16px 16px, rgba(45, 226, 230, 0.18), transparent 38px),
                radial-gradient(circle at calc(100% - 16px) 16px, rgba(13, 27, 42, 0.12), transparent 38px),
                radial-gradient(circle at 16px calc(100% - 16px), rgba(45, 226, 230, 0.14), transparent 38px),
                radial-gradient(circle at calc(100% - 16px) calc(100% - 16px), rgba(13, 27, 42, 0.12), transparent 38px);
            background-repeat: no-repeat;
        """

        self.body.setStyleSheet(self.body_base_style)
        self.body_opacity = QGraphicsOpacityEffect(self.body)
        self.body_opacity.setOpacity(0.0)
        self.body.setGraphicsEffect(self.body_opacity)

        self.hover_duration = 200
        self.lift_distance = 5
        self._hover_geometry_anim = None
        self._shadow_anims = []
        self._intro_anims = []

        self.card_layout.addWidget(self.body)

    def enterEvent(self, event):
        self.body.setStyleSheet(self.body_hover_style)
        self.animate_shadow(target_blur=28, target_y=4)
        self.animate_geometry(lift=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.body.setStyleSheet(self.body_base_style)
        self.animate_shadow(target_blur=22, target_y=8)
        self.animate_geometry(lift=False)
        super().leaveEvent(event)

    def animate_shadow(self, target_blur, target_y):
        blur_anim = QPropertyAnimation(self.shadow, b"blurRadius")
        blur_anim.setDuration(self.hover_duration)
        blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        blur_anim.setStartValue(self.shadow.blurRadius())
        blur_anim.setEndValue(target_blur)

        y_anim = QPropertyAnimation(self.shadow, b"yOffset")
        y_anim.setDuration(self.hover_duration)
        y_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        y_anim.setStartValue(self.shadow.yOffset())
        y_anim.setEndValue(target_y)

        self._shadow_anims = [blur_anim, y_anim]
        for anim in self._shadow_anims:
            anim.start()

    def animate_geometry(self, lift=True):
        if self._hover_geometry_anim and self._hover_geometry_anim.state() == QPropertyAnimation.Running:
            self._hover_geometry_anim.stop()

        current_geometry = self.geometry()
        target_geometry = QRect(current_geometry)
        if lift:
            target_geometry.moveTop(current_geometry.top() - self.lift_distance)
        else:
            target_geometry.moveTop(current_geometry.top() + self.lift_distance)

        self._hover_geometry_anim = QPropertyAnimation(self, b"geometry")
        self._hover_geometry_anim.setDuration(self.hover_duration)
        self._hover_geometry_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_geometry_anim.setStartValue(current_geometry)
        self._hover_geometry_anim.setEndValue(target_geometry)
        self._hover_geometry_anim.start()

    def start_intro_animation(self, delay_ms=0):
        QTimer.singleShot(delay_ms, self._run_intro_animation)

    def _run_intro_animation(self):
        start_pos = self.pos() + QPoint(0, 12)
        end_pos = self.pos()
        self.move(start_pos)

        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(220)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(end_pos)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        opacity_anim = QPropertyAnimation(self.body_opacity, b"opacity")
        opacity_anim.setDuration(220)
        opacity_anim.setStartValue(self.body_opacity.opacity())
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._intro_anims = [pos_anim, opacity_anim]
        for anim in self._intro_anims:
            anim.start()

class FileEncryptionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Szyfrowanie i odszyfrowywanie plików")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QIcon("icon.png"))

        self.init_ui()

    def init_ui(self):
        column_count = 12
        gutter = 16
        vertical_spacing = 22

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(vertical_spacing)

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
            f"color: {accent_color}; text-transform: uppercase; letter-spacing: 1.2px; padding-top: 10px;"
        )
        layout.addWidget(header_label)

        # Podtytuł (H2)
        subheader_label = QLabel("Twoja bezpieczna przestrzeń do szyfrowania plików")
        subheader_label.setFont(QFont(display_font_family, 18, QFont.Weight.DemiBold))
        subheader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subheader_label.setStyleSheet(
            f"color: {accent_color}; letter-spacing: 0.6px; margin-bottom: 10px; padding-top: 6px;"
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

        tags_layout = QHBoxLayout()
        tags_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tags_layout.setSpacing(10)
        tags = [
            {
                "label": "Priorytet",
                "background": "#ffe4e6",  # pastelowy róż
                "color": "#7a1f2a",
            },
            {
                "label": "Nowość",
                "background": "#e0f2fe",  # pastelowy błękit
                "color": "#0f3057",
            },
            {
                "label": "Kluczowe ryzyko",
                "background": "#fff7e0",  # pastelowy żółty
                "color": "#5a3d00",
            },
        ]
        for tag in tags:
            tag_label = QLabel(tag["label"])
            tag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tag_label.setStyleSheet(
                f"""
                background-color: {tag['background']};
                color: {tag['color']};
                padding: 6px 12px;
                border-radius: 12px;
                font-weight: 700;
                letter-spacing: 0.4px;
                text-transform: uppercase;
                border: 1px solid rgba(13, 27, 42, 0.08);
                """
            )
            tags_layout.addWidget(tag_label)

        layout.addLayout(tags_layout)

        cards_grid = QGridLayout()
        cards_grid.setContentsMargins(0, vertical_spacing, 0, 0)
        cards_grid.setHorizontalSpacing(gutter)
        cards_grid.setVerticalSpacing(vertical_spacing)
        for column in range(column_count):
            cards_grid.setColumnStretch(column, 1)
        layout.addLayout(cards_grid)

        file_card, file_card_body = self.create_card(
            title="Przegląd plików",
            icon="📂",
            accent_color=accent_color,
            highlight_color=highlight_color,
            heading_font=QFont(display_font_family, 16, QFont.Weight.Bold),
        )
        cards_grid.addWidget(file_card, 0, 0, 1, 7)
        self.apply_section_animation(file_card, delay_ms=60)

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
        cards_grid.addWidget(actions_card, 0, 7, 1, 5)
        self.apply_section_animation(actions_card, delay_ms=140)

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

        timeline_card, timeline_card_body = self.create_card(
            title="Linia czasu operacji",
            icon="⏳",
            accent_color=accent_color,
            highlight_color=highlight_color,
            heading_font=QFont(display_font_family, 14, QFont.Weight.DemiBold),
        )
        cards_grid.addWidget(timeline_card, 1, 0, 1, column_count)
        self.apply_section_animation(timeline_card, delay_ms=220)

        stages = [
            {"title": "Planowanie", "status": "plan"},
            {"title": "Przygotowanie pliku", "status": "w toku"},
            {"title": "Szyfrowanie", "status": "w toku"},
            {"title": "Weryfikacja", "status": "ukończone"},
            {"title": "Archiwizacja", "status": "ukończone"},
        ]
        timeline_widget = self.create_timeline(stages, accent_color)
        timeline_card_body.addWidget(timeline_widget)

        self.refresh_file_list()

    def create_card(self, title, icon, accent_color, highlight_color, heading_font):
        card = CardWidget(accent_color, highlight_color)

        title_bar = QWidget()
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(14, 12, 14, 12)
        title_bar_layout.setSpacing(8)
        title_bar.setLayout(title_bar_layout)
        title_bar.setStyleSheet(
            f"""
            background-color: {accent_color};
            border-top-left-radius: 14px;
            border-top-right-radius: 14px;
            background-image:
                radial-gradient(circle at 12px 12px, rgba(255, 255, 255, 0.18), transparent 32px),
                radial-gradient(circle at calc(100% - 12px) 12px, rgba(45, 226, 230, 0.18), transparent 32px);
            background-repeat: no-repeat;
            """
        )

        title_label = QLabel(f"{icon} {title}")
        title_label.setFont(heading_font)
        title_label.setStyleSheet("color: white; letter-spacing: 0.8px;")
        title_bar_layout.addWidget(title_label)
        card.card_layout.insertWidget(0, title_bar)

        return card, card.body_layout

    def apply_section_animation(self, widget, delay_ms=0):
        if hasattr(widget, "start_intro_animation"):
            widget.start_intro_animation(delay_ms)

    def create_timeline(self, stages, accent_color):
        timeline_container = QWidget()
        timeline_layout = QHBoxLayout()
        timeline_layout.setContentsMargins(10, 4, 10, 4)
        timeline_layout.setSpacing(0)
        timeline_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timeline_container.setLayout(timeline_layout)

        for index, stage in enumerate(stages):
            stage_widget = QWidget()
            stage_layout = QVBoxLayout()
            stage_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stage_layout.setContentsMargins(8, 4, 8, 4)
            stage_widget.setLayout(stage_layout)

            marker = QWidget()
            marker.setFixedSize(22, 22)
            marker.setStyleSheet(
                f"""
                background-color: {self.status_color(stage['status'])};
                border: 3px solid {accent_color};
                border-radius: 11px;
                """
            )

            label = QLabel(f"{stage['title']}\n({stage['status']})")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                "color: #1f2f46; font-weight: 600; letter-spacing: 0.3px; padding-top: 6px;"
            )

            stage_layout.addWidget(marker)
            stage_layout.addWidget(label)
            timeline_layout.addWidget(stage_widget)

            if index < len(stages) - 1:
                connector = QFrame()
                connector.setFrameShape(QFrame.Shape.HLine)
                connector.setFixedHeight(3)
                connector.setFixedWidth(70)
                connector.setStyleSheet(
                    f"background-color: {accent_color}; border: 1px solid {accent_color};"
                )
                timeline_layout.addWidget(connector)

        return timeline_container

    def status_color(self, status):
        status_styles = {
            "plan": "#cbd5e1",  # jasny szary
            "w toku": "#2de2e6",  # turkus (highlight)
            "ukończone": "#2ecc71",  # zieleń sukcesu
        }
        return status_styles.get(status, "#cbd5e1")

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

