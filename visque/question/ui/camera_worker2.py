import cv2
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

GRID_COLS = 2   # sütun sayısı
GRID_ROWS = 2   # satır sayısı

def _draw_grid(frame, cols=GRID_COLS, rows=GRID_ROWS):
    h, w = frame.shape[:2]
    cell_w = w // cols
    cell_h = h // rows

    # Dikey çizgiler (Sütunlar)
    for i in range(1, cols):
        x = i * cell_w
        cv2.line(frame, (x, 0), (x, h), (255, 255, 255), 1)

    # Yatay çizgiler (Satırlar)
    for j in range(1, rows):
        y = j * cell_h
        # DÜZELTME: Eski kodda (x, h) vardı, doğrusu (w, y) olmalı yani genişlik boyunca çizilmeli.
        cv2.line(frame, (0, y), (w, y), (255, 255, 255), 1)

    return cell_w, cell_h

def _get_cell_from_point(x, y, frame_width, frame_height, cols=GRID_COLS, rows=GRID_ROWS):
    cell_w = frame_width / cols
    cell_h = frame_height / rows

    col = int(x / cell_w)
    row = int(y / cell_h)

    # Sınır kontrolü
    col = max(0, min(cols - 1, col))
    row = max(0, min(rows - 1, row))

    cell_id = row * cols + col
    return row, col, cell_id

def process_frame(frame):
    # 1. Ön Hazırlık
    h, w = frame.shape[:2]
    # Görüntüyü biraz küçültmek işlemi hızlandırır (isteğe bağlı)
    # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5) 
    
    processed = frame.copy()
    
    # Izgarayı çiziyoruz
    cell_w, cell_h = _draw_grid(processed)

    # 2. Gürültü Azaltma (Sadece Gaussian yeterli)
    # Bilateral filter çok yavaştır, kaldırdım.
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)

    # 3. Işık Değişimine Karşı Çözüm: HSV Dönüşümü
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Siyah rengi tanımlıyoruz (HSV Uzayında)
    # H (Renk): Önemli değil (0-180)
    # S (Doygunluk): Önemli değil (0-255)
    # V (Parlaklık): EN ÖNEMLİSİ! 0-60 arası karanlık (siyah) kabul edilir.
    # Ortam çok aydınlıksa 60'ı 80 yapabilirsin.
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 60]) 

    mask = cv2.inRange(hsv, lower_black, upper_black)

    # 4. Morfolojik İşlemler (Görüntüyü temizleme)
    # Kernel: Temizleme silgisinin boyutu
    kernel = np.ones((15, 15), np.uint8)
    
    # Opening: Beyaz gürültüleri (küçük noktaları) siler
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # Closing: Nesne içindeki siyah delikleri kapatır
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Maskeyi görselleştirmek için renkliye çevir (GUI'de göstermek için)
    thresh_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # 5. Kontur Bulma
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    best_cnt = None
    max_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Çok küçük gürültüleri ve ekranı kaplayan hataları ele
        if 1000 < area < 300000:
            if area > max_area:
                max_area = area
                best_cnt = cnt

    data = {
        "detected": False,
        "cx": None, "cy": None,
        "row": None, "col": None, "cell": None
    }

    if best_cnt is not None:
        # En büyük konturu çiz
        cv2.drawContours(processed, [best_cnt], -1, (0, 255, 0), 3)

        # Ağırlık merkezi (Moment) hesapla
        M = cv2.moments(best_cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            data["detected"] = True
            data["cx"] = cx
            data["cy"] = cy
            
            # Hangi hücrede?
            row, col, cell_id = _get_cell_from_point(cx, cy, processed.shape[1], processed.shape[0])
            data["row"] = row
            data["col"] = col
            data["cell"] = cell_id

            # Görselleştirme
            cv2.circle(processed, (cx, cy), 8, (0, 0, 255), -1)
            
            # Aktif hücreyi boya
            rx1 = int(col * cell_w)
            ry1 = int(row * cell_h)
            rx2 = int(rx1 + cell_w)
            ry2 = int(ry1 + cell_h)
            cv2.rectangle(processed, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)

            text = f"Cell: {cell_id} (R:{row}, C:{col})"
            cv2.putText(processed, text, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return processed, data, thresh_color


class CameraWorker2(QObject):
    dataReady = pyqtSignal(object)
    frameReady = pyqtSignal(object, object)
    finished = pyqtSignal()

    def __init__(self, parent=None, camera_index=0):
        super().__init__(parent)
        self._running = False
        self.cap = None
        self._camera_index = camera_index

    @pyqtSlot()
    def start(self):
        self._running = True
        # cv2.CAP_DSHOW windows'ta kameranın daha hızlı açılmasını sağlar
        self.cap = cv2.VideoCapture(self._camera_index, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            # Yedek olarak normal açmayı dene
            self.cap = cv2.VideoCapture(self._camera_index)
            if not self.cap.isOpened():
                print("Kamera acilamadi")
                self.finished.emit()
                return

        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                break

            processed, sendData, thresed = process_frame(frame)
            
            self.dataReady.emit(sendData)
            self.frameReady.emit(processed, thresed)

            # 100ms uyku = 10 FPS demektir. Biraz daha akıcı olması için düşürdüm.
            # 30ms = ~30 FPS
            QThread.msleep(100)

        if self.cap:
            self.cap.release()
        
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        self._running = False