import time
import cv2
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

GRID_COLS = 2   # sütun sayısı
GRID_ROWS = 2   # satır sayısı

def _draw_grid(frame, cols=GRID_COLS, rows=GRID_ROWS):
    h, w = frame.shape[:2]
    cell_w = w // cols
    cell_h = h // rows
    for i in range(1, cols):
        x = i * cell_w
        cv2.line(frame, (x, 0), (x, h), (255, 255, 255), 1)
    for j in range(1, rows):
        y = j * cell_h
        cv2.line(frame, (0, y), (w, y), (255, 255, 255), 1)
    return cell_w, cell_h

def _get_cell_from_point(x, y, frame_width, frame_height, cols=GRID_COLS, rows=GRID_ROWS):
    cell_w = frame_width / cols
    cell_h = frame_height / rows
    col = int(x / cell_w)
    row = int(y / cell_h)
    col = max(0, min(cols - 1, col))
    row = max(0, min(rows - 1, row))
    cell_id = row * cols + col
    return row, col, cell_id

def process_frame(frame, background_ref):
    # 1. Ön Hazırlıklar
    processed = frame.copy()
    h, w = processed.shape[:2]
    _draw_grid(processed)

    # --- AŞAMA 1: HAREKET ALGILAMA (Arka Plan Çıkarma) ---
    gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_curr = cv2.GaussianBlur(gray_curr, (21, 21), 0)
    diff = cv2.absdiff(background_ref, blurred_curr)
    # Fark eşiği (25). Ortam gürültüsüne göre artırılabilir.
    _, motion_mask = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

    # --- AŞAMA 2: PARLAKLIK ALGILAMA (HSV - Value) ---
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Parlaklık (Value) değeri 0-80 arası olanları seç.
    # Işık çok artarsa 80'i 100'e kadar çekebilirsin.
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50]) 
    dark_mask = cv2.inRange(hsv, lower_black, upper_black)

    # --- AŞAMA 3: BİRLEŞTİRME (Hem Hareketli Hem Karanlık) ---
    combined_mask = cv2.bitwise_and(motion_mask, dark_mask)

    # --- AŞAMA 4: TEMİZLİK ---
    kernel = np.ones((5, 5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

    thresh_color = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)

    contours, _ = cv2.findContours(
        combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    newcnt = None
    bigarea = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 1000 < area < 300000:
            if bigarea < area:
                newcnt = cnt
                bigarea = area

    data = { "detected": False, "cx": None, "cy": None, "row": None, "col": None, "cell": None }

    if newcnt is not None:
        cv2.drawContours(processed, [newcnt], -1, (0, 255, 0), 3)
        M = cv2.moments(newcnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            data["detected"] = True
            data["cx"] = cx
            data["cy"] = cy
            row, col, cell_id = _get_cell_from_point(cx, cy, w, h)
            data["row"] = row
            data["col"] = col
            data["cell"] = cell_id
            
            cv2.circle(processed, (cx, cy), 8, (0, 0, 255), -1)
            # Hücre vurgulama çizimi için cell boyutlarını tekrar hesapla
            cell_w = w // GRID_COLS
            cell_h = h // GRID_ROWS
            x1 = int(col * cell_w)
            y1 = int(row * cell_h)
            x2 = int(x1 + cell_w)
            y2 = int(y1 + cell_h)
            cv2.rectangle(processed, (x1, y1), (x2, y2), (0, 255, 0), 2)
            text = f"Cell: {cell_id} (R:{row}, C:{col})"
            cv2.putText(processed, text, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return processed, data, thresh_color

class CameraWorker(QObject):
    dataReady = pyqtSignal(object) 
    frameReady = pyqtSignal(object, object)
    finished = pyqtSignal()

    def __init__(self, parent=None, camera_index=0):
        super().__init__(parent)
        self._running = False
        self.cap = None
        self._camera_index = camera_index
        self.background_ref = None 
        self._reset_requested = False

    @pyqtSlot()
    def start(self):
        self._running = True
        self.cap = cv2.VideoCapture(self._camera_index, cv2.CAP_DSHOW) 
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self._camera_index)
            if not self.cap.isOpened():
                print("Kamera acilamadi")
                self.finished.emit()
                return

        baslangic_zamani = time.time()
        print("Kamera isiniyor... Lutfen bekleyin.")

        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, -1)
            # 2 Saniye Isınma Kontrolü
            gecen_sure = time.time() - baslangic_zamani
            if gecen_sure < 2.0:
                cv2.putText(frame, f"Sistem Hazirlaniyor... {2.0 - gecen_sure:.1f}sn", 
                           (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                self.frameReady.emit(frame, frame) 
                QThread.msleep(30)
                continue

            # Arka Plan Referansı Alma
            if self.background_ref is None or self._reset_requested:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.background_ref = cv2.GaussianBlur(gray, (21, 21), 0)
                self._reset_requested = False
                print("Arka plan referansi ALINDI!")
                cv2.putText(frame, "REFERANS ALINDI!", (20, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                self.frameReady.emit(frame, frame)
                QThread.msleep(30)
                continue

            # İşleme
            processed, sendData, thresed = process_frame(frame, self.background_ref)
            self.dataReady.emit(sendData)
            self.frameReady.emit(processed, thresed)
            QThread.msleep(30)

        if self.cap:
            self.cap.release()
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        self._running = False

    @pyqtSlot()
    def reset_background(self):
        self._reset_requested = True