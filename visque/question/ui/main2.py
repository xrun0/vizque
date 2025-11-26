import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
# Çalışma dizininin proje kökü olduğundan emin olalım (sorun yaşarsan alttaki insert satırını açık bırak)
sys.path.insert(0, os.path.dirname(__file__))

from pages.start_page import StartPage
from pages.question_page import QuestionPage
from styles.reloader import QssReloader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo")
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage()
        self.question_page = QuestionPage()

        self.stack.addWidget(self.start_page)     # index 0
        self.stack.addWidget(self.question_page)  # index 1
#
        self.start_page.btn_start.clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )
        self.question_page.btn_next.clicked.connect(self.handle_next_question)

    def handle_next_question(self):
        self.question_page.subtitle.setText("Yeni soru yüklendi (örnek).")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    from PyQt5.QtWidgets import QApplication
    from styles.reloader import QssReloader  # reloader.py içindeki sınıf

    app = QApplication(sys.argv)

    base_dir = Path(__file__).resolve().parent
    qss_path = base_dir / "styles" / "startpage.qss"

    qss_files = [str(qss_path)] if qss_path.exists() else []

    # İlk yükleme + hot-reload
    reloader = QssReloader(app, qss_files)

    w = MainWindow()
    w.resize(1440, 766)
    w.show()
    sys.exit(app.exec_())
