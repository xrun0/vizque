from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication

class ProjectionView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visque - Projeksiyon")
        self.setAutoFillBackground(True)

        v = QVBoxLayout(self)
        self.label = QLabel("Projeksiyon — efekt bekleniyor")
        self.label.setAlignment(Qt.AlignCenter)
        v.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clear_effect)

        # açılışta tam ekran (ikinci ekran varsa oraya sürükleyebilirsin)
        self.showFullScreen()

    def show_effect(self, cell_id: str, correct: bool, duration_ms: int = 800):
        # basit: arka planı yeşil/kırmızı yap, yazıyı değiştir, sonra geri dön
        color = QColor(0, 160, 60) if correct else QColor(180, 40, 40)
        pal = self.palette()
        pal.setColor(QPalette.Window, color)
        self.setPalette(pal)
        self.label.setText(f"{cell_id} → {'DOĞRU' if correct else 'YANLIŞ'}")
        self.timer.start(duration_ms)

    def clear_effect(self):
        pal = self.palette()
        pal.setColor(QPalette.Window, QApplication.palette().color(QPalette.Window))
        self.setPalette(pal)
        self.label.setText("Projeksiyon — efekt bekleniyor")