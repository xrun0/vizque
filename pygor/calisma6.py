import cv2
import numpy as np
import json

# === Izgara Ayarları ===
GRID_COLS = 4   # sütun sayısı
GRID_ROWS = 2   # satır sayısı


def _draw_grid(frame, cols=GRID_COLS, rows=GRID_ROWS):
    """
    Frame üzerine cols x rows (default: 4x2) ızgarayı çizer.
    Hücre genişliği (cell_w) ve yüksekliğini (cell_h) döndürür.
    """
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


def _get_cell_from_point(x, y, frame_width, frame_height,
                         cols=GRID_COLS, rows=GRID_ROWS):
    """
    Verilen (x, y) noktasının cols x rows ızgarada hangi hücreye denk geldiğini hesaplar.
    row, col, cell_id döner.
      - row: 0..rows-1
      - col: 0..cols-1
      - cell_id: 0..(rows*cols-1)
    """
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
    """
    Kameradan gelen tek bir frame'i işler:
      - 4x2 ızgara çizer
      - Basit threshold + kontur ile en büyük SİYAH cismi bulmaya çalışır
      - Merkezin düştüğü ızgara hücresini hesaplar
      - İşlenmiş görüntüde (processed_frame):
          * Merkeze KIRMIZI daire koyar
          * İlgili hücreyi YEŞİL dikdörtgenle çizer

    Dönüş:
      processed_frame: Üzerine ızgara + highlight çizilmiş frame
      data: {
          "detected": bool,
          "cx": int veya None,
          "cy": int veya None,
          "row": int veya None,
          "col": int veya None,
          "cell": int veya None
      }
    """
    processed = frame.copy()
    h, w = processed.shape[:2]

    # 1) Izgarayı çiz
    cell_w, cell_h = _draw_grid(processed)

    # 2) Siyah bölgeleri algılamak için gri + ters threshold
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Burada küçük bir eşik değeri seçtik (siyah daha koyu)
    # 0-255 arasında, 60'tan koyu olanlar "beyaz" maske olacak
    _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)

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


def send_to_app(data):
    """
    Burada veriyi asıl uygulamana göndereceksin.
    Şimdilik sadece JSON string olarak ekrana basıyoruz.
    """
    payload = json.dumps(data)
    print("Gönderilen veri:", payload)


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame okunamadı, çıkılıyor...")
            break

        # 1) Kameradan gelen ham görüntü
        raw_frame = frame.copy()

        # 2) İşlenmiş görüntü
        processed_frame, data = process_frame(frame)

        # Uygulamaya veri gönder
        send_to_app(data)

        # --- Senin istediğin 2 pencere ---
        cv2.imshow("Camera Raw", raw_frame)        # 1. pencere: ham kamera
        cv2.imshow("Processed", processed_frame)   # 2. pencere: kırmızı daire + ızgara

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC ile çık
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()