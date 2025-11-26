import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QDialog, QDialogButtonBox, QRadioButton, QButtonGroup, QMessageBox
)
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt



# Basit soru diyalogu (tek soruluk)
class QuestionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Soru")
        self.setWindowFlag(Qt.FramelessWindowHint, True)  # kenarlıkları gizle
        self.setModal(True)

        # Soru içeriği (istersen metinleri burada değiştir)
        question_text = "5 + 7 kaç eder?"
        choices = ["10", "11", "12", "13"]
        correct_idx = 2  # '12'

        v = QVBoxLayout(self)
        lbl = QLabel(question_text)
        lbl.setWordWrap(True)
        v.addWidget(lbl)

        self.group = QButtonGroup(self)
        for i, c in enumerate(choices):
            rb = QRadioButton(c)
            self.group.addButton(rb, i)
            v.addWidget(rb)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        v.addWidget(btns)

        def on_accept():
            idx = self.group.checkedId()
            if idx == -1:
                QMessageBox.information(self, "Uyarı", "Lütfen bir seçenek seçin.")
                return
            is_correct = (idx == correct_idx)
            QMessageBox.information(
                self,
                "Sonuç",
                "Doğru! 🎉" if is_correct else "Yanlış. 🙁"
            )
            self.accept()

        btns.accepted.connect(on_accept)
        btns.rejected.connect(self.reject)


# Ana pencere (sadece buton var, tıklayınca soru açılır)
class QuestionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visque - Soru (Bağımsız)")
        self.setWindowFlag(Qt.FramelessWindowHint, True)  # kenarlıkları gizle
        layout = QVBoxLayout(self)

        info = QLabel("Bu ekran yalnızca soru göstermek için bağımsız bir demodur.\n"
                      "Aşağıdaki butona tıklayın.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignLeft)
        layout.addWidget(info)

        btn = QPushButton("Soru Göster")
        btn.clicked.connect(self.show_question)
        layout.addWidget(btn)

    def show_question(self):
        QuestionDialog(self).exec()

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Escape:
            self.showNormal()

def load_styles(app):
    base_path = os.path.join(os.path.dirname(__file__), "styles")
    parts = []
    for filename in ("base.qss", "components.qss"):
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f.read())
        else:
            print("Hatalı Bir Durum Var")
    app.setStyleSheet("\n".join(parts))

def main():
    app = QApplication(sys.argv)
    load_styles(app)
    win = QuestionWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
