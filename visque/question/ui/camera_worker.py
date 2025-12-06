# ui/camera_worker.py

import cv2
import numpy as np

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

GRID_COLS = 2   # sütun sayısı
GRID_ROWS = 2   # satır sayısı

def _draw_grid(frame, cols=GRID_COLS, rows=GRID_ROWS):
    h, w = frame.shape[:2]
    cell_w = w // cols
    cell_h = h // rows

    # Dikey çizgiler
    for i in range(1, cols):
        x = i * cell_w
        cv2.line(frame, (x, 0), (x, h), (255, 255, 255), 1)

    # Yatay çizgiler
    for j in range(1, rows):
        y = j * cell_h
        cv2.line(frame, (0, y), (x, h), (255, 255, 255), 1)
        y = j * cell_h
        cv2.line(frame, (0, y), (frame.shape[1], y), (255, 255, 255), 1)

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
    h, w = frame.shape[:2]

    scale = 1
    new_width  = int(w * scale)
    new_height = int(h * scale)
  
    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    #frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    processed = frame.copy()
    h, w = processed.shape[:2]

    

    # 1) Izgarayı çiz
    cell_w, cell_h = _draw_grid(processed)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (11,11), 0)
    blur2 = cv2.medianBlur(blur, 9)
    blur3 = cv2.bilateralFilter(blur2, d=9, sigmaColor=75, sigmaSpace=75)

    _, thresh = cv2.threshold(blur3, 6, 255, cv2.THRESH_BINARY_INV)

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    newcnt = None
    bigarea = 0
    thresh_color = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 6000 < area < 300000:
            if bigarea < area:
                newcnt = cnt
                bigarea = cv2.contourArea(cnt)
                cv2.drawContours(processed, [cnt], -1, (0, 255, 0), 8)
    data = {
        "detected": False,
        "cx": None,
        "cy": None,
        "row": None,
        "col": None,
        "cell": None
    }
    if newcnt is not None:
        c = max(newcnt, key=cv2.contourArea)
        M = cv2.moments(newcnt)
        if M["m00"] != 0:
          cx = int(M["m10"] / M["m00"])
          cy = int(M["m01"] / M["m00"])
          data["detected"] = True
          data["cx"] = cx
          data["cy"] = cy
          # 3) Noktanın hangi hücrede olduğunu bul
          row, col, cell_id = _get_cell_from_point(cx, cy, w, h)
          data["row"] = row
          data["col"] = col
          data["cell"] = cell_id
          # 4) Görsel highlight (tam senin istediğin)
          # Merkeze kırmızı daire
          cv2.circle(processed, (cx, cy), 8, (0, 0, 255), -1)
          # Hücreyi yeşil dikdörtgenle vurgula
          x1 = col * cell_w
          y1 = row * cell_h
          x2 = x1 + cell_w
          y2 = y1 + cell_h
          cv2.rectangle(processed, (x1, y1), (x2, y2), (0, 255, 0), 2)
          # Bilgi yazısı
          text = f"row={row}, col={col}, cell={cell_id}"
          cv2.putText(processed,text,(10, h - 10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0, 255, 0),2,)
        #c = max(newcnt, key=cv2.contourArea)
        #print("c"+c
    return processed,data,thresh_color


class CameraWorker(QObject):
    """
    Ayrı bir thread içinde çalışacak.
    Her kare için dataReady(int) sinyali ile sendData değerini gönderecek.
    (Burada imshow YOK, sadece veri üretimi var.)
    """

    dataReady = pyqtSignal(object)  # Her kare için sendData değeri
    frameReady = pyqtSignal(object,object)
    finished = pyqtSignal()

    def __init__(self, parent=None, camera_index=0):
        super().__init__(parent)
        self._running = False
        self.cap = None
        self._camera_index = camera_index

    @pyqtSlot()
    def start(self):
        """
        Thread çalışmaya başladığında çalışacak ana döngü.
        """
        self._running = True
        self.cap = cv2.VideoCapture(self._camera_index)

        if not self.cap.isOpened():
            print("Kamera acilamadi")
            return

        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                break

            processed,sendData,thresed = process_frame(frame)
            # Uygulamaya sinyal gönder
            #print(sendData)
            self.dataReady.emit(sendData)
            self.frameReady.emit(processed,thresed)

            # Çok hızlı gitmesin, CPU'yu yakmasın:
            QThread.msleep(100)

        if self.cap:
            self.cap.release()
            self.cap = None

        cv2.destroyAllWindows()   # OpenCV pencereleri varsa kapat
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        """
        Döngüyü durdurmak için.
        """
        self._running = False
