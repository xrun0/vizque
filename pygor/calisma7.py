import cv2
import numpy as np
import json

# === Izgara Ayarları ===
GRID_COLS = 4   # sütun sayısı
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
    processed = frame.copy()
    h, w = processed.shape[:2]

    # 1) Izgarayı çiz
    cell_w, cell_h = _draw_grid(processed)

    # 2) Siyah bölgeleri algılamak için gri + ters threshold
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Burada küçük bir eşik değeri seçtik (siyah daha koyu)
    # 0-255 arasında, 60'tan koyu olanlar "beyaz" maske olacak
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)

    # Gürültüyü biraz temizlemek istersen (opsiyonel):
    # kernel = np.ones((3, 3), np.uint8)
    # thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    data = {
        "detected": False,
        "cx": None,
        "cy": None,
        "row": None,
        "col": None,
        "cell": None
    }

    if contours:
        # Çok küçük gürültüleri atmak için min alan
        min_area = 500  # ihtiyacına göre oynayabilirsin
        big_contours = [c for c in contours if cv2.contourArea(c) > min_area]

        if big_contours:
            # En büyük konturu al
            c = max(big_contours, key=cv2.contourArea)
            M = cv2.moments(c)

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
                cv2.putText(
                    processed,
                    text,
                    (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

    return processed, data

def amain2():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame okunamadı, çıkılıyor...")
            break
        
        processed_frame, data, thresh_frame = process_frame(frame)
        cv2.imshow("Processed", processed_frame)   # 2. pencere: kırmızı daire + ızgara
        cv2.imshow("thresh_frame", thresh_frame)   # 2. pencere: kırmızı daire + ızgara

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
  orjimg = cv2.imread('medya/ucuncu.png')
  height, width = orjimg.shape[:2]
  
  scale = 1
  new_width  = int(width * scale)
  new_height = int(height * scale)
  
  img = cv2.resize(orjimg, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

  processed_frame, data = process_frame(img)

  cv2.imshow("processed_frame", processed_frame)

  cv2.waitKey(0)
  cv2.destroyAllWindows()



if __name__ == "__main__":
    main()