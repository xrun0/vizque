import cv2
import numpy as np

def bul_siyah_kareler(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    kareler = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1000:
            continue  # çok küçük şekilleri atla

        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)

        if len(approx) == 4 and cv2.isContourConvex(approx):
            x, y, w, h = cv2.boundingRect(approx)
            center = (x + w // 2, y + h // 2)
            kareler.append({'kontur': cnt, 'merkez': center, 'bbox': (x, y, w, h)})

    return kareler

def sırala_kareler(kareler, satir=4, sutun=2):
    # Önce kareleri Y'ye göre sırala (satır)
    kareler.sort(key=lambda k: k['merkez'][1])
    satirlar = [kareler[i * sutun:(i + 1) * sutun] for i in range(satir)]

    for row in satirlar:
        row.sort(key=lambda k: k['merkez'][0])  # Satır içindeki kareleri X'e göre sırala

    return satirlar

def bul_kirmizi_nokta(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower1 = np.array([0, 100, 100])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([160, 100, 100])
    upper2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.medianBlur(mask, 5)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        if area > 100:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy)
    return None

# Ana döngü
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    kareler = bul_siyah_kareler(frame)

    if len(kareler) == 8:
        satirlar = sırala_kareler(kareler)

        kirmizi = bul_kirmizi_nokta(frame)
        if kirmizi:
            cx, cy = kirmizi
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

            for i, row in enumerate(satirlar):
                for j, kare in enumerate(row):
                    x, y, w, h = kare['bbox']
                    if x <= cx <= x + w and y <= cy <= y + h:
                        print(f"🔴 Kırmızı nokta {i}. satır, {j}. sütun karede")
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, f"{i},{j}", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Her karenin etrafına kutu çiz
        for row in satirlar:
            for kare in row:
                x, y, w, h = kare['bbox']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)

    cv2.imshow("Kamera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
