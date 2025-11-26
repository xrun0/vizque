# ui/pages/question_page.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap


class QuestionPage(QWidget):
    answerSelected = pyqtSignal(int)
    timeUp = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("questionPage")

        # ==== KÖK LAYOUT ====
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ==== ÜST ÇUBUK (sol: timer, sağ: progress + ?) ====
        top = QHBoxLayout()
        top.setSpacing(8)

        # Sol: Timer
        twrap = QHBoxLayout()
        tw = QWidget(); tw.setLayout(twrap)
        self.timerIcon = QLabel("⏱")
        self.timerIcon.setObjectName("timerIcon")
        self.timerLabel = QLabel("2:00")
        self.timerLabel.setObjectName("timerLabel")
        twrap.addWidget(self.timerIcon)
        twrap.addWidget(self.timerLabel)
        top.addWidget(tw, 0, Qt.AlignLeft)

        top.addStretch(1)

        # Sağ: Progress + soru işareti
        rwrap = QHBoxLayout()
        rw = QWidget(); rw.setLayout(rwrap)
        self.progressLabel = QLabel("1 / 5")
        self.progressLabel.setObjectName("progressLabel")
        self.qmarkLabel = QLabel("?")
        self.qmarkLabel.setObjectName("qmarkLabel")
        rwrap.addWidget(self.progressLabel)
        rwrap.addWidget(self.qmarkLabel)
        top.addWidget(rw, 0, Qt.AlignRight)

        topw = QWidget(); topw.setLayout(top)
        root.addWidget(topw)

        # ==== SORU KUTUSU ====
        self.questionBox = QFrame()
        self.questionBox.setObjectName("questionBox")
        self.questionBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        qlay = QVBoxLayout(self.questionBox)
        qlay.setContentsMargins(24, 16, 24, 16)
        qlay.setSpacing(0)

        self.questionLabel = QLabel("Soru burada görünecek.")
        self.questionLabel.setObjectName("questionLabel")
        self.questionLabel.setAlignment(Qt.AlignCenter)
        self.questionLabel.setWordWrap(True)
        qlay.addWidget(self.questionLabel)

        root.addWidget(self.questionBox)

        # ==== TALİMAT ====
        self.instruction = QLabel("Cevabı olduğunu düşündüğünüz şıkka zıplayabilirsiniz!")
        self.instruction.setObjectName("instruction")
        self.instruction.setAlignment(Qt.AlignCenter)
        root.addWidget(self.instruction)

        # ==== ŞIKLAR ====
        self.answersWrap = QWidget()
        self.answersGrid = QGridLayout(self.answersWrap)
        self.answersGrid.setContentsMargins(0, 0, 0, 0)
        self.answersGrid.setHorizontalSpacing(32)
        self.answersGrid.setVerticalSpacing(8)

        self.optionCards = []
        # 4 placeholder şık
        for i in range(4):
            card, letter = self._make_option(i, f"Seçenek {i+1}")
            self.answersGrid.addWidget(card,   0, i, alignment=Qt.AlignTop)
            self.answersGrid.addWidget(letter, 1, i, alignment=Qt.AlignHCenter)

        root.addWidget(self.answersWrap, 0, Qt.AlignHCenter)
        root.addStretch(1)

        # ==== ALT LOGOLAR (opsiyonel) ====
        logos = QHBoxLayout()
        logos.setSpacing(18)
        self.logo1 = QLabel(); self.logo2 = QLabel(); self.logo3 = QLabel(); self.logo4 = QLabel()
        for l in (self.logo1, self.logo2, self.logo3, self.logo4):
            l.setObjectName("bottomLogo")
            l.setMinimumSize(100, 40)
            l.setAlignment(Qt.AlignCenter)
        logos.addStretch(1); logos.addWidget(self.logo1); logos.addWidget(self.logo2)
        logos.addWidget(self.logo3); logos.addWidget(self.logo4); logos.addStretch(1)
        lw = QWidget(); lw.setObjectName("logosWrap"); lw.setLayout(logos)
        root.addWidget(lw)

        # ==== TIMER STATE ====
        self._remaining = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    # ---------- PUBLIC API ----------

    def setQuestion(self, text: str, options: list, progress: tuple = None, timer_text: str = None):
        """
        Soru ve 4 şık metnini günceller.
        progress: (current, total) -> "1 / 5"
        timer_text: "2:00" gibi (isteğe bağlı; normalde start/reset ile güncellenir)
        """
        self.questionLabel.setText(text or "")

        if options and len(options) == 4:
            for i, card in enumerate(self.optionCards):
                lbl = card.findChild(QLabel, "optionText")
                if lbl:
                    lbl.setText(options[i])
                # durumunu sıfırla
                card.setProperty("state", "normal")
                card.style().unpolish(card); card.style().polish(card); card.update()

        if progress:
            self.progressLabel.setText(f"{progress[0]} / {progress[1]}")

        if timer_text:
            self.timerLabel.setText(timer_text)

    def setLogos(self, paths: list):
        labels = [self.logo1, self.logo2, self.logo3, self.logo4]
        for i, p in enumerate(paths[:4]):
            pm = QPixmap(p)
            if not pm.isNull():
                labels[i].setPixmap(pm.scaledToHeight(40, Qt.SmoothTransformation))

    # Durum (QSS ile renklendirmek için)
    def setAnswerState(self, index: int, state: str):
        if 0 <= index < len(self.optionCards):
            w = self.optionCards[index]
            w.setProperty("state", state)  # "normal" | "selected" | "correct" | "wrong"
            w.style().unpolish(w); w.style().polish(w); w.update()

    # ---------- TIMER API ----------
    def startTimer(self, seconds: int):
        self._remaining = max(0, int(seconds))
        self._render_time()
        self._timer.start(1000)

    def resetTimer(self, seconds: int):
        self._timer.stop()
        self._remaining = max(0, int(seconds))
        self._render_time()

    def stopTimer(self):
        if self._timer.isActive():
            self._timer.stop()

    def _tick(self):
        if self._remaining > 0:
            self._remaining -= 1
            self._render_time()
        if self._remaining == 0:
            self.stopTimer()
            self.timeUp.emit()

    def _render_time(self):
        m, s = divmod(self._remaining, 60)
        self.timerLabel.setText(f"{m}:{s:02d}")

    # Sayfa gizlenirse sayaç dursun (isteğe bağlı ama iyi pratik)
    def hideEvent(self, e):
        self.stopTimer()
        super().hideEvent(e)

    # ---------- INTERNAL: OPTION FACTORY & EVENTS ----------
    def _make_option(self, index: int, text: str):
        print(text)
        card = QFrame()
        card.setObjectName("optionCard")
        card.setProperty("optIndex", index)
        card.setProperty("state", "normal")
        card.setCursor(Qt.PointingHandCursor)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(0)

        lbl = QLabel(text)
        lbl.setObjectName("optionText")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lay.addWidget(lbl)

        card.installEventFilter(self)
        lbl.installEventFilter(self)

        letter = QLabel(chr(ord('A') + index))
        letter.setObjectName("optionLetter")
        letter.setAlignment(Qt.AlignCenter)

        self.optionCards.append(card)
        return card, letter

    def eventFilter(self, obj, event):
        if obj in getattr(self, "optionCards", []):
            if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                idx = int(obj.property("optIndex"))
                self.answerSelected.emit(idx)
                return True
        return super().eventFilter(obj, event)

    def on_camera_choice(self, index: int):
        """
        Kameradan gelen index'e göre şık seç.
        MainWindow şu anda:
          0 -> seçim yok
          1 -> A
          2 -> B
          3 -> C
          4 -> D
        Bizim içerde kullanacağımız index 0..3 olmalı.
        """
    
        # 1) Önce tüm şıkları normal hale getir (QSS state temizleme)
        for i in range(len(self.optionCards)):
            self.setAnswerState(i, "normal")
    
        # 2) 0 ise "hiçbir şık seçme" anlamına gelsin → sadece temizleyip çık
        if index == 0:
            return
    
        # 3) Kameradan gelen 1..4 değerini 0..3'e çevir
        opt_idx = index - 1
    
        # 4) Geçerli index mi kontrol et
        if 0 <= opt_idx < len(self.optionCards):
            # 4a) Görsel olarak seçili göster
            self.setAnswerState(opt_idx, "selected")
    
            # 4b) Sanki kullanıcı o karta tıklamış gibi sinyali gönder
            self.answerSelected.emit(opt_idx)
