import sys, os
import json
import cv2
import time
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import QThread, pyqtSlot, QTimer,QUrl
from PyQt5.QtMultimedia import QSoundEffect

from camera_worker import CameraWorker
from animation import GeriSayimLabel
# Çalışma dizininin proje kökü olduğundan emin olalım
sys.path.insert(0, os.path.dirname(__file__))

from pages.start_page import StartPage
from pages.question_page import QuestionPage
from pages.result_page import ResultPage
from styles.reloader import QssReloader
from projection_window import ProjectionWindow
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo")
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # --- Sayfalar ---
        self.start_page = StartPage()
        self.question_page = QuestionPage()
        self.result_page = ResultPage()
        self.projection = ProjectionWindow()
        self.geri_sayim = GeriSayimLabel(self)
        self.in_feedback = False
        # Projeksiyonu 2. ekrana al
        screens = QApplication.screens()
        if len(screens) > 1:
            geom = screens[1].geometry()
            self.projection.setGeometry(geom)
        self.projection.showFullScreen()

        self.stack.addWidget(self.start_page)      # index 0
        self.stack.addWidget(self.question_page)   # index 1
        self.stack.addWidget(self.result_page)     # index 2

        # --- Kamera ---
        self.camera_thread = None
        self.camera_worker = None

        # --- Quiz state ---
        self.questions = []
        self.duration_sec = 10        # Her soru için varsayılan 10 sn
        self.current_idx = 0
        self.correct_count = 0
        self.wrong_count = 0

        # Kamera seçimi ile ilgili state
        self.selected_choice = None       # 1..4, şu anda seçili olan şık
        self.last_detected_cell = None    # (row, col) bilgisi

        # --- Sinyaller ---
        self.start_page.cardClicked.connect(self.goto_question_page)
        # Süre bitince artık goto_result değil, on_time_up çalışacak
        self.question_page.timeUp.connect(self.on_time_up)
        self.result_page.goHome.connect(self.back_to_start)

        # Mouse ile tıklama olursa hâlâ çalışsın
        self.question_page.answerSelected.connect(self.on_answer_selected)

        base_dir = Path(__file__).resolve().parent
        sound_dir = base_dir / "sounds"

        self.sound_correct = self._create_sound(sound_dir / "correct.wav")
        self.sound_wrong   = self._create_sound(sound_dir / "wrong.wav")
        self.sound_result  = self._create_sound(sound_dir / "victory.wav")
        self.sound_countdown = self._create_sound(sound_dir / "countdown.wav")

        if self.sound_countdown:
            self.sound_countdown.setLoopCount(QSoundEffect.Infinite)
            self.sound_countdown.setVolume(0.4)  # 40%

    # =========================
    #   SAYFA GEÇİŞLERİ
    # =========================
    def goto_question_page(self):
        # Kamerayı aç
        self.setup_camera()

        # (İstersen debug görüntü)
        self.camera_worker.frameReady.connect(self.on_debug_frame)
        self.geri_sayim.baslat()
        QTimer.singleShot(3000, self.camera_background_ready)
        # Soruları yükle

    def camera_background_ready(self):
        self.load_questions()
        print("Kart tıklandı, QuestionPage açılıyor...")
        self.stack.setCurrentWidget(self.question_page)
        self.show_current_question()
        self.start_countdown_sound()

    def load_questions(self):
        base_dir = Path(__file__).resolve().parent
        qpath = base_dir / "questions" / "questions.json"
        with qpath.open("r", encoding="utf-8") as f:
            data = json.load(f)

        all_questions = data.get("questions", [])
        self.questions = random.sample(all_questions, 5)

        # Süre
        self.duration_sec = int(data.get("duration_sec", 10))

        # Sayaçlar
        self.current_idx = 0
        self.correct_count = 0
        self.wrong_count = 0


    def reset_quiz(self):
        self.current_idx = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.selected_choice = None
        self.last_detected_cell = None

    def show_current_question(self):
        # Tüm sorular bittiyse sonuç ekranına git
        if not (0 <= self.current_idx < len(self.questions)):
            return self.goto_result()
        self.start_countdown_sound()
        # Yeni soru: seçim state'lerini sıfırla
        self.selected_choice = None
        self.last_detected_cell = None
        # Projeksiyon gridini temizle
        self.projection.setSelectedCell(None, None)

        q = self.questions[self.current_idx]
        text = q["text"]
        options = q["options"]
        progress = (self.current_idx + 1, len(self.questions))

        self.question_page.setQuestion(text, options, progress=progress)
        self.question_page.resetTimer(self.duration_sec)
        self.question_page.startTimer(self.duration_sec)

    def on_answer_selected(self, idx: int):
        """
        Bu fonksiyon daha çok mouse ile tıklama senaryosu için.
        Kamera akışı için asıl mantık on_time_up içinde.
        """
        q = self.questions[self.current_idx]
        if idx == int(q["answer"]):
            self.correct_count += 1
        else:
            self.wrong_count += 1

        # Sonraki soruya geç
        self.stop_countdown_sound()
        self.current_idx += 1
        if self.current_idx < len(self.questions):
            self.show_current_question()
        else:
            self.stop_camera()
            self.goto_result()

    def goto_result(self):
        # Projeksiyonda tam ekran GIF oynat
        self.projection.showFullResultGif()
        self.play_result_sound()
        print("Quiz bitti -> Result sayfasına geçiliyor")
        self.result_page.setResults(
            self.correct_count,
            self.wrong_count
        )
        self.stack.setCurrentWidget(self.result_page)

    def back_to_start(self):
        self.reset_quiz()
        self.projection.clearResultGif()
        self.stack.setCurrentWidget(self.start_page)

    # =========================
    #   KAMERA & DEBUG
    # =========================
    def on_debug_frame(self, renkli, thresed):
        cv2.imshow("DEBUG", renkli)
        cv2.imshow("DEBUG2", thresed)
        cv2.waitKey(1)

    def setup_camera(self):
        """Kamerayı başlatmak için tek yer burası olsun."""
        self.camera_thread = QThread(self)
        self.camera_worker = CameraWorker()

        self.camera_worker.moveToThread(self.camera_thread)

        # Thread başladığında worker.start çalışsın
        self.camera_thread.started.connect(self.camera_worker.start)

        # Worker bitince thread de bitsin
        self.camera_worker.finished.connect(self.camera_thread.quit)

        # Kameradan gelen veriyi dinle
        self.camera_worker.dataReady.connect(self.on_camera_data)

        # Thread tamamen bitince bellek temizliği
        self.camera_thread.finished.connect(self.camera_thread.deleteLater)

        self.camera_thread.start()

    def stop_camera(self):
        if not self.camera_worker:
            return
        print("Kamera durduruluyor...")
        self.camera_worker.stop()   # sadece bayrak indir, thread kendi kendini kapatacak
        self.camera_worker = None
        print("Kamera durdu.")

    @pyqtSlot(object)
    def on_camera_data(self, sendData: object):
        """
        Kameradan gelen veriyi işler:
        - Sadece soru sayfasındayken çalışır
        - Çocuğun bastığı kareye göre:
        - BU NOKTADA HENÜZ CEVAP SAYILMAZ.
          Cevap sadece süre bittiğinde (on_time_up) değerlendirilir.
        """

        # 1) Sadece soru sayfasındayken kamera verisini dikkate al        
        if self.stack.currentWidget() != self.question_page:
            return

        if self.in_feedback:
            return
        
        # Hiçbir şey algılanmadıysa: seçimleri temizle
        if not sendData.get("detected", False):
            self.selected_choice = None
            self.last_detected_cell = None
            self.question_page.on_camera_choice(0)          # tüm şıkları normal yap
            self.projection.setSelectedCell(None, None)     # projeksiyonda da boş
            return

        # row/col -> şık (1..4) eşleştirmesi
        mapping = {
            (0, 0): 1,  # A
            (0, 1): 2,  # B
            (1, 0): 3,  # C
            (1, 1): 4,  # D
        }

        key = (sendData.get("row"), sendData.get("col"))
        choice = mapping.get(key)
        if choice is None:
            self.selected_choice = None
            self.last_detected_cell = None
            return

        # State'i güncelle
        self.selected_choice = choice      # 1..4
        self.last_detected_cell = key      # (row, col)

        # 1. ekranda ilgili şıkkı seçili göster
        self.question_page.on_camera_choice(choice)

        # 2. ekranda seçili kareyi PNG ile göster
        row, col = key
        self.projection.setSelectedCell(row, col)

    # =========================
    #   SÜRE BİTİNCE CEVAP DEĞERLENDİRME
    # =========================
    def on_time_up(self):
        """
        Her soru için süre bittiğinde:
          - Eğer bir şık seçilmişse, o şıkkı doğru/yanlış olarak değerlendir.
          - 1. ekranda (QuestionPage) doğru/yanlış renklendirmesini göster.
          - 2. ekranda (ProjectionWindow) doğru/yanlış PNG'sini göster.
          - Kısa bir beklemeden sonra sonraki soruya geç.
        """
        print("Süre bitti, cevap değerlendiriliyor...")

        q = self.questions[self.current_idx]
        correct_idx = int(q["answer"])   # 0..3
        correct_choice = correct_idx + 1 # 1..4

        # choice -> (row,col) map'i
        choice_to_cell = {
            1: (0, 0),
            2: (0, 1),
            3: (1, 0),
            4: (1, 1),
        }
        self.stop_countdown_sound()
        self.in_feedback = True
        # Hiç seçim yapılmadıysa: yanlış kabul et
        if self.selected_choice is None:
            print("Hiç seçim yapılmadı, yanlış sayılıyor.")
            # UI'de sadece doğru şıkkı yeşil gösterebiliriz
            self.question_page.setAnswerState(correct_idx, "correct")

            # Projeksiyonda doğru kareyi 'correct' PNG ile göster
            row, col = choice_to_cell.get(correct_choice, (None, None))
            self.projection.showResultCell(row, col, is_correct=True)

        else:
            sel_choice = self.selected_choice   # 1..4
            sel_idx = sel_choice - 1            # 0..3

            if sel_choice == correct_choice:
                print("Seçilen şık DOĞRU.")
                # UI
                self.question_page.setAnswerState(sel_idx, "correct")
                # Projeksiyon
                if self.last_detected_cell:
                    row, col = self.last_detected_cell
                else:
                    row, col = choice_to_cell.get(sel_choice, (None, None))
                self.projection.showResultCell(row, col, is_correct=True)
                self.correct_count += 1
                self.play_correct_sound()

            else:
                print("Seçilen şık YANLIŞ.")
                # UI: seçilen kırmızı, doğru yeşil
                self.question_page.setAnswerState(sel_idx, "wrong")
                self.question_page.setAnswerState(correct_idx, "correct")

                # --- Projeksiyon tarafı ---

                # Yanlış seçilen kare (çocuğun durduğu yer)
                if self.last_detected_cell:
                    wrong_row, wrong_col = self.last_detected_cell
                else:
                    wrong_row, wrong_col = choice_to_cell.get(sel_choice, (None, None))

                # Doğru kare
                correct_row, correct_col = choice_to_cell.get(correct_choice, (None, None))

                # Hem yanlış hem doğru kareyi aynı anda göster
                self.projection.showWrongAndCorrect(
                    wrong_row, wrong_col,
                    correct_row, correct_col
                )

                self.wrong_count += 1
                self.play_wrong_sound()
        # Küçük bir gecikmeden sonra sonraki soruya geçelim (1 sn)
        def go_next():
            self.in_feedback = False
            self.current_idx += 1
            if self.current_idx < len(self.questions):
                self.show_current_question()
            else:
                self.stop_camera()
                self.goto_result()

        QTimer.singleShot(4000, go_next)
    # =========================
    #   SES OYNATICILARI

    def _create_sound(self, path: Path):
        """Verilen dosya yolundan bir QSoundEffect oluşturur."""
        effect = QSoundEffect(self)
        effect.setSource(QUrl.fromLocalFile(str(path)))
        effect.setVolume(0.5)  # 0.0 - 1.0 arası
        return effect

    def play_correct_sound(self):
        if self.sound_correct:
            self.sound_correct.stop()
            self.sound_correct.play()

    def play_wrong_sound(self):
        if self.sound_wrong:
            self.sound_wrong.stop()
            self.sound_wrong.play()

    def start_countdown_sound(self):
        if self.sound_countdown:
            self.sound_countdown.stop()
            self.sound_countdown.play()

    def stop_countdown_sound(self):
        if self.sound_countdown:
            self.sound_countdown.stop()


    def play_result_sound(self):
        if self.sound_result:
            self.sound_result.stop()
            self.sound_result.play()

    # =========================
    #   PENCERE KAPANIRKEN
    # =========================
    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)


# Main
if __name__ == "__main__":
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
