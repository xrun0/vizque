# visque/question/question_stacked.py
import sys, os
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QButtonGroup, QFrame, QMessageBox
)

# ---- (İstersen) QSS yükleyici: styles/base.qss ve components.qss otomatik yüklenir ----
def load_styles(app):
    base_path = os.path.join(os.path.dirname(__file__), "styles")
    if not os.path.isdir(base_path):
        return
    parts = []
    for fname in ("base.qss", "components.qss"):
        fpath = os.path.join(base_path, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                parts.append(f.read())
    if parts:
        app.setStyleSheet("\n".join(parts))

class QuestionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visque - Tek Pencere Quiz")
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        #self.showFullScreen()

        # ---- Durum değişkenleri ----
        self.questions = [
            {"text": "5 + 7 kaç eder?", "choices": ["10", "11", "12", "13"], "correct_idx": 2},
            {"text": "En küçük asal sayı hangisidir?", "choices": ["0", "1", "2", "3"], "correct_idx": 2},
            {"text": "Işık yılı hangi büyüklüğü ölçer?", "choices": ["Zaman", "Hız", "Uzaklık", "Kütle"], "correct_idx": 2},
        ]
        self.current_index = 0
        self.score = 0
        self.group = None  # QButtonGroup (soru sayfasında oluşturulacak)

        # ---- Kök yerleşim ve yığın (stack) ----
        root = QVBoxLayout(self)
        self.stack = QStackedWidget(self)
        root.addWidget(self.stack)

        # ---- 3 sayfa: Start, Quiz, Summary ----
        self.startPage = self.build_start_page()
        self.quizPage  = self.build_quiz_page()
        self.summaryPage = self.build_summary_page()

        self.stack.addWidget(self.startPage)
        self.stack.addWidget(self.quizPage)
        self.stack.addWidget(self.summaryPage)

        self.stack.setCurrentWidget(self.startPage)

    # -------------------- SAYFA 1: START --------------------
    
    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Escape:
            self.showNormal()

    def build_start_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(16)

        title = QLabel("Quiz'e Hoş Geldin")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        subtitle = QLabel("Başla düğmesine bas; sorular aynı pencerede gösterilecek.")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)

        startBtn = QPushButton("Başla")
        startBtn.setProperty("variant", "primary")
        startBtn.setFixedHeight(44)
        startBtn.clicked.connect(self.on_start)

        v.addWidget(title)
        v.addWidget(subtitle)
        v.addStretch(1)
        v.addWidget(startBtn, alignment=Qt.AlignRight)
        return page

    # -------------------- SAYFA 2: QUIZ --------------------
    def build_quiz_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setSpacing(16)

        # Panel (görsel ayrım için)
        panel = QFrame()
        panel.setProperty("panel", True)
        panel.setFrameShape(QFrame.NoFrame)
        pv = QVBoxLayout(panel)
        pv.setContentsMargins(24, 24, 24, 24)
        pv.setSpacing(16)

        # Soru metni
        self.lblQuestion = QLabel("Soru metni burada görünecek")
        self.lblQuestion.setWordWrap(True)
        self.lblQuestion.setStyleSheet("font-size: 20px;")
        pv.addWidget(self.lblQuestion)

        # Seçenekler için dikey alan
        self.choicesWrap = QWidget()
        self.choicesLayout = QVBoxLayout(self.choicesWrap)
        self.choicesLayout.setSpacing(10)
        self.choicesLayout.setContentsMargins(0, 0, 0, 0)
        pv.addWidget(self.choicesWrap)

        outer.addWidget(panel)

        # Alt buton çubuğu
        bar = QHBoxLayout()
        bar.addStretch(1)

        self.btnPrev = QPushButton("Geri")
        self.btnPrev.setProperty("variant", "secondary")
        self.btnPrev.setFixedHeight(40)
        self.btnPrev.clicked.connect(self.on_prev)
        self.btnPrev.setEnabled(False)  # ilk soruda pasif

        self.btnNext = QPushButton("Sonraki")
        self.btnNext.setProperty("variant", "primary")
        self.btnNext.setFixedHeight(40)
        self.btnNext.setEnabled(False)  # seçilene kadar pasif
        self.btnNext.clicked.connect(self.on_next)

        bar.addWidget(self.btnPrev)
        bar.addWidget(self.btnNext)
        outer.addLayout(bar)
        return page

    # -------------------- SAYFA 3: SUMMARY --------------------
    def build_summary_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(16)

        title = QLabel("Bitti 🎉")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        self.lblSummary = QLabel("Skor: 0 / 0")
        self.lblSummary.setStyleSheet("font-size: 18px; color: #374151;")

        btnRow = QHBoxLayout()
        btnRow.addStretch(1)
        btnRestart = QPushButton("Başa Dön")
        btnRestart.setProperty("variant", "secondary")
        btnRestart.setFixedHeight(40)
        btnRestart.clicked.connect(self.on_restart)
        btnRow.addWidget(btnRestart)

        v.addWidget(title)
        v.addWidget(self.lblSummary)
        v.addStretch(1)
        v.addLayout(btnRow)
        return page

    # -------------------- AKIŞ EYLEMLERİ --------------------
    def on_start(self):
        self.current_index = 0
        self.score = 0
        self.render_question(self.current_index)
        self.stack.setCurrentWidget(self.quizPage)

    def on_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.render_question(self.current_index)

    def on_next(self):
        # Seçim yapılmış mı?
        selected = self.group.checkedId() if self.group else -1
        if selected == -1:
            QMessageBox.information(self, "Uyarı", "Lütfen bir seçenek seçin.")
            return

        # Puanla
        if selected == self.questions[self.current_index]["correct_idx"]:
            self.score += 1

        # Sıradaki
        self.current_index += 1
        if self.current_index >= len(self.questions):
            # Özet sayfası
            self.lblSummary.setText(f"Skor: {self.score} / {len(self.questions)}")
            self.stack.setCurrentWidget(self.summaryPage)
        else:
            self.render_question(self.current_index)

    def on_restart(self):
        self.stack.setCurrentWidget(self.startPage)

    # -------------------- SORU RENDER --------------------
    def clear_choices(self):
        # mevcut radio butonlarını temizle
        while self.choicesLayout.count():
            item = self.choicesLayout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

    def render_question(self, idx: int):
        q = self.questions[idx]
        self.lblQuestion.setText(q["text"])
        self.clear_choices()
        self.group = QButtonGroup(self)

        # radio butonlarını oluştur
        for i, choice in enumerate(q["choices"]):
            rb = QRadioButton(choice)
            rb.toggled.connect(self.on_choice_toggled)
            self.group.addButton(rb, i)
            self.choicesLayout.addWidget(rb)

        # buton durumları
        self.btnPrev.setEnabled(idx > 0)
        self.btnNext.setEnabled(False)

    def on_choice_toggled(self, checked: bool):
        if checked:
            self.btnNext.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    load_styles(app)  # styles klasörün yoksa sorun değil, atlar
    win = QuestionWindow()
    win.show()  # Tam ekran istersen: win.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()