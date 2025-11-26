import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import QThread, pyqtSlot
from camera_worker import CameraWorker
# Çalışma dizininin proje kökü olduğundan emin olalım (sorun yaşarsan alttaki insert satırını açık bırak)
sys.path.insert(0, os.path.dirname(__file__))

from pages.start_page import StartPage
from pages.question_page import QuestionPage
from pages.result_page import ResultPage
from styles.reloader import QssReloader
import json
import cv2
from PyQt5.QtCore import QTimer
import time
from projection_window import ProjectionWindow
from PyQt5.QtWidgets import QApplication

class MainWindow(QMainWindow):
    #inital Method
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo")
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage()
        self.question_page = QuestionPage()
        self.result_page = ResultPage()
        self.projection = ProjectionWindow()

        screens = QApplication.screens()
        if len(screens) > 1:
            geom = screens[1].geometry()
            self.projection.setGeometry(geom)
        self.projection.showFullScreen()

        self.stack.addWidget(self.start_page)     # index 0
        self.stack.addWidget(self.question_page)  # index 1
        self.stack.addWidget(self.result_page)  # index 1


        self.camera_thread = None
        self.camera_worker = None
        self.resultGifLabel = None
        
            
        self.questions = []
        self.duration_sec = 12
        self.current_idx = 0
        self.correct_count = 0
        self.wrong_count = 0

        self.last_camera_choice = None      # Son algılanan şık (1..4)
        self.last_choice_time = 0           # Bu şık ilk ne zaman görüldü (ms cinsinden)
        self.choice_confirm_delay = 5000     # KAÇ ms beklenir -> 500ms = 0.5 saniye

        
        self.start_page.cardClicked.connect(self.goto_question_page)
        self.question_page.timeUp.connect(self.goto_result)
        self.result_page.goHome.connect(self.back_to_start)

        self.question_page.answerSelected.connect(self.on_answer_selected)
        #kamera test kısmı

#Sayfalar ve İşlemleri
    def goto_question_page(self):
        self.setup_camera()
        #self.camera_worker.frameReady.connect(self.on_debug_frame)
        self.load_questions()
        print("Kart tıklandı, QuestionPage açılıyor...")
        self.stack.setCurrentWidget(self.question_page)
        self.question_page.startTimer(32)
        self.show_current_question()

    def load_questions(self):
        base_dir = Path(__file__).resolve().parent
        qpath = base_dir / "questions" / "questions.json"
        with qpath.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self.questions = data.get("questions", [])
        self.duration_sec = int(data.get("duration_sec", 12))
        self.current_idx = 0
        self.correct_count = 0
        self.wrong_count = 0

    def reset_quiz(self):
        self.current_idx = 0
        self.correct_count = 0
        self.wrong_count = 0

    def show_current_question(self):
        if not (0 <= self.current_idx < len(self.questions)):
            return self.goto_result()

        q = self.questions[self.current_idx]
        text = q["text"]
        options = q["options"]
        progress = (self.current_idx + 1, len(self.questions))

        self.question_page.setQuestion(text, options, progress=progress)
        self.question_page.resetTimer(self.duration_sec)
        self.question_page.startTimer(self.duration_sec)
    
    def on_answer_selected(self, idx: int):
        q = self.questions[self.current_idx]
        if idx == int(q["answer"]):
            self.correct_count += 1
        else:
            self.wrong_count += 1
        # sonraki soruya geç
        self.current_idx += 1
        if self.current_idx < len(self.questions):
            self.show_current_question()
        else:
            self.stop_camera()
            self.goto_result(self.correct_count, self.wrong_count)

    def handle_next_question(self):
        self.question_page.subtitle.setText("Yeni soru yüklendi (örnek).")

    def goto_result(self,correct_count=None, wrong_count=None):
        self.projection.showFullResultGif()
        print("Süre bitti -> Result sayfasına geçiliyor")
        self.result_page.setResults(
            self.correct_count,
            self.wrong_count
        )
        self.stack.setCurrentWidget(self.result_page)

    def back_to_start(self):
        self.reset_quiz()
        self.projection.clearResultGif()
        self.stack.setCurrentWidget(self.start_page)
    
#kamera ve Debug kısmı
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

        # Debug görüntü istiyorsan:
        # self.camera_worker.frameReady.connect(self.on_debug_frame)

        # Kameradan gelen veriyi dinle
        self.camera_worker.dataReady.connect(self.on_camera_data)

        # Thread tamamen bitince bellek temizliği
        self.camera_thread.finished.connect(self.camera_thread.deleteLater)

        self.camera_thread.start()

    def stop_camera(self):
        print("Kamera durduruluyor...")
        self.camera_worker.stop()   # sadece bayrak indir, thread kendi kendini kapatacak
        self.camera_worker = None
        print("Kamera durdu.")


    @pyqtSlot(object)
    def on_camera_data(self, sendData: object):
        # 1) Sadece soru sayfasındayken kamera verisini dikkate al
        if self.stack.currentWidget() != self.question_page:
            return

        # 2) Hiçbir şey algılanmadıysa: seçimi temizle ve debounce'i sıfırla
        if not sendData.get("detected", False):
            # şıkları eski haline döndür
            self.question_page.on_camera_choice(0)
            self.projection.setActiveCell(None, None)
            # debounce değişkenlerini sıfırla
            self.last_camera_choice = None
            self.last_choice_time = 0
            return

        # 3) row/col -> şık eşleştirmesi (eskiden if if yaptığın yer)
        mapping = {
            (0, 0): 1,  # A
            (0, 1): 2,  # B
            (1, 0): 3,  # C
            (1, 1): 4,  # D
        }

        key = (sendData.get("row"), sendData.get("col"))
        if key not in mapping:
            # Geçersiz koordinat ise hiçbir şey yapma
            return

        detected_choice = mapping[key]   # 1..4
        now = time.time() * 1000         # şu anki zaman (milisaniye)

        # 4) İlk kez bu şık algılandıysa veya şık değiştiyse: beklemeye başla
        if self.last_camera_choice != detected_choice:
            # yeni şık başladı
            self.last_camera_choice = detected_choice
            self.last_choice_time = now
            # hemen cevap verme, sadece başlangıç zamanını kaydet
            return

        # 5) Aynı şık choice_confirm_delay ms'den uzun süredir görülüyorsa: artık onayla
        elapsed = now - self.last_choice_time
        if elapsed >= self.choice_confirm_delay:
            print(f"KAMERA → Şık onaylandı: {detected_choice} (geçen süre: {elapsed:.0f} ms)")
            row, col = key
            self.projection.setActiveCell(row, col)

            self.question_page.on_camera_choice(detected_choice)

            # 6) Bir daha üst üste tetiklenmesin diye debounce'i sıfırla
            self.last_camera_choice = None
            self.last_choice_time = 0

#Thread Kısmı
    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)

#Main Fonksiyonu Ana Yükleyici
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
