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
        self.stack.addWidget(self.start_page)     # index 0
        self.stack.addWidget(self.question_page)  # index 1
        self.stack.addWidget(self.result_page)  # index 1

        self.camera_thread = QThread(self)
        self.camera_worker = CameraWorker()
        self.camera_worker.moveToThread(self.camera_thread)
        self.camera_thread.started.connect(self.camera_worker.start)
        self.camera_worker.dataReady.connect(self.on_camera_data)
        self.camera_thread.start()
        
        

        self.questions = []
        self.duration_sec = 32
        self.current_idx = 0
        self.correct_count = 0

        self.load_questions()

        self.start_page.cardClicked.connect(self.goto_question_page)
        self.question_page.timeUp.connect(self.goto_result)
        self.result_page.goHome.connect(self.back_to_start)
        #self.result_page.goHome.connect(self.back_to_start)

        self.question_page.answerSelected.connect(self.on_answer_selected)
        #kamera test kısmı
        #self.camera_worker.frameReady.connect(self.on_debug_frame)

#Sayfalar ve İşlemleri
    def goto_question_page(self):
        print("Kart tıklandı, QuestionPage açılıyor...")
        self.stack.setCurrentWidget(self.question_page)
        self.question_page.startTimer(32)
        #self.show_current_question()

    def load_questions(self):
        base_dir = Path(__file__).resolve().parent
        qpath = base_dir / "questions" / "questions.json"
        with qpath.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self.questions = data.get("questions", [])
        self.duration_sec = int(data.get("duration_sec", 32))
        self.current_idx = 0
        self.correct_count = 0

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
        # sonraki soruya geç
        self.current_idx += 1
        if self.current_idx < len(self.questions):
            self.show_current_question()
        else:
            self.goto_result()

    def handle_next_question(self):
        self.question_page.subtitle.setText("Yeni soru yüklendi (örnek).")

    def goto_result(self):
        print("Süre bitti -> Result sayfasına geçiliyor")
        self.stack.setCurrentWidget(self.result_page)

        #self.start_page.btn_start.clicked.connect(
        #    lambda: self.stack.setCurrentIndex(1)
        #)
        #self.question_page.btn_next.clicked.connect(self.handle_next_question)

    def back_to_start(self):
        self.stack.setCurrentWidget(self.start_page)
    
#kamera ve Debug kısmı
    def on_debug_frame(self, renkli, thresed):
        cv2.imshow("DEBUG", renkli)
        cv2.imshow("DEBUG2", thresed)
        cv2.waitKey(1)

    @pyqtSlot(object)
    def on_camera_data(self, sendData: object):
        if sendData['detected'] == False:
            self.question_page.on_camera_choice(0)
        else:
            if sendData['row'] == 0 and sendData['col']==0:
                print("A Şıkkı")
                self.question_page.on_camera_choice(1)
            if sendData['row'] == 0 and sendData['col']==1:
                print("B Şıkkı")
                self.question_page.on_camera_choice(2)

            if sendData['row'] == 1 and sendData['col']==0:
                print("C Şıkkı")
                self.question_page.on_camera_choice(3)

            if sendData['row'] == 1 and sendData['col']==1:
                print("D Şıkkı")
                self.question_page.on_camera_choice(4)
            self.question_page.on_camera_choice(0)
            
#Thread Kısmı
    def closeEvent(self, event):
        """
        Pencere kapanırken thread'i düzgün kapatalım.
        """
        try:
            if self.camera_worker:
                self.camera_worker.stop()
            if self.camera_thread:
                self.camera_thread.quit()
                self.camera_thread.wait()
        except Exception as e:
            print("Kamera thread'i kapanırken hata:", e)
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
